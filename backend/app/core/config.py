from decouple import config
from typing import Optional

class Settings:
    # 数据库配置
    DATABASE_URL: str = config("DATABASE_URL", default="postgresql://user:password@localhost/trip_master")

    # JWT配置
    SECRET_KEY: str = config("SECRET_KEY", default="your-secret-key-here")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)

    # 应用配置
    DEBUG: bool = config("DEBUG", default=True, cast=bool)

    # 项目信息
    PROJECT_NAME: str = "Trip Master API"
    API_V1_STR: str = "/api"

settings = Settings()
