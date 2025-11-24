"""
运行数据分析脚本
快速生成数据分析报告
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.data_analyzer import DataAnalyzer
from utils.config import Config


def main():
    """主函数"""
    print("=" * 60)
    print("心血管疾病数据分析")
    print("=" * 60)
    
    # 加载配置
    config = Config()
    
    # 创建分析器
    analyzer = DataAnalyzer(config.DATA_PATH)
    
    # 运行分析
    success = analyzer.run_full_analysis()
    
    if success:
        print("\n✓ 分析完成！")
    else:
        print("\n✗ 分析失败")
        sys.exit(1)


if __name__ == "__main__":
    main()

