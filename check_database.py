from database.database import SessionLocal
from database.models import User, Advertisement, UserInteraction


def check_database():
    db = SessionLocal()

    try:
        print("📊 数据库内容检查:")
        print("\n👥 用户:")
        users = db.query(User).all()
        for user in users:
            print(f"  - {user.user_id}: {user.age}岁, {user.gender}, 兴趣: {user.interests}")

        print("\n📢 广告:")
        ads = db.query(Advertisement).all()
        for ad in ads:
            print(f"  - {ad.ad_id}: {ad.title} (${ad.bid_price})")

        print("\n🔄 交互记录:")
        interactions = db.query(UserInteraction).all()
        for interaction in interactions:
            print(f"  - {interaction.user_id} -> {interaction.ad_id} -> {interaction.action}")

        print(f"\n✅ 总计: {len(users)} 用户, {len(ads)} 广告, {len(interactions)} 交互")

    finally:
        db.close()


if __name__ == "__main__":
    check_database()