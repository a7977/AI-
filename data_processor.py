import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import json
from sqlalchemy.orm import Session
from database.models import User, Advertisement, UserInteraction


class DataProcessor:
    def __init__(self, db_session: Optional[Session] = None):
        """初始化数据处理器

        Args:
            db_session: 数据库会话，如果为None则使用内存数据
        """
        self.db_session = db_session
        self.user_profiles = {}
        self.ad_inventory = {}
        self.interaction_history = []
        self.feature_dim = 8

    def load_data_from_db(self):
        """从数据库加载数据"""
        if not self.db_session:
            print("⚠️ 未提供数据库会话，使用示例数据")
            self.load_sample_data()
            return

        try:
            print("📥 从数据库加载数据...")

            # 加载用户数据
            users = self.db_session.query(User).all()
            for user in users:
                self.user_profiles[user.user_id] = {
                    "age": user.age,
                    "gender": user.gender,
                    "interests": user.interests or [],
                    "location": user.location,
                    "device": user.device
                }

            # 加载广告数据
            ads = self.db_session.query(Advertisement).filter(Advertisement.is_active == True).all()
            for ad in ads:
                self.ad_inventory[ad.ad_id] = {
                    "title": ad.title,
                    "category": ad.category,
                    "keywords": ad.keywords or [],
                    "target_age": [ad.target_age_min, ad.target_age_max],
                    "target_gender": ad.target_gender,
                    "bid_price": ad.bid_price
                }

            # 加载交互数据
            interactions = self.db_session.query(UserInteraction).all()
            for interaction in interactions:
                self.interaction_history.append({
                    "user_id": interaction.user_id,
                    "ad_id": interaction.ad_id,
                    "action": interaction.action,
                    "timestamp": interaction.timestamp.isoformat() if interaction.timestamp else None
                })

            print(f"✅ 从数据库加载: {len(users)} 用户, {len(ads)} 广告, {len(interactions)} 交互记录")

        except Exception as e:
            print(f"❌ 数据库加载失败: {e}，使用示例数据")
            self.load_sample_data()

    def load_sample_data(self):
        """加载示例数据（当没有数据库时使用）"""
        print("📝 加载示例数据...")

        # 模拟用户数据
        self.user_profiles = {
            "user_1": {
                "age": 25,
                "gender": "male",
                "interests": ["technology", "sports", "gaming"],
                "location": "Beijing",
                "device": "mobile"
            },
            "user_2": {
                "age": 30,
                "gender": "female",
                "interests": ["fashion", "beauty", "travel"],
                "location": "Shanghai",
                "device": "desktop"
            },
            "user_3": {
                "age": 35,
                "gender": "male",
                "interests": ["business", "finance", "travel"],
                "location": "Shenzhen",
                "device": "tablet"
            }
        }

        # 模拟广告数据
        self.ad_inventory = {
            "ad_1": {
                "title": "最新智能手机",
                "category": "electronics",
                "keywords": ["technology", "mobile", "innovation"],
                "target_age": [18, 35],
                "target_gender": "all",
                "bid_price": 2.5
            },
            "ad_2": {
                "title": "时尚女装",
                "category": "clothing",
                "keywords": ["fashion", "beauty", "style"],
                "target_age": [20, 40],
                "target_gender": "female",
                "bid_price": 1.8
            },
            "ad_3": {
                "title": "旅游套餐",
                "category": "travel",
                "keywords": ["travel", "vacation", "adventure"],
                "target_age": [25, 50],
                "target_gender": "all",
                "bid_price": 3.2
            },
            "ad_4": {
                "title": "游戏设备",
                "category": "electronics",
                "keywords": ["gaming", "entertainment", "technology"],
                "target_age": [15, 30],
                "target_gender": "male",
                "bid_price": 2.0
            }
        }

        # 模拟交互历史
        self.interaction_history = [
            {"user_id": "user_1", "ad_id": "ad_1", "action": "click", "timestamp": "2024-01-01 10:00:00"},
            {"user_id": "user_1", "ad_id": "ad_4", "action": "click", "timestamp": "2024-01-01 11:00:00"},
            {"user_id": "user_2", "ad_id": "ad_2", "action": "click", "timestamp": "2024-01-01 12:00:00"},
            {"user_id": "user_3", "ad_id": "ad_3", "action": "view", "timestamp": "2024-01-01 13:00:00"},
        ]

        print(
            f"✅ 示例数据加载: {len(self.user_profiles)} 用户, {len(self.ad_inventory)} 广告, {len(self.interaction_history)} 交互记录")

    def save_interaction_to_db(self, user_id: str, ad_id: str, action: str):
        """保存交互记录到数据库"""
        if not self.db_session:
            print("⚠️ 无数据库会话，跳过保存")
            return

        try:
            from datetime import datetime
            interaction = UserInteraction(
                user_id=user_id,
                ad_id=ad_id,
                action=action,
                timestamp=datetime.now()
            )
            self.db_session.add(interaction)
            self.db_session.commit()

            # 更新内存中的交互历史
            self.interaction_history.append({
                "user_id": user_id,
                "ad_id": ad_id,
                "action": action,
                "timestamp": interaction.timestamp.isoformat() if interaction.timestamp else None
            })

            print(f"✅ 交互记录已保存到数据库")

        except Exception as e:
            print(f"❌ 保存交互记录失败: {e}")
            self.db_session.rollback()

    def create_user_features(self, user_id: str) -> np.ndarray:
        """创建用户特征向量 - 统一为8维"""
        if user_id not in self.user_profiles:
            return np.zeros(self.feature_dim)

        user = self.user_profiles[user_id]

        # 统一使用8维特征
        features = np.zeros(self.feature_dim)

        # 特征1: 年龄归一化 (0-1)
        features[0] = user["age"] / 100.0

        # 特征2: 性别编码 (男:1, 女:0)
        features[1] = 1.0 if user["gender"] == "male" else 0.0

        # 特征3: 兴趣数量归一化
        features[2] = len(user["interests"]) / 10.0

        # 特征4: 设备编码 (mobile:0.3, desktop:0.6, tablet:0.9)
        device_map = {"mobile": 0.3, "desktop": 0.6, "tablet": 0.9}
        features[3] = device_map.get(user["device"], 0.5)

        # 特征5-7: 基于兴趣的简单编码
        interest_strength = 0.0
        for interest in user["interests"]:
            if interest in ["technology", "gaming"]:
                interest_strength += 0.2
            elif interest in ["fashion", "beauty"]:
                interest_strength += 0.1
        features[4] = min(interest_strength, 1.0)

        # 特征6: 随机特征1
        features[5] = 0.3

        # 特征7: 随机特征2
        features[6] = 0.7

        # 特征8: 随机特征3
        features[7] = 0.5

        return features

    def create_ad_features(self, ad_id: str) -> np.ndarray:
        """创建广告特征向量 - 统一为8维"""
        if ad_id not in self.ad_inventory:
            return np.zeros(self.feature_dim)

        ad = self.ad_inventory[ad_id]

        # 统一使用8维特征
        features = np.zeros(self.feature_dim)

        # 特征1: 价格归一化
        features[0] = ad["bid_price"] / 10.0

        # 特征2: 关键词数量归一化
        features[1] = len(ad["keywords"]) / 5.0

        # 特征3: 目标年龄范围
        target_age_range = ad["target_age"][1] - ad["target_age"][0]
        features[2] = target_age_range / 50.0

        # 特征4: 性别目标 (all:0.5, male:0.8, female:0.2)
        gender_map = {"all": 0.5, "male": 0.8, "female": 0.2}
        features[3] = gender_map.get(ad["target_gender"], 0.5)

        # 特征5: 类别编码
        category_map = {
            "electronics": 0.8, "clothing": 0.4, "food": 0.2,
            "travel": 0.6, "education": 0.3, "entertainment": 0.7,
            "sports": 0.5, "beauty": 0.4
        }
        features[4] = category_map.get(ad["category"], 0.5)

        # 特征6: 随机特征1
        features[5] = 0.4

        # 特征7: 随机特征2
        features[6] = 0.6

        # 特征8: 随机特征3
        features[7] = 0.9

        return features