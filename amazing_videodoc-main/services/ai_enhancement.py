"""
AI增强分析服务 - 关键词提取、情感分析、主题分类等
"""
import openai
import cohere
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import re

logger = logging.getLogger(__name__)

class AIEnhancementService:
    def __init__(self, openai_api_key: str, cohere_api_key: str):
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.cohere_client = cohere.Client(api_key=cohere_api_key)
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[Dict[str, Any]]:
        """提取关键词"""
        try:
            # 使用Cohere进行关键词提取
            response = self.cohere_client.generate(
                model="command",
                prompt=f"""请从以下文本中提取最重要的{max_keywords}个关键词，按重要性排序：

文本：{text}

请以JSON格式返回，格式如下：
[
    {{"keyword": "关键词", "importance": 0.9, "category": "类别"}},
    ...
]""",
                max_tokens=500,
                temperature=0.3
            )
            
            # 解析响应
            result_text = response.generations[0].text.strip()
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            keywords = json.loads(result_text)
            return keywords[:max_keywords]
            
        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            # 降级到TF-IDF方法
            return self._extract_keywords_tfidf(text, max_keywords)
    
    def _extract_keywords_tfidf(self, text: str, max_keywords: int) -> List[Dict[str, Any]]:
        """使用TF-IDF提取关键词（降级方案）"""
        try:
            # 简单的文本预处理
            words = re.findall(r'\b\w+\b', text.lower())
            words = [w for w in words if len(w) > 2]
            
            if not words:
                return []
            
            # 使用TF-IDF
            vectorizer = TfidfVectorizer(max_features=max_keywords, stop_words=None)
            tfidf_matrix = vectorizer.fit_transform([' '.join(words)])
            
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # 排序并返回
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return [
                {
                    "keyword": kw,
                    "importance": float(score),
                    "category": "general"
                }
                for kw, score in keyword_scores[:max_keywords]
            ]
            
        except Exception as e:
            logger.error(f"TF-IDF关键词提取失败: {e}")
            return []
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """情感分析"""
        try:
            response = self.cohere_client.classify(
                model="large",
                inputs=[text],
                examples=[
                    {"text": "这个视频太棒了，学到了很多知识", "label": "positive"},
                    {"text": "内容很无聊，浪费时间", "label": "negative"},
                    {"text": "视频质量一般，还可以", "label": "neutral"},
                    {"text": "非常有用，强烈推荐", "label": "positive"},
                    {"text": "完全听不懂，太难了", "label": "negative"},
                    {"text": "内容比较基础，适合初学者", "label": "neutral"}
                ]
            )
            
            classification = response.classifications[0]
            prediction = classification.prediction
            confidence = classification.confidence
            
            return {
                "sentiment": prediction,
                "confidence": float(confidence),
                "positive_score": float(classification.labels.get("positive", {}).get("confidence", 0)),
                "negative_score": float(classification.labels.get("negative", {}).get("confidence", 0)),
                "neutral_score": float(classification.labels.get("neutral", {}).get("confidence", 0))
            }
            
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "positive_score": 0.33,
                "negative_score": 0.33,
                "neutral_score": 0.34
            }
    
    def classify_topic(self, text: str) -> Dict[str, Any]:
        """主题分类"""
        try:
            response = self.cohere_client.classify(
                model="large",
                inputs=[text],
                examples=[
                    {"text": "Python编程教程，教你如何写代码", "label": "technology"},
                    {"text": "数学微积分课程，导数积分", "label": "education"},
                    {"text": "美食制作教程，如何做菜", "label": "lifestyle"},
                    {"text": "健身运动指导，减肥塑形", "label": "health"},
                    {"text": "历史故事讲解，古代文化", "label": "culture"},
                    {"text": "商业管理课程，创业指导", "label": "business"},
                    {"text": "艺术绘画教程，创意设计", "label": "art"},
                    {"text": "科学实验演示，物理化学", "label": "science"}
                ]
            )
            
            classification = response.classifications[0]
            prediction = classification.prediction
            confidence = classification.confidence
            
            # 获取所有类别的置信度
            topic_scores = {}
            for label, data in classification.labels.items():
                topic_scores[label] = float(data.confidence)
            
            return {
                "primary_topic": prediction,
                "confidence": float(confidence),
                "topic_scores": topic_scores
            }
            
        except Exception as e:
            logger.error(f"主题分类失败: {e}")
            return {
                "primary_topic": "general",
                "confidence": 0.5,
                "topic_scores": {"general": 1.0}
            }
    
    def detect_similarity(self, texts: List[str], threshold: float = 0.8) -> List[Dict[str, Any]]:
        """检测文本相似度"""
        try:
            if len(texts) < 2:
                return []
            
            # 获取文本嵌入
            embeddings = []
            for text in texts:
                response = self.cohere_client.embed(
                    model="embed-english-v2.0",
                    texts=[text]
                )
                embeddings.append(response.embeddings[0])
            
            embeddings = np.array(embeddings)
            
            # 计算相似度矩阵
            similarity_matrix = cosine_similarity(embeddings)
            
            # 找出相似度超过阈值的文本对
            similar_pairs = []
            for i in range(len(texts)):
                for j in range(i + 1, len(texts)):
                    similarity = similarity_matrix[i][j]
                    if similarity >= threshold:
                        similar_pairs.append({
                            "text1_index": i,
                            "text2_index": j,
                            "similarity": float(similarity),
                            "text1": texts[i][:100] + "..." if len(texts[i]) > 100 else texts[i],
                            "text2": texts[j][:100] + "..." if len(texts[j]) > 100 else texts[j]
                        })
            
            return similar_pairs
            
        except Exception as e:
            logger.error(f"相似度检测失败: {e}")
            return []
    
    def generate_summary_enhanced(self, text: str, max_length: int = 200) -> Dict[str, Any]:
        """生成增强摘要"""
        try:
            # 使用GPT生成结构化摘要
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的内容分析师，请为给定的文本生成结构化摘要。"
                    },
                    {
                        "role": "user",
                        "content": f"""请为以下文本生成结构化摘要，包含：
1. 核心观点（3-5个要点）
2. 关键数据或事实
3. 主要结论
4. 适用人群

文本：{text}

请以JSON格式返回，确保摘要简洁明了。"""
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            summary_text = response.choices[0].message.content
            
            # 尝试解析JSON
            try:
                summary_data = json.loads(summary_text)
            except:
                # 如果不是JSON，创建简单结构
                summary_data = {
                    "core_points": [summary_text],
                    "key_facts": [],
                    "conclusions": [],
                    "target_audience": "general"
                }
            
            return summary_data
            
        except Exception as e:
            logger.error(f"增强摘要生成失败: {e}")
            return {
                "core_points": [text[:200] + "..." if len(text) > 200 else text],
                "key_facts": [],
                "conclusions": [],
                "target_audience": "general"
            }
    
    def analyze_learning_difficulty(self, text: str) -> Dict[str, Any]:
        """分析学习难度"""
        try:
            response = self.cohere_client.classify(
                model="large",
                inputs=[text],
                examples=[
                    {"text": "这是最基础的入门教程，适合完全的新手", "label": "beginner"},
                    {"text": "需要一定的编程基础，中等难度", "label": "intermediate"},
                    {"text": "高级主题，需要深厚的专业知识", "label": "advanced"},
                    {"text": "专家级内容，需要多年经验", "label": "expert"}
                ]
            )
            
            classification = response.classifications[0]
            prediction = classification.prediction
            confidence = classification.confidence
            
            # 难度等级映射
            difficulty_levels = {
                "beginner": {"level": 1, "name": "入门级", "description": "适合初学者"},
                "intermediate": {"level": 2, "name": "中级", "description": "需要一定基础"},
                "advanced": {"level": 3, "name": "高级", "description": "需要专业知识"},
                "expert": {"level": 4, "name": "专家级", "description": "需要丰富经验"}
            }
            
            level_info = difficulty_levels.get(prediction, difficulty_levels["intermediate"])
            
            return {
                "difficulty_level": prediction,
                "level_info": level_info,
                "confidence": float(confidence)
            }
            
        except Exception as e:
            logger.error(f"学习难度分析失败: {e}")
            return {
                "difficulty_level": "intermediate",
                "level_info": {"level": 2, "name": "中级", "description": "需要一定基础"},
                "confidence": 0.5
            }
    
    def generate_learning_path(self, topics: List[str]) -> List[Dict[str, Any]]:
        """生成学习路径建议"""
        try:
            if not topics:
                return []
            
            # 使用GPT生成学习路径
            topics_text = "、".join(topics)
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的学习顾问，请根据给定的主题生成合理的学习路径。"
                    },
                    {
                        "role": "user",
                        "content": f"""请为以下主题生成学习路径：{topics_text}

请以JSON格式返回，包含：
1. 学习顺序
2. 每个阶段的重点
3. 预估学习时间
4. 推荐资源类型

格式：
[
    {{"step": 1, "topic": "主题", "focus": "重点", "duration": "时间", "resources": "资源类型"}},
    ...
]"""
                    }
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            path_text = response.choices[0].message.content
            
            try:
                learning_path = json.loads(path_text)
                return learning_path
            except:
                # 降级方案
                return [
                    {
                        "step": 1,
                        "topic": topics[0] if topics else "基础学习",
                        "focus": "掌握基础概念",
                        "duration": "1-2周",
                        "resources": "入门教程"
                    }
                ]
                
        except Exception as e:
            logger.error(f"学习路径生成失败: {e}")
            return []
