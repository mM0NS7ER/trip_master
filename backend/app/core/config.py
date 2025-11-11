from decouple import config
from typing import Optional

class Settings:
    # Supabase配置
    SUPABASE_URL: str = config("SUPABASE_URL", default="")
    SUPABASE_KEY: str = config("SUPABASE_ANON_KEY", default="")
    SUPABASE_SERVICE_KEY: str = config("SUPABASE_SERVICE_ROLE_KEY", default="")
    
    # 数据库配置 (使用Supabase PostgreSQL)
    DATABASE_URL: str = config("DATABASE_URL", default="")

    # JWT配置
    SECRET_KEY: str = config("SECRET_KEY", default="your-secret-key-here")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    # 令牌自动续期阈值（分钟），当令牌剩余时间少于这个值时，会自动续期
    TOKEN_REFRESH_THRESHOLD_MINUTES: int = config("TOKEN_REFRESH_THRESHOLD_MINUTES", default=5, cast=int)

    # 应用配置
    DEBUG: bool = config("DEBUG", default=True, cast=bool)

    # 项目信息
    PROJECT_NAME: str = "Trip Master API"
    API_V1_STR: str = "/api"

    # AI服务配置
    AI_MODEL: str = config("AI_MODEL", default="glm-4")
    AI_API_KEY: str = config("AI_API_KEY", default="")
    SYSTEM_PROMPT: str = config("SYSTEM_PROMPT", default="你是一个旅行规划师，帮助用户制定个性化的旅行计划。")
    
    
    # 科大讯飞语音识别API配置
    XUNFEI_APP_ID: str = config("XUNFEI_APP_ID", default="")
    XUNFEI_API_KEY: str = config("XUNFEI_API_KEY", default="")
    XUNFEI_API_SECRET: str = config("XUNFEI_API_SECRET", default="")

settings = Settings()
