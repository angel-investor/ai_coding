"""
模型训练器
使用 XGBoost 训练心血管疾病预测模型
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib
import os
import logging
from typing import Tuple, Dict, Optional

logger = logging.getLogger(__name__)


class ModelTrainer:
    """XGBoost 模型训练器"""
    
    def __init__(self, data_path: str, target_col: str = 'cardio'):
        """
        初始化模型训练器
        
        Args:
            data_path: 数据文件路径
            target_col: 目标列名
        """
        self.data_path = data_path
        self.target_col = target_col
        self.model: Optional[xgb.XGBClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: Optional[list] = None
        
        logger.info(f"初始化模型训练器，数据路径: {data_path}")
    
    def load_and_preprocess_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        加载并预处理数据
        
        Returns:
            特征数据框和目标序列
        """
        try:
            # 加载数据
            df = pd.read_excel(self.data_path)
            logger.info(f"成功加载数据，共 {len(df)} 行")
            
            # 检查目标列是否存在
            if self.target_col not in df.columns:
                raise ValueError(f"目标列 '{self.target_col}' 不存在于数据中")
            
            # 分离特征和目标
            X = df.drop(columns=[self.target_col])
            y = df[self.target_col]
            
            # 处理缺失值
            X = X.fillna(X.mean())
            
            # 保存特征名称
            self.feature_names = list(X.columns)
            
            logger.info(f"数据预处理完成，特征数: {X.shape[1]}")
            return X, y
            
        except Exception as e:
            logger.error(f"数据加载和预处理失败: {e}")
            raise
    
    def train(self, 
              test_size: float = 0.2, 
              random_state: int = 42,
              **xgb_params) -> Dict[str, float]:
        """
        训练模型
        
        Args:
            test_size: 测试集比例
            random_state: 随机种子
            **xgb_params: XGBoost 参数
            
        Returns:
            评估指标字典
        """
        # 加载数据
        X, y = self.load_and_preprocess_data()
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        logger.info(f"训练集大小: {len(X_train)}, 测试集大小: {len(X_test)}")
        
        # 标准化
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 设置默认参数
        default_params = {
            'objective': 'binary:logistic',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'random_state': random_state,
            'eval_metric': 'logloss'
        }
        default_params.update(xgb_params)
        
        # 训练模型
        logger.info("开始训练 XGBoost 模型...")
        self.model = xgb.XGBClassifier(**default_params)
        self.model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_test_scaled, y_test)],
            verbose=False
        )
        
        # 预测
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # 计算评估指标
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_pred_proba)
        }
        
        # 混淆矩阵
        cm = confusion_matrix(y_test, y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        
        logger.info("模型训练完成")
        logger.info(f"准确率: {metrics['accuracy']:.4f}")
        logger.info(f"精确率: {metrics['precision']:.4f}")
        logger.info(f"召回率: {metrics['recall']:.4f}")
        logger.info(f"F1分数: {metrics['f1_score']:.4f}")
        logger.info(f"ROC AUC: {metrics['roc_auc']:.4f}")
        
        return metrics
    
    def cross_validate(self, cv: int = 5) -> Dict[str, float]:
        """
        交叉验证
        
        Args:
            cv: 折数
            
        Returns:
            交叉验证结果
        """
        if self.model is None:
            raise ValueError("模型尚未训练，请先调用 train() 方法")
        
        X, y = self.load_and_preprocess_data()
        X_scaled = self.scaler.transform(X)
        
        scores = cross_val_score(self.model, X_scaled, y, cv=cv, scoring='accuracy')
        
        cv_results = {
            'mean_score': scores.mean(),
            'std_score': scores.std(),
            'scores': scores.tolist()
        }
        
        logger.info(f"交叉验证完成，平均准确率: {cv_results['mean_score']:.4f} (+/- {cv_results['std_score']:.4f})")
        
        return cv_results
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        获取特征重要性
        
        Returns:
            特征重要性数据框
        """
        if self.model is None:
            raise ValueError("模型尚未训练，请先调用 train() 方法")
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("特征重要性计算完成")
        return importance_df
    
    def save_model(self, model_path: str = "./model/xgb_model.pkl"):
        """
        保存模型和预处理器
        
        Args:
            model_path: 模型保存路径
        """
        if self.model is None:
            raise ValueError("模型尚未训练，请先调用 train() 方法")
        
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # 保存模型、标准化器和特征名称
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }
        
        joblib.dump(model_data, model_path)
        logger.info(f"模型已保存至: {model_path}")
        print(f"✅ 模型已保存至: {model_path}")


if __name__ == "__main__":
    # 测试代码
    trainer = ModelTrainer("D:/project/workspace/ai_coding/data/心血管疾病.xlsx")
    metrics = trainer.train()
    print("\n模型评估指标:")
    for key, value in metrics.items():
        if key != 'confusion_matrix':
            print(f"{key}: {value:.4f}")
    
    # 保存模型
    trainer.save_model()
    
    # 特征重要性
    importance = trainer.get_feature_importance()
    print("\n特征重要性 Top 10:")
    print(importance.head(10))
