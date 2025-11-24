"""
生成数据分析报告脚本
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.data_analysis import CardiovascularDataAnalysis
from utils.config import Config
from utils.logger import setup_logger


def main():
    """主函数"""
    # 设置日志
    logger = setup_logger('generate_report')
    
    # 加载配置
    config = Config()
    
    logger.info("=" * 50)
    logger.info("开始生成数据分析报告")
    logger.info("=" * 50)
    
    # 创建分析器
    logger.info(f"数据路径: {config.DATA_PATH}")
    analyzer = CardiovascularDataAnalysis(data_path=config.DATA_PATH)
    
    # 加载数据
    logger.info("\n加载数据...")
    df = analyzer.load_data()
    logger.info(f"数据形状: {df.shape}")
    
    # 生成基础统计
    logger.info("\n生成基础统计信息...")
    stats = analyzer.generate_basic_stats()
    print(f"\n数据集信息:")
    print(f"  - 总样本数: {stats['shape'][0]:,}")
    print(f"  - 特征数量: {stats['shape'][1]}")
    print(f"  - 患病人数: {stats['cardio_distribution'].get(1, 0):,}")
    print(f"  - 健康人数: {stats['cardio_distribution'].get(0, 0):,}")
    
    # 生成 HTML 报告
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'analysis',
        'report.html'
    )
    
    logger.info(f"\n生成 HTML 报告: {output_path}")
    report_path = analyzer.generate_html_report(output_path)
    
    logger.info("\n" + "=" * 50)
    logger.info("报告生成完成!")
    logger.info(f"报告位置: {os.path.abspath(report_path)}")
    logger.info("=" * 50)
    
    print("\n" + "=" * 50)
    print("✅ 数据分析报告生成完成！")
    print(f"📊 报告位置: {os.path.abspath(report_path)}")
    print("💡 请用浏览器打开 report.html 查看完整报告")
    print("=" * 50 + "\n")


if __name__ == '__main__':
    main()

