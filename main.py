# 修改 main.py 开头的导入部分
from data_processor import DataProcessor
from models import RecommendationModel, UserEmbeddingModel
from data import FeatureEngineer   # 移除 data. 前缀
from typing import List, Dict, Any
from database.database import SessionLocal, init_database


class PersonalizedAdRecommendation:
    def __init__(self, db_session=None):
        print("🔧 初始化 PersonalizedAdRecommendation...")
        self.db_session = db_session

        # 先创建 DataProcessor 实例
        print("📦 创建 DataProcessor...")
        self.data_processor = DataProcessor(db_session)

        # 然后创建其他组件
        self.recommendation_model = RecommendationModel()
        self.user_embedding_model = UserEmbeddingModel()
        self.feature_engineer = FeatureEngineer()

        print("✅ PersonalizedAdRecommendation 初始化完成")

    def initialize(self):
        """初始化系统"""
        print("🚀 初始化个性化广告推荐系统...")

        # 检查数据
        if not self.data_processor.user_profiles:
            print("📝 数据为空，创建示例数据...")
            self.create_sample_data_in_db()
            # 重新加载数据
            self.data_processor.load_data_from_db()

        # 训练模型
        self.train_models()

        print("✅ 系统初始化完成")

    def create_sample_data_in_db(self):
        """在数据库中创建示例数据"""
        if not self.db_session:
            print("⚠️ 无数据库会话，跳过创建示例数据")
            return

        try:
            from database.models import User, Advertisement, UserInteraction
            from datetime import datetime

            print("📝 在数据库中创建示例数据...")

            # 检查是否已存在数据
            existing_users = self.db_session.query(User).count()
            if existing_users > 0:
                print("✅ 数据库中已有数据，跳过创建")
                return

            # 创建示例用户
            users = [
                User(user_id="user_1", age=25, gender="male", interests=["technology", "sports"], location="Beijing",
                     device="mobile"),
                User(user_id="user_2", age=30, gender="female", interests=["fashion", "beauty"], location="Shanghai",
                     device="desktop"),
                User(user_id="user_3", age=35, gender="male", interests=["business", "travel"], location="Shenzhen",
                     device="tablet"),
            ]

            # 创建示例广告
            advertisements = [
                Advertisement(ad_id="ad_1", title="最新智能手机", category="electronics",
                              keywords=["technology", "mobile"], target_age_min=18, target_age_max=35,
                              target_gender="all", bid_price=2.5),
                Advertisement(ad_id="ad_2", title="时尚女装", category="clothing", keywords=["fashion", "beauty"],
                              target_age_min=20, target_age_max=40, target_gender="female", bid_price=1.8),
                Advertisement(ad_id="ad_3", title="旅游套餐", category="travel", keywords=["travel", "vacation"],
                              target_age_min=25, target_age_max=50, target_gender="all", bid_price=3.2),
            ]

            # 添加到数据库
            for user in users:
                self.db_session.add(user)
            for ad in advertisements:
                self.db_session.add(ad)

            self.db_session.commit()
            print("✅ 示例数据创建成功")

        except Exception as e:
            print(f"❌ 创建示例数据失败: {e}")
            self.db_session.rollback()

    def train_models(self):
        """训练所有模型"""
        print("=== 开始训练个性化广告推荐模型 ===")

        # 训练传统推荐模型
        self.recommendation_model.train(self.data_processor)

        # 如果训练数据太少，生成一些模拟数据
        if len(self.data_processor.interaction_history) < 10:
            print("📝 训练数据不足，生成模拟交互数据...")
            self._generate_simulated_interactions()

        # 训练嵌入模型
        for interaction in self.data_processor.interaction_history:
            self.user_embedding_model.update_user_embedding(
                interaction['user_id'],
                interaction['ad_id'],
                interaction['action']
            )

        print("=== 模型训练完成 ===\n")

    def _generate_simulated_interactions(self):
        """生成模拟交互数据以丰富训练集"""
        simulated_interactions = []

        # 模拟一些点击行为
        user_ad_pairs = [
            ("user_1", "ad_1", "click"),
            ("user_1", "ad_3", "view"),
            ("user_2", "ad_2", "click"),
            ("user_2", "ad_1", "view"),
            ("user_3", "ad_3", "click"),
            ("user_3", "ad_2", "view"),
            ("user_1", "ad_4", "click"),
            ("user_2", "ad_4", "view"),
            ("user_3", "ad_1", "view"),
        ]

        from datetime import datetime, timedelta
        base_time = datetime.now()

        for i, (user_id, ad_id, action) in enumerate(user_ad_pairs):
            # 确保用户和广告存在
            if (user_id in self.data_processor.user_profiles and
                    ad_id in self.data_processor.ad_inventory):
                interaction_time = base_time - timedelta(hours=i)
                simulated_interactions.append({
                    "user_id": user_id,
                    "ad_id": ad_id,
                    "action": action,
                    "timestamp": interaction_time.isoformat()
                })

        # 添加到交互历史
        self.data_processor.interaction_history.extend(simulated_interactions)
        print(f"✅ 生成 {len(simulated_interactions)} 条模拟交互数据")

    def get_recommendations(self, user_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """为用户获取广告推荐"""
        print(f"为用户 {user_id} 生成推荐...")

        if user_id not in self.data_processor.user_profiles:
            return [{"error": f"用户 {user_id} 不存在"}]

        recommendations = []
        user_feature = self.data_processor.create_user_features(user_id)

        for ad_id in self.data_processor.ad_inventory.keys():
            ad_feature = self.data_processor.create_ad_features(ad_id)

            click_probability = self.recommendation_model.predict_click_probability(user_feature, ad_feature)
            similarity = self.feature_engineer.calculate_similarity(user_feature, ad_feature)
            combined_score = click_probability * similarity

            recommendations.append({
                'ad_id': ad_id,
                'ad_info': self.data_processor.ad_inventory[ad_id],
                'click_probability': float(click_probability),
                'similarity': float(similarity),
                'combined_score': float(combined_score),
                'from_collaborative_filtering': False  # 简化版本
            })

        recommendations.sort(key=lambda x: x['combined_score'], reverse=True)
        return recommendations[:top_k]

    def record_user_interaction(self, user_id: str, ad_id: str, action: str):
        """记录用户交互"""
        print(f"记录交互: 用户 {user_id} -> 广告 {ad_id} -> 行为 {action}")
        self.data_processor.save_interaction_to_db(user_id, ad_id, action)

    def display_recommendations(self, user_id: str):
        """显示推荐结果"""
        recommendations = self.get_recommendations(user_id)

        print(f"\n=== 为用户 {user_id} 的个性化广告推荐 ===")
        for i, rec in enumerate(recommendations, 1):
            if 'error' in rec:
                print(f"错误: {rec['error']}")
                continue

            print(f"{i}. 广告: {rec['ad_info']['title']}")
            print(f"   类别: {rec['ad_info']['category']}")
            print(f"   点击概率: {rec['click_probability']:.4f}")
            print(f"   相似度: {rec['similarity']:.4f}")
            print(f"   综合评分: {rec['combined_score']:.4f}")
            print()


def main():
    try:
        # 初始化数据库
        init_database()

        # 创建数据库会话
        db = SessionLocal()

        try:
            # 创建推荐系统实例
            print("🔧 创建推荐系统实例...")
            ad_system = PersonalizedAdRecommendation(db)

            # 初始化系统
            ad_system.initialize()

            # 为不同用户生成推荐
            test_users = list(ad_system.data_processor.user_profiles.keys())[:3]
            print(f"👥 测试用户: {test_users}")

            for user_id in test_users:
                ad_system.display_recommendations(user_id)

        except Exception as e:
            print(f"❌ 系统运行错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()

    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()