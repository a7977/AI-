import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity


class FeatureEngineer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit(self, user_features: np.ndarray, ad_features: np.ndarray):
        """拟合特征标准化器"""
        all_features = np.vstack([user_features, ad_features])
        self.scaler.fit(all_features)
        self.is_fitted = True

    def transform_user_features(self, user_features: np.ndarray) -> np.ndarray:
        """转换用户特征"""
        if self.is_fitted:
            return self.scaler.transform(user_features.reshape(1, -1)).flatten()
        return user_features

    def transform_ad_features(self, ad_features: np.ndarray) -> np.ndarray:
        """转换广告特征"""
        if self.is_fitted:
            return self.scaler.transform(ad_features.reshape(1, -1)).flatten()
        return ad_features

    def calculate_similarity(self, user_feature: np.ndarray, ad_feature: np.ndarray) -> float:
        """计算用户和广告的相似度"""
        user_feature = self.transform_user_features(user_feature)
        ad_feature = self.transform_ad_features(ad_feature)

        # 确保特征维度一致
        min_dim = min(len(user_feature), len(ad_feature))
        user_feature = user_feature[:min_dim]
        ad_feature = ad_feature[:min_dim]

        similarity = cosine_similarity(
            user_feature.reshape(1, -1),
            ad_feature.reshape(1, -1)
        )[0][0]

        return float(similarity)