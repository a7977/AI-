from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from config import Config, get_connection_info

# 创建引擎
try:
    engine = create_engine(
        Config.DATABASE_URL,
        **Config.ENGINE_KWARGS,
        echo=True  # 显示SQL语句，便于调试
    )
    print(f"✅ 数据库引擎创建成功 - 使用 {Config.DB_TYPE}")
except Exception as e:
    print(f"❌ 创建数据库引擎失败: {e}")
    # 如果失败，回退到SQLite
    Config.DATABASE_URL = "sqlite:///./ad_recommendation.db"
    Config.ENGINE_KWARGS = {"connect_args": {"check_same_thread": False}}
    engine = create_engine(Config.DATABASE_URL, **Config.ENGINE_KWARGS, echo=True)
    print("✅ 已回退到SQLite数据库")

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """获取数据库会话 - 生成器函数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """创建所有表"""
    try:
        Base.metadata.create_all(bind=engine)
        print(f"✅ 数据库表创建成功")
    except Exception as e:
        print(f"❌ 创建表失败: {e}")
        raise

def init_database():
    """初始化数据库"""
    print(f"🚀 初始化数据库连接...")
    print(f"📊 数据库类型: {Config.DB_TYPE}")
    print(f"🔗 连接URL: {get_connection_info()}")

    create_tables()
    print("✅ 数据库初始化完成")