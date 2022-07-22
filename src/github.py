from __future__ import annotations

import logging
import urllib.parse

from typing import Any, Dict

import httpx

from fastapi import APIRouter, Body, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr, HttpUrl

from config import OauthAppConfig


class GithubErrorRes(BaseModel):
    error: str | None
    error_description: str | None
    error_uri: str | None


default_responses = {500: {"model": GithubErrorRes}}
router = APIRouter(prefix='/github', responses=default_responses)  # type: ignore


class GithubException(Exception):

    def __init__(self, error: GithubErrorRes):
        super().__init__()
        self.error = error


def exception_handler(_: Request, exc: GithubException):
    return JSONResponse(exc.error.dict(), status_code=500)


def is_github_error(data: Dict[Any, Any]):
    if data.get('error'):
        raise GithubException(GithubErrorRes(**data))


class GithubUser(BaseModel):
    username: str = Body(..., description="用户登录名")
    userid: int = Body(..., description="用户ID")
    email: EmailStr | None = Body(None, description="用户邮箱地址")
    avatar_url: HttpUrl | None = Body(None, description="用户头像地址")
    type: str | None = Body(None, description="用户类型")


def make_github_user(data: dict) -> GithubUser:
    try:
        body = {
            "username": data['login'],
            "userid": data['id'],
            "email": data.get("email"),
            "avatar_url": data.get('avatar_url'),
            "type": data.get("type"),
        }
        return GithubUser(**body)
    except KeyError as e:
        logging.warning(f"bad key: {e}\n{data}")
        raise e


async def get_access_token_by_code(code: str) -> str:
    assert OauthAppConfig().github_client_id and OauthAppConfig().github_secret
    cli = httpx.AsyncClient(headers={"Accept": "application/json"})
    access_token_url = 'https://github.com/login/oauth/access_token'
    res = await cli.post(
        access_token_url,
        json={
            "client_id": OauthAppConfig().github_client_id,
            "client_secret": OauthAppConfig().github_secret,
            "code": code,
        }
    )
    if res.status_code != 200:
        logging.warning(f"{res.text}")

    is_github_error(res.json())

    access_token = res.json().get("access_token")
    if not access_token:
        logging.warning(f'{res.json()}')
    assert isinstance(access_token, str)
    return access_token


async def get_user(access_token: str) -> dict:
    cli = httpx.AsyncClient(headers={"Accept": "application/json"})
    user_url = 'https://api.github.com/user'
    headers = {"Authorization": f"token {access_token}"}
    res = await cli.get(user_url, headers=headers)
    if res.status_code != 200:
        logging.warning(f"{res.text}")

    is_github_error(res.json())

    return dict(res.json())


@router.get("/")
async def github():
    """\f
    https://docs.github.com/cn/developers/apps/building-oauth-apps/authorizing-oauth-apps
    """
    assert OauthAppConfig().github_client_id and OauthAppConfig().github_secret
    authorize_url = "https://github.com/login/oauth/authorize"
    params = {
        "client_id": OauthAppConfig().github_client_id,
        "redirect_uri": OauthAppConfig().github_redirect_uri,
        "scope": "user:email"
    }
    redirect_url = f"{authorize_url}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(redirect_url)


@router.get("/callback", response_model=GithubUser)
async def github_callback(code: str = Query(...)):
    access_token = await get_access_token_by_code(code)
    user = await get_user(access_token)
    github_user = make_github_user(user)
    logging.info(f"user {github_user.username} login success.")
    return github_user
