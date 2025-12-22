from pydantic_settings import BaseSettings, SettingsConfigDict


class EmailConfig(BaseSettings):
    STMP_EMAIL_ADDRESS: str
    STMP_PASSWORD: str
    SMTP_SERVER: str
    SMTP_PORT: int = 465
    SMTP_CALLBACK: str

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra='ignore'
    )


email_config = EmailConfig()
