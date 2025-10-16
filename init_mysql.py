import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def init_mysql_database():
    """初始化MySQL数据库"""
    try:
        # 获取配置
        host = os.getenv("MYSQL_HOST", "localhost")
        port = int(os.getenv("MYSQL_PORT", "3306"))
        user = os.getenv("MYSQL_USER", "root")
        password = os.getenv("MYSQL_PASSWORD", "")
        db_name = os.getenv("MYSQL_DB", "ad_recommendation")

        print(f"🔧 初始化MySQL数据库 '{db_name}'...")

        # 连接MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4'
        )

        with connection.cursor() as cursor:
            # 创建数据库（如果不存在）
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ 数据库 '{db_name}' 创建成功或已存在")

        connection.close()
        return True

    except pymysql.err.OperationalError as e:
        print(f"❌ MySQL连接失败: {e}")
        print("\n💡 请检查：")
        print("1. MySQL服务是否正在运行")
        print("2. MySQL用户名和密码是否正确")
        print("3. 网络连接是否正常")
        return False
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False


if __name__ == "__main__":
    init_mysql_database()