from fastapi import FastAPI, HTTPException, Depends
from main import PersonalizedAdRecommendation
from database.database import SessionLocal, init_database
from sqlalchemy.orm import Session
import uvicorn
from typing import List, Dict, Any
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="个性化广告推荐API",
    version="2.0.0",
    description="基于机器学习的个性化广告推荐系统",
    docs_url="/docs",
    redoc_url="/redoc"
)


# 全局变量存储推荐系统实例
ad_system = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global ad_system
    try:
        print("🚀 启动个性化广告推荐API服务器...")

        # 初始化数据库
        try:
            init_database()
            print("✅ 数据库初始化成功")
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            # 继续尝试，可能数据库已存在

        # 创建数据库会话
        try:
            db = SessionLocal()
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            raise

        # 创建推荐系统实例
        try:
            ad_system = PersonalizedAdRecommendation(db)
            print("✅ 推荐系统实例创建成功")
        except Exception as e:
            print(f"❌ 推荐系统创建失败: {e}")
            db.close()
            raise

        # 初始化系统
        try:
            ad_system.initialize()
            print("✅ 系统初始化成功")
        except Exception as e:
            print(f"❌ 系统初始化失败: {e}")
            db.close()
            raise

        print("📊 系统信息:")
        print(f"   - 用户数量: {len(ad_system.data_processor.user_profiles)}")
        print(f"   - 广告数量: {len(ad_system.data_processor.ad_inventory)}")
        print(f"   - 交互记录: {len(ad_system.data_processor.interaction_history)}")

    except Exception as e:
        print(f"❌ 系统启动失败: {e}")
        import traceback
        traceback.print_exc()
        # 不要重新抛出异常，让服务器继续运行
        ad_system = None

    yield

    # Shutdown
    if ad_system and ad_system.db_session:
        ad_system.db_session.close()
        print("✅ 数据库连接已关闭")


app = FastAPI(
    title="个性化广告推荐API",
    version="2.0.0",
    description="基于机器学习的个性化广告推荐系统",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan  # 使用新的 lifespan 处理器
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 前端开发服务器
        "http://127.0.0.1:3000",  # 前端开发服务器（备用）
        "http://localhost:8080",  # 其他可能的端口
        "http://127.0.0.1:8080",  # 其他可能的端口
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法：GET, POST, PUT, DELETE 等
    allow_headers=["*"],  # 允许所有头部
)

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "个性化广告推荐系统API v2.0",
        "version": "2.0.0",
        "status": "运行中",
        "features": ["MySQL数据库支持", "个性化推荐", "实时交互记录"]
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    status = "healthy" if ad_system is not None else "degraded"
    return {
        "status": status,
        "database": "connected",
        "model_loaded": ad_system is not None,
        "message": "系统运行中" if ad_system else "系统初始化中"
    }


@app.get("/recommend/{user_id}")
async def recommend_ads(user_id: str, top_k: int = 5):
    """为用户推荐广告"""
    if ad_system is None:
        raise HTTPException(status_code=503, detail="推荐系统未初始化")

    try:
        recommendations = ad_system.get_recommendations(user_id, top_k)
        return {
            "status": "success",
            "user_id": user_id,
            "top_k": top_k,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推荐失败: {str(e)}")


@app.post("/interaction/{user_id}/{ad_id}/{action}")
async def record_interaction(user_id: str, ad_id: str, action: str):
    """记录用户与广告的交互行为"""
    if ad_system is None:
        raise HTTPException(status_code=503, detail="推荐系统未初始化")

    try:
        valid_actions = ["click", "view", "purchase", "ignore"]
        if action not in valid_actions:
            raise HTTPException(status_code=400, detail=f"无效的action参数，可选值: {valid_actions}")

        ad_system.record_user_interaction(user_id, ad_id, action)
        return {
            "status": "success",
            "message": "交互记录成功",
            "data": {
                "user_id": user_id,
                "ad_id": ad_id,
                "action": action
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"记录交互失败: {str(e)}")


@app.get("/users")
async def get_users():
    """获取所有用户列表"""
    if ad_system is None:
        raise HTTPException(status_code=503, detail="推荐系统未初始化")

    try:
        users = list(ad_system.data_processor.user_profiles.keys())
        return {
            "status": "success",
            "users": users,
            "count": len(users)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")


@app.get("/ads")
async def get_ads():
    """获取所有广告列表"""
    if ad_system is None:
        raise HTTPException(status_code=503, detail="推荐系统未初始化")

    try:
        ads = []
        for ad_id, ad_info in ad_system.data_processor.ad_inventory.items():
            ads.append({
                "ad_id": ad_id,
                "title": ad_info["title"],
                "category": ad_info["category"],
                "bid_price": ad_info["bid_price"]
            })
        return {
            "status": "success",
            "ads": ads,
            "count": len(ads)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取广告列表失败: {str(e)}")


@app.get("/user/{user_id}/profile")
async def get_user_profile(user_id: str):
    """获取用户画像"""
    if ad_system is None:
        raise HTTPException(status_code=503, detail="推荐系统未初始化")

    try:
        if user_id not in ad_system.data_processor.user_profiles:
            raise HTTPException(status_code=404, detail="用户不存在")

        profile = ad_system.data_processor.user_profiles[user_id]
        return {
            "status": "success",
            "user_id": user_id,
            "profile": profile
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户画像失败: {str(e)}")


@app.post("/user")
async def create_user(user_data: Dict):
    """创建新用户"""
    if ad_system is None:
        raise HTTPException(status_code=503, detail="推荐系统未初始化")

    try:
        # 这里可以添加创建用户的逻辑
        # 暂时返回成功消息
        return {
            "status": "success",
            "message": "用户创建功能待实现",
            "user_data": user_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")


@app.post("/ad")
async def create_advertisement(ad_data: Dict):
    """创建新广告"""
    if ad_system is None:
        raise HTTPException(status_code=503, detail="推荐系统未初始化")

    try:
        # 这里可以添加创建广告的逻辑
        # 暂时返回成功消息
        return {
            "status": "success",
            "message": "广告创建功能待实现",
            "ad_data": ad_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建广告失败: {str(e)}")


if __name__ == "__main__":
    print("🌐 启动API服务器...")
    print("📚 API文档地址: http://localhost:8000/docs")
    print("📚 ReDoc文档地址: http://localhost:8000/redoc")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )