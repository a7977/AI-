import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os


class SimpleFeatureEngineer:
    """简化的特征工程类"""

    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit(self, features):
        """拟合特征标准化器"""
        if len(features) > 0:
            self.scaler.fit(features)
            self.is_fitted = True

    def calculate_similarity(self, user_feature, ad_feature):
        """计算用户和广告的相似度"""
        if len(user_feature) == 0 or len(ad_feature) == 0:
            return 0.0

        # 确保特征维度一致
        min_dim = min(len(user_feature), len(ad_feature))
        user_feature = user_feature[:min_dim]
        ad_feature = ad_feature[:min_dim]

        # 如果已经拟合，进行标准化
        if self.is_fitted:
            try:
                user_feature = self.scaler.transform(user_feature.reshape(1, -1)).flatten()
                ad_feature = self.scaler.transform(ad_feature.reshape(1, -1)).flatten()
            except:
                pass  # 如果标准化失败，使用原始特征

        similarity = cosine_similarity(
            user_feature.reshape(1, -1),
            ad_feature.reshape(1, -1)
        )[0][0]

        return float(similarity)


class RecommendationModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.feature_engineer = SimpleFeatureEngineer()
        self.is_trained = False
        self.combined_feature_dim = 16  # 用户8维 + 广告8维

    def prepare_training_data(self, data_processor):
        """准备训练数据"""
        X = []
        y = []

        # 收集所有特征用于标准化
        all_features = []

        # 收集用户特征
        for user_id in data_processor.user_profiles.keys():
            user_feature = data_processor.create_user_features(user_id)
            all_features.append(user_feature)

        # 收集广告特征
        for ad_id in data_processor.ad_inventory.keys():
            ad_feature = data_processor.create_ad_features(ad_id)
            all_features.append(ad_feature)

        # 转换为numpy数组
        if all_features:
            all_features = np.array(all_features)
            # 拟合特征工程
            self.feature_engineer.fit(all_features)

        # 准备训练样本
        for interaction in data_processor.interaction_history:
            user_id = interaction["user_id"]
            ad_id = interaction["ad_id"]
            action = interaction["action"]

            user_feature = data_processor.create_user_features(user_id)
            ad_feature = data_processor.create_ad_features(ad_id)

            # 合并特征 - 现在维度一致了
            combined_feature = np.concatenate([user_feature, ad_feature])
            X.append(combined_feature)

            # 标签：点击为1，其他为0
            label = 1 if action == "click" else 0
            y.append(label)

        return np.array(X) if X else np.array([]), np.array(y) if y else np.array([])

    def train(self, data_processor):
        """训练模型"""
        print("开始训练推荐模型...")

        X, y = self.prepare_training_data(data_processor)

        if len(X) == 0:
            print("警告：没有训练数据，创建虚拟数据训练模型")
            # 创建虚拟数据 - 使用正确的维度
            X = np.random.rand(20, self.combined_feature_dim)
            y = np.random.randint(0, 2, 20)
            self.model.fit(X, y)
            print("使用虚拟数据完成模型训练")
        else:
            print(f"训练数据形状: X={X.shape}, y={y.shape}")
            self.model.fit(X, y)
            accuracy = self.model.score(X, y)
            print(f"模型训练完成，训练集准确率: {accuracy:.4f}")

        self.is_trained = True

    def predict_click_probability(self, user_feature, ad_feature):
        """预测点击概率"""
        if not self.is_trained:
            return 0.5

        if len(user_feature) == 0 or len(ad_feature) == 0:
            return 0.5

        # 合并特征
        combined_feature = np.concatenate([user_feature, ad_feature])

        try:
            probability = self.model.predict_proba(combined_feature.reshape(1, -1))[0][1]
            return probability
        except Exception as e:
            print(f"预测错误: {e}")
            return 0.5

    def save_model(self, filepath: str):
        """保存模型"""
        if self.is_trained:
            joblib.dump(self.model, filepath)
            print(f"模型已保存到: {filepath}")

    def load_model(self, filepath: str):
        """加载模型"""
        if os.path.exists(filepath):
            self.model = joblib.load(filepath)
            self.is_trained = True
            print(f"模型已从 {filepath} 加载")