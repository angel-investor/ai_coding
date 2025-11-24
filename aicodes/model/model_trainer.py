"""
模型训练器
用于训练和评估XGBoost模型
"""

import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix, classification_report
)
from sklearn.preprocessing import StandardScaler
import joblib
import os
from typing import Tuple, Dict, Optional


class ModelTrainer:
    """XGBoost模型训练器"""
    
    def __init__(self, data_path: str, target_column: str = 'cardio'):
        """
        初始化模型训练器
        
        Args:
            data_path: 数据集路径
            target_column: 目标列名
        """
        self.data_path = data_path
        self.target_column = target_column
        self.model: Optional[XGBClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: Optional[list] = None
        
    def load_and_preprocess_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        加载并预处理数据
        
        Returns:
            Tuple[DataFrame, Series]: 特征和目标变量
        """
        # 加载数据
        if self.data_path.endswith('.xlsx'):
            df = pd.read_excel(self.data_path)
        elif self.data_path.endswith('.csv'):
            df = pd.read_csv(self.data_path)
        else:
            raise ValueError("不支持的文件格式")
        
        # 分离特征和目标
        X = df.drop(columns=[self.target_column])
        y = df[self.target_column]
        
        # 保存特征名
        self.feature_names = X.columns.tolist()
        
        # 处理缺失值
        X = X.fillna(X.mean())
        
        return X, y
    
    def train_model(
        self, 
        test_size: float = 0.2, 
        random_state: int = 42,
        **xgb_params
    ) -> Dict[str, float]:
        """
        训练XGBoost模型
        
        Args:
            test_size: 测试集比例
            random_state: 随机种子
            **xgb_params: XGBoost参数
            
        Returns:
            Dict: 评估指标
        """
        # 加载数据
        X, y = self.load_and_preprocess_data()
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # 标准化
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 设置默认参数
        default_params = {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'random_state': random_state,
            'eval_metric': 'logloss'
        }
        default_params.update(xgb_params)
        
        # 训练模型
        self.model = XGBClassifier(**default_params)
        self.model.fit(X_train_scaled, y_train)
        
        # 预测
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # 评估
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_pred_proba)
        }
        
        # 打印评估报告
        print("模型评估指标:")
        for metric, value in metrics.items():
            print(f"{metric}: {value:.4f}")
        
        print("\n分类报告:")
        print(classification_report(y_test, y_pred))
        
        print("\n混淆矩阵:")
        print(confusion_matrix(y_test, y_pred))
        
        return metrics
    
    def cross_validate(self, cv: int = 5) -> Dict[str, float]:
        """
        交叉验证
        
        Args:
            cv: 折数
            
        Returns:
            Dict: 交叉验证得分
        """
        X, y = self.load_and_preprocess_data()
        
        if self.model is None:
            raise ValueError("模型尚未训练，请先调用train_model()")
        
        scores = cross_val_score(self.model, X, y, cv=cv, scoring='accuracy')
        
        cv_results = {
            'cv_mean': scores.mean(),
            'cv_std': scores.std(),
            'cv_scores': scores.tolist()
        }
        
        print(f"交叉验证得分: {scores}")
        print(f"平均得分: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")
        
        return cv_results
    
    def save_model(self, model_dir: str = './model'):
        """
        保存模型和预处理器
        
        Args:
            model_dir: 模型保存目录
        """
        if self.model is None:
            raise ValueError("模型尚未训练")
        
        os.makedirs(model_dir, exist_ok=True)
        
        # 保存模型
        model_path = os.path.join(model_dir, 'xgb_model.pkl')
        joblib.dump(self.model, model_path)
        
        # 保存标准化器
        scaler_path = os.path.join(model_dir, 'scaler.pkl')
        joblib.dump(self.scaler, scaler_path)
        
        # 保存特征名
        features_path = os.path.join(model_dir, 'feature_names.pkl')
        joblib.dump(self.feature_names, features_path)
        
        print(f"模型已保存到: {model_path}")
        print(f"标准化器已保存到: {scaler_path}")
        print(f"特征名已保存到: {features_path}")
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        获取特征重要性
        
        Returns:
            DataFrame: 特征重要性排序
        """
        if self.model is None:
            raise ValueError("模型尚未训练")
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df

