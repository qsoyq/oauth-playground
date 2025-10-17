import logging
import os

import typer
import uvicorn

from fastapi import FastAPI

from github import (
    GithubException,
    exception_handler as github_exception_handler,
    router as github_router,
)

cmd = typer.Typer()
app = FastAPI(prefix=os.getenv("api_prefix", "/oauth-playground"))

app.add_exception_handler(GithubException, github_exception_handler)  # type: ignore
app.include_router(github_router, tags=["oauth-github-playground"])


@cmd.command()
def http(
    host: str = typer.Option("0.0.0.0", "--host", "-h", envvar="http_host"),
    port: int = typer.Option(8000, "--port", "-p", envvar="http_port"),
    reload: bool = typer.Option(False, "--reload", envvar="http_reload"),
    log_level: int = typer.Option(logging.DEBUG, "--log_level", envvar="log_level"),
):
    """启动 http 服务"""
    logging.basicConfig(level=log_level)
    logging.info(f"http server listening on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    cmd()
