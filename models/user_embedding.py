import numpy as np
from collections import defaultdict


class UserEmbeddingModel:
    def __init__(self, embedding_size=128):
        self.embedding_size = embedding_size
        self.user_embeddings = {}
        self.ad_embeddings = {}
        self.user_interaction_history = defaultdict(list)

    def update_user_embedding(self, user_id, ad_id, action):
        """基于用户交互更新嵌入向量"""
        if user_id not in self.user_embeddings:
            self.user_embeddings[user_id] = np.random.normal(0, 0.1, self.embedding_size)

        if ad_id not in self.ad_embeddings:
            self.ad_embeddings[ad_id] = np.random.normal(0, 0.1, self.embedding_size)

        # 记录交互历史
        self.user_interaction_history[user_id].append({
            'ad_id': ad_id,
            'action': action,
            'timestamp': np.datetime64('now')
        })

        user_embedding = self.user_embeddings[user_id]
        ad_embedding = self.ad_embeddings[ad_id]

        # 根据行为调整嵌入向量
        if action == 'click':
            learning_rate = 0.1
            self.user_embeddings[user_id] = user_embedding + learning_rate * ad_embedding
        elif action == 'view':
            learning_rate = 0.01
            self.user_embeddings[user_id] = user_embedding + learning_rate * ad_embedding

    def get_user_similar_ads(self, user_id, top_k=5):
        """获取与用户相似的广告"""
        if user_id not in self.user_embeddings:
            return []

        user_embedding = self.user_embeddings[user_id]
        similarities = []

        for ad_id, ad_embedding in self.ad_embeddings.items():
            similarity = self.cosine_similarity(user_embedding, ad_embedding)
            similarities.append((ad_id, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return [ad_id for ad_id, similarity in similarities[:top_k]]

    @staticmethod
    def cosine_similarity(vec1, vec2):
        """计算余弦相似度"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)