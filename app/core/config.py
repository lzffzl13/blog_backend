from pydantic_settings import BaseSettings, SettingsConfigDict


# 配置类，用于加载环境变量并提供应用配置项
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# 创建全局配置实例，供其他模块导入使用
settings = Settings()
