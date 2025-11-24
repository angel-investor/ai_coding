"""
模型训练脚本
用于训练和保存 XGBoost 模型
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.model_trainer import ModelTrainer
from utils.config import Config
from utils.logger import setup_logger


def main():
    """主函数"""
    # 设置日志
    logger = setup_logger('train_model')
    
    # 加载配置
    config = Config()
    
    logger.info("=" * 50)
    logger.info("开始训练心血管疾病预测模型")
    logger.info("=" * 50)
    
    # 创建训练器
    logger.info(f"数据路径: {config.DATA_PATH}")
    trainer = ModelTrainer(data_path=config.DATA_PATH, target_column='cardio')
    
    # 训练模型
    logger.info("\n训练模型...")
    metrics = trainer.train_model(
        test_size=0.2,
        random_state=42,
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1
    )
    
    # 交叉验证
    logger.info("\n进行交叉验证...")
    cv_results = trainer.cross_validate(cv=5)
    
    # 特征重要性
    logger.info("\n特征重要性:")
    importance_df = trainer.get_feature_importance()
    print(importance_df.head(10))
    
    # 保存模型
    logger.info(f"\n保存模型到: {config.MODEL_DIR}")
    trainer.save_model(model_dir=config.MODEL_DIR)
    
    logger.info("\n" + "=" * 50)
    logger.info("模型训练完成!")
    logger.info("=" * 50)
    
    # 打印总结
    print("\n模型评估总结:")
    print(f"准确率: {metrics['accuracy']:.4f}")
    print(f"精确率: {metrics['precision']:.4f}")
    print(f"召回率: {metrics['recall']:.4f}")
    print(f"F1分数: {metrics['f1_score']:.4f}")
    print(f"ROC AUC: {metrics['roc_auc']:.4f}")
    print(f"\n交叉验证平均得分: {cv_results['cv_mean']:.4f} (+/- {cv_results['cv_std']:.4f})")


if __name__ == '__main__':
    main()
