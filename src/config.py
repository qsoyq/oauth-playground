from pydantic_settings import BaseSettings, SettingsConfigDict


class OauthAppConfig(BaseSettings):
    github_client_id: str = ""
    github_secret: str = ""
    github_redirect_uri: str = ""

    model_config = SettingsConfigDict(env_file=".env")
