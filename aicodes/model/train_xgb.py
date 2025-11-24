"""
XGBoost 分类模型训练
心血管疾病预测
"""

import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    classification_report,
    confusion_matrix,
    roc_auc_score
)
import joblib
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import setup_logger

# 设置日志
logger = setup_logger('train_xgb', log_dir='./logs')


class XGBoostTrainer:
    """XGBoost 模型训练器"""
    
    def __init__(self, data_path: str, target_col: str = 'cardio'):
        """
        初始化训练器
        
        Args:
            data_path: 数据文件路径
            target_col: 目标列名
        """
        self.data_path = data_path
        self.target_col = target_col
        self.model = None
        self.scaler = None
        self.feature_names = None
        
        logger.info(f"初始化 XGBoost 训练器")
        logger.info(f"数据路径: {data_path}")
        logger.info(f"目标列: {target_col}")
    
    def load_data(self):
        """加载数据"""
        logger.info("加载数据...")
        
        try:
            if self.data_path.endswith('.xlsx'):
                df = pd.read_excel(self.data_path)
            elif self.data_path.endswith('.csv'):
                df = pd.read_csv(self.data_path)
            else:
                raise ValueError("不支持的文件格式")
            
            logger.info(f"数据加载成功，形状: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"数据加载失败: {e}")
            raise
    
    def preprocess_data(self, df):
        """
        数据预处理
        
        Args:
            df: 原始数据框
            
        Returns:
            X: 特征矩阵
            y: 目标变量
        """
        logger.info("开始数据预处理...")
        
        # 分离特征和目标
        if self.target_col not in df.columns:
            raise ValueError(f"目标列 '{self.target_col}' 不存在")
        
        # 排除 id 列和目标列
        exclude_cols = [self.target_col]
        if 'id' in df.columns:
            exclude_cols.append('id')
            logger.info("排除 'id' 列")
        
        X = df.drop(columns=exclude_cols)
        y = df[self.target_col]
        
        # 保存特征名
        self.feature_names = X.columns.tolist()
        logger.info(f"特征列: {self.feature_names}")
        
        # 处理缺失值
        if X.isnull().sum().sum() > 0:
            logger.warning("发现缺失值，使用均值填充")
            X = X.fillna(X.mean())
        
        # 检查是否有分类变量需要 one-hot 编码
        categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if categorical_cols:
            logger.info(f"对分类变量进行 one-hot 编码: {categorical_cols}")
            X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
            self.feature_names = X.columns.tolist()
        
        logger.info(f"预处理后特征数: {X.shape[1]}")
        logger.info(f"样本数: {X.shape[0]}")
        logger.info(f"目标变量分布: {y.value_counts().to_dict()}")
        
        return X, y
    
    def split_data(self, X, y, test_size=0.2, random_state=42):
        """
        划分训练集和测试集
        
        Args:
            X: 特征矩阵
            y: 目标变量
            test_size: 测试集比例
            random_state: 随机种子
            
        Returns:
            X_train, X_test, y_train, y_test
        """
        logger.info(f"划分数据集，测试集比例: {test_size}")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=test_size, 
            random_state=random_state,
            stratify=y  # 保持类别比例
        )
        
        logger.info(f"训练集大小: {X_train.shape[0]}")
        logger.info(f"测试集大小: {X_test.shape[0]}")
        
        return X_train, X_test, y_train, y_test
    
    def standardize_features(self, X_train, X_test):
        """
        标准化特征
        
        Args:
            X_train: 训练集特征
            X_test: 测试集特征
            
        Returns:
            X_train_scaled, X_test_scaled
        """
        logger.info("标准化特征...")
        
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        logger.info("特征标准化完成")
        
        return X_train_scaled, X_test_scaled
    
    def train_model(self, X_train, y_train, **params):
        """
        训练 XGBoost 模型
        
        Args:
            X_train: 训练集特征
            y_train: 训练集目标
            **params: XGBoost 参数
        """
        logger.info("开始训练 XGBoost 模型...")
        
        # 默认参数
        default_params = {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42,
            'eval_metric': 'logloss',
            'use_label_encoder': False
        }
        
        # 更新参数
        default_params.update(params)
        
        logger.info(f"模型参数: {default_params}")
        
        # 创建并训练模型
        self.model = XGBClassifier(**default_params)
        self.model.fit(X_train, y_train)
        
        logger.info("模型训练完成")
    
    def evaluate_model(self, X_test, y_test):
        """
        评估模型
        
        Args:
            X_test: 测试集特征
            y_test: 测试集目标
            
        Returns:
            metrics: 评估指标字典
        """
        logger.info("评估模型性能...")
        
        # 预测
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        # 计算指标
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_pred_proba)
        }
        
        # 打印结果
        print("\n" + "=" * 50)
        print("模型评估结果")
        print("=" * 50)
        print(f"Accuracy:  {metrics['accuracy']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall:    {metrics['recall']:.4f}")
        print(f"F1 Score:  {metrics['f1_score']:.4f}")
        print(f"ROC AUC:   {metrics['roc_auc']:.4f}")
        print("=" * 50)
        
        # 详细分类报告
        print("\n分类报告:")
        print(classification_report(y_test, y_pred, target_names=['健康', '患病']))
        
        # 混淆矩阵
        print("\n混淆矩阵:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        print(f"真阴性: {cm[0,0]}, 假阳性: {cm[0,1]}")
        print(f"假阴性: {cm[1,0]}, 真阳性: {cm[1,1]}")
        
        # 记录到日志
        logger.info(f"模型评估完成")
        for metric, value in metrics.items():
            logger.info(f"{metric}: {value:.4f}")
        
        return metrics
    
    def save_model(self, model_dir='./model'):
        """
        保存模型和预处理器
        
        Args:
            model_dir: 模型保存目录
        """
        logger.info(f"保存模型到: {model_dir}")
        
        # 创建目录
        os.makedirs(model_dir, exist_ok=True)
        
        # 保存模型
        model_path = os.path.join(model_dir, 'xgb_model.pkl')
        joblib.dump(self.model, model_path)
        logger.info(f"模型已保存: {model_path}")
        
        # 保存标准化器
        scaler_path = os.path.join(model_dir, 'scaler.pkl')
        joblib.dump(self.scaler, scaler_path)
        logger.info(f"标准化器已保存: {scaler_path}")
        
        # 保存特征名
        features_path = os.path.join(model_dir, 'feature_names.pkl')
        joblib.dump(self.feature_names, features_path)
        logger.info(f"特征名已保存: {features_path}")
        
        print(f"\n✅ 模型文件已保存到: {os.path.abspath(model_dir)}")
    
    def get_feature_importance(self):
        """获取特征重要性"""
        if self.model is None:
            raise ValueError("模型尚未训练")
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n特征重要性 Top 10:")
        print(importance_df.head(10).to_string(index=False))
        
        return importance_df
    
    def run_full_pipeline(self, test_size=0.2, **model_params):
        """
        运行完整的训练流程
        
        Args:
            test_size: 测试集比例
            **model_params: 模型参数
        """
        logger.info("=" * 50)
        logger.info("开始完整训练流程")
        logger.info("=" * 50)
        
        # 1. 加载数据
        df = self.load_data()
        
        # 2. 预处理
        X, y = self.preprocess_data(df)
        
        # 3. 划分数据集
        X_train, X_test, y_train, y_test = self.split_data(X, y, test_size)
        
        # 4. 标准化
        X_train_scaled, X_test_scaled = self.standardize_features(X_train, X_test)
        
        # 5. 训练模型
        self.train_model(X_train_scaled, y_train, **model_params)
        
        # 6. 评估模型
        metrics = self.evaluate_model(X_test_scaled, y_test)
        
        # 7. 特征重要性
        self.get_feature_importance()
        
        # 8. 保存模型
        self.save_model()
        
        logger.info("=" * 50)
        logger.info("训练流程完成")
        logger.info("=" * 50)
        
        return metrics


def main():
    """主函数"""
    # 数据路径
    data_path = "D:/project/workspace/ai_coding/data/心血管疾病.xlsx"
    
    # 创建训练器
    trainer = XGBoostTrainer(data_path, target_col='cardio')
    
    # 运行完整训练流程
    metrics = trainer.run_full_pipeline(
        test_size=0.2,
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8
    )
    
    print("\n" + "=" * 50)
    print("🎉 训练完成！")
    print("=" * 50)
    print("\n下一步:")
    print("1. 查看模型文件: model/xgb_model.pkl")
    print("2. 启动 Flask 服务: python run_server.py")
    print("3. 访问预测页面: http://localhost:5000/web/predict.html")
    print("=" * 50 + "\n")


if __name__ == '__main__':
    main()

