"""
模型预测器
用于加载模型并进行预测
"""

import joblib
import numpy as np
import pandas as pd
from typing import Union, List, Dict
import os


class ModelPredictor:
    """模型预测器类"""
    
    def __init__(self, model_dir: str = './model'):
        """
        初始化预测器
        
        Args:
            model_dir: 模型文件目录
        """
        self.model_dir = model_dir
        self.model = None
        self.scaler = None
        self.feature_names = None
        
    def load_model(self):
        """加载模型、标准化器和特征名"""
        model_path = os.path.join(self.model_dir, 'xgb_model.pkl')
        scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
        features_path = os.path.join(self.model_dir, 'feature_names.pkl')
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.feature_names = joblib.load(features_path)
        
        print("模型加载成功")
    
    def predict(self, features: Union[Dict, pd.DataFrame, np.ndarray]) -> Dict:
        """
        进行预测
        
        Args:
            features: 特征数据（字典、DataFrame或数组）
            
        Returns:
            Dict: 预测结果
        """
        if self.model is None:
            self.load_model()
        
        # 转换输入为DataFrame
        if isinstance(features, dict):
            df = pd.DataFrame([features])
        elif isinstance(features, np.ndarray):
            df = pd.DataFrame(features, columns=self.feature_names)
        else:
            df = features
        
        # 确保特征顺序正确
        df = df[self.feature_names]
        
        # 标准化
        features_scaled = self.scaler.transform(df)
        
        # 预测
        prediction = self.model.predict(features_scaled)[0]
        probability = self.model.predict_proba(features_scaled)[0]
        
        result = {
            'prediction': int(prediction),
            'probability': {
                'negative': float(probability[0]),
                'positive': float(probability[1])
            },
            'risk_level': self._get_risk_level(probability[1])
        }
        
        return result
    
    def predict_batch(self, features_list: List[Dict]) -> List[Dict]:
        """
        批量预测
        
        Args:
            features_list: 特征字典列表
            
        Returns:
            List[Dict]: 预测结果列表
        """
        if self.model is None:
            self.load_model()
        
        df = pd.DataFrame(features_list)
        df = df[self.feature_names]
        
        features_scaled = self.scaler.transform(df)
        
        predictions = self.model.predict(features_scaled)
        probabilities = self.model.predict_proba(features_scaled)
        
        results = []
        for i in range(len(predictions)):
            result = {
                'prediction': int(predictions[i]),
                'probability': {
                    'negative': float(probabilities[i][0]),
                    'positive': float(probabilities[i][1])
                },
                'risk_level': self._get_risk_level(probabilities[i][1])
            }
            results.append(result)
        
        return results
    
    def _get_risk_level(self, probability: float) -> str:
        """
        根据概率判断风险等级
        
        Args:
            probability: 患病概率
            
        Returns:
            str: 风险等级
        """
        if probability < 0.3:
            return '低风险'
        elif probability < 0.6:
            return '中风险'
        else:
            return '高风险'
    
    def get_feature_names(self) -> List[str]:
        """
        获取特征名列表
        
        Returns:
            List[str]: 特征名
        """
        if self.feature_names is None:
            self.load_model()
        
        return self.feature_names

