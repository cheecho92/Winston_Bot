from dataclasses import dataclass

'''
datalcasses essentially just group variables and allow you to call them elsewhere using 
config.value
'''

@dataclass
class Config:
    name: str
    client_id: str
    client_secret: str
    auth_uri: str
    token_uri: str
    scopes: list
    api_uri: str
    browser: str
    channel: str | None = None
    channel_name: str | None = None
    bot: str | None = None
    token_file: str | None = None
    host: str = "localhost"
    port: int = 3000
    discord: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    redirect_uri: str = "http://localhost:3000"
    content_type: dict | None = None
    headers: dict | None = None