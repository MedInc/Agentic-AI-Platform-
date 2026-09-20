from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    sap_base_url: str = "https://your-s4-host.example.com"
    sap_username: str = ""
    sap_password: str = ""
    sap_auth_mode: str = "basic"
    use_mock_sap: bool = True
    approval_threshold_usd: float = 50000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
