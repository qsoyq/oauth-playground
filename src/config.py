from pydantic import BaseSettings


class OauthAppConfig(BaseSettings):
    github_client_id: str = ""
    github_secret: str = ""
    github_redirect_uri: str = ''
