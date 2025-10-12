from pydantic_settings import BaseSettings, SettingsConfigDict


class S3Config(BaseSettings):
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_SERVER_URL: str
    S3_ENDPOINT: str
    BUCKET_NAME: str

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra='ignore'
    )


s3_config = S3Config()