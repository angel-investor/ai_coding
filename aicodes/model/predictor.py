"""
模型预测器
加载训练好的模型进行预测
"""

import joblib
import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Union, Optional

logger = logging.getLogger(__name__)


class ModelPredictor:
    """模型预测器类"""
    
    def __init__(self, model_path: str):
        """
        初始化预测器
        
        Args:
            model_path: 模型文件路径
        """
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.feature_names = None
        
        self.load_model()
    
    def load_model(self):
        """加载模型和预处理器"""
        try:
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            
            logger.info(f"成功加载模型: {self.model_path}")
            logger.info(f"特征数量: {len(self.feature_names)}")
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            raise
    
    def predict(self, features: Union[Dict, pd.DataFrame, np.ndarray]) -> Dict:
        """
        进行预测
        
        Args:
            features: 特征数据，可以是字典、DataFrame或数组
            
        Returns:
            预测结果字典，包含预测类别和概率
        """
        try:
            # 转换输入格式
            if isinstance(features, dict):
                # 确保特征顺序正确
                X = pd.DataFrame([features])[self.feature_names]
            elif isinstance(features, pd.DataFrame):
                X = features[self.feature_names]
            else:
                X = np.array(features).reshape(1, -1)
            
            # 标准化
            X_scaled = self.scaler.transform(X)
            
            # 预测
            prediction = self.model.predict(X_scaled)[0]
            probability = self.model.predict_proba(X_scaled)[0]
            
            result = {
                'prediction': int(prediction),
                'probability': {
                    'class_0': float(probability[0]),
                    'class_1': float(probability[1])
                },
                'risk_level': self._get_risk_level(probability[1]),
                'confidence': float(max(probability))
            }
            
            logger.info(f"预测完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"预测失败: {e}")
            raise
    
    def predict_batch(self, features_list: List[Dict]) -> List[Dict]:
        """
        批量预测
        
        Args:
            features_list: 特征字典列表
            
        Returns:
            预测结果列表
        """
        results = []
        for features in features_list:
            result = self.predict(features)
            results.append(result)
        
        logger.info(f"批量预测完成，共 {len(results)} 条")
        return results
    
    def _get_risk_level(self, probability: float) -> str:
        """
        根据概率获取风险等级
        
        Args:
            probability: 患病概率
            
        Returns:
            风险等级字符串
        """
        if probability < 0.3:
            return "低风险"
        elif probability < 0.6:
            return "中风险"
        elif probability < 0.8:
            return "高风险"
        else:
            return "极高风险"
    
    def get_feature_names(self) -> List[str]:
        """
        获取模型需要的特征名称
        
        Returns:
            特征名称列表
        """
        return self.feature_names
    
    def explain_prediction(self, features: Dict) -> Dict:
        """
        解释预测结果（简单版本）
        
        Args:
            features: 特征字典
            
        Returns:
            解释信息字典
        """
        result = self.predict(features)
        
        # 获取特征重要性
        feature_importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        # 排序并取前5个重要特征
        top_features = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        explanation = {
            'prediction_result': result,
            'top_important_features': [
                {'feature': feat, 'importance': float(imp)}
                for feat, imp in top_features
            ],
            'input_features': features
        }
        
        return explanation


if __name__ == "__main__":
    # 测试代码
    predictor = ModelPredictor("./model/xgb_model.pkl")
    
    # 示例特征
    sample_features = {
        'age': 50,
        'gender': 1,
        'height': 170,
        'weight': 75,
        'ap_hi': 120,
        'ap_lo': 80,
        'cholesterol': 1,
        'gluc': 1,
        'smoke': 0,
        'alco': 0,
        'active': 1
    }
    
    result = predictor.predict(sample_features)
    print("预测结果:", result)
