from database.database import init_database, SessionLocal
from database.models import User, Advertisement, UserInteraction
from datetime import datetime


def create_sample_data():
    """创建示例数据"""
    db = SessionLocal()

    try:
        print("📝 创建示例数据...")

        # 清空现有数据（可选，根据需求决定）
        # db.query(UserInteraction).delete()
        # db.query(Advertisement).delete()
        # db.query(User).delete()

        # 创建示例用户 - 使用更智能的插入方式
        users = [
            User(
                user_id="user_1",
                age=25,
                gender="male",
                interests=["technology", "sports", "gaming"],
                location="Beijing",
                device="mobile"
            ),
            User(
                user_id="user_2",
                age=30,
                gender="female",
                interests=["fashion", "beauty", "travel"],
                location="Shanghai",
                device="desktop"
            ),
            User(
                user_id="user_3",
                age=35,
                gender="male",
                interests=["business", "finance", "travel"],
                location="Shenzhen",
                device="tablet"
            )
        ]

        # 创建示例广告
        advertisements = [
            Advertisement(
                ad_id="ad_1",
                title="最新智能手机",
                category="electronics",
                keywords=["technology", "mobile", "innovation"],
                target_age_min=18,
                target_age_max=35,
                target_gender="all",
                bid_price=2.5,
                image_url="https://example.com/phone.jpg",
                landing_page="https://example.com/phone"
            ),
            Advertisement(
                ad_id="ad_2",
                title="时尚女装",
                category="clothing",
                keywords=["fashion", "beauty", "style"],
                target_age_min=20,
                target_age_max=40,
                target_gender="female",
                bid_price=1.8,
                image_url="https://example.com/fashion.jpg",
                landing_page="https://example.com/fashion"
            ),
            Advertisement(
                ad_id="ad_3",
                title="旅游套餐",
                category="travel",
                keywords=["travel", "vacation", "adventure"],
                target_age_min=25,
                target_age_max=50,
                target_gender="all",
                bid_price=3.2,
                image_url="https://example.com/travel.jpg",
                landing_page="https://example.com/travel"
            ),
            Advertisement(
                ad_id="ad_4",
                title="游戏设备",
                category="electronics",
                keywords=["gaming", "entertainment", "technology"],
                target_age_min=15,
                target_age_max=30,
                target_gender="male",
                bid_price=2.0,
                image_url="https://example.com/gaming.jpg",
                landing_page="https://example.com/gaming"
            )
        ]

        # 使用更安全的插入方式
        for user in users:
            # 检查是否已存在
            existing_user = db.query(User).filter(User.user_id == user.user_id).first()
            if not existing_user:
                db.add(user)
            else:
                print(f"⚠️ 用户 {user.user_id} 已存在，跳过")

        for ad in advertisements:
            # 检查是否已存在
            existing_ad = db.query(Advertisement).filter(Advertisement.ad_id == ad.ad_id).first()
            if not existing_ad:
                db.add(ad)
            else:
                print(f"⚠️ 广告 {ad.ad_id} 已存在，跳过")

        db.commit()
        print("✅ 示例数据创建成功")

    except Exception as e:
        print(f"❌ 创建示例数据失败: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    # 初始化数据库
    init_database()

    # 创建示例数据
    create_sample_data()

    print("🎉 数据库初始化完成！")