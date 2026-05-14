from pydantic_settings import BaseSettings

# 配置类，用于加载环境变量并提供应用配置项
class Settings(BaseSettings):
    # 数据库连接 URL，从环境变量中读取
    DATABASE_URL: str
    # 用于 JWT 等安全功能的密钥，从环境变量中读取
    SECRET_KEY: str
    # 访问令牌的过期时间（分钟），默认为 30 分钟
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        # 指定环境变量文件路径
        env_file = ".env"
        # 指定环境变量文件的编码格式
        env_file_encoding = "utf-8"

# 创建全局配置实例，供其他模块导入使用
settings = Settings()