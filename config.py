import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    # 数据库配置
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")  # mysql 或 sqlite

    # MySQL配置
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "ad_recommendation")

    # 构建数据库URL
    if DB_TYPE == "sqlite":
        DATABASE_URL = "sqlite:///./ad_recommendation.db"
        ENGINE_KWARGS = {"connect_args": {"check_same_thread": False}}
    else:
        DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        ENGINE_KWARGS = {"pool_pre_ping": True, "pool_recycle": 300}

    # 模型参数
    EMBEDDING_SIZE = 128
    BATCH_SIZE = 32
    LEARNING_RATE = 0.001

    # 推荐参数
    TOP_K_RECOMMENDATIONS = 10
    SIMILARITY_THRESHOLD = 0.7

    # 广告类别
    AD_CATEGORIES = [
        "electronics", "clothing", "food", "travel",
        "education", "entertainment", "sports", "beauty"
    ]


def get_connection_info():
    """获取连接信息（隐藏密码）"""
    if Config.DB_TYPE == "sqlite":
        return Config.DATABASE_URL
    else:
        return f"mysql+pymysql://{Config.MYSQL_USER}:***@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DB}"