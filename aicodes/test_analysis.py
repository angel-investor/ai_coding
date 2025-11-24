"""
测试数据分析模块
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analysis.data_analysis import CardiovascularDataAnalysis

def main():
    """测试数据分析功能"""
    
    print("=" * 60)
    print("测试数据分析模块")
    print("=" * 60)
    
    # 数据路径
    data_path = "D:/project/workspace/ai_coding/data/心血管疾病.xlsx"
    
    # 检查数据文件是否存在
    if not os.path.exists(data_path):
        print(f"❌ 错误: 数据文件不存在")
        print(f"   路径: {data_path}")
        print("\n请确保数据文件存在后再运行此脚本。")
        return
    
    print(f"✓ 数据文件存在: {data_path}")
    print()
    
    # 创建分析器
    print("1. 创建数据分析器...")
    analyzer = CardiovascularDataAnalysis(data_path)
    
    # 加载数据
    print("2. 加载数据...")
    df = analyzer.load_data()
    print(f"   数据形状: {df.shape}")
    print(f"   列名: {df.columns.tolist()}")
    print()
    
    # 生成基础统计
    print("3. 生成基础统计信息...")
    stats = analyzer.generate_basic_stats()
    print(f"   总样本数: {stats['shape'][0]:,}")
    print(f"   特征数量: {stats['shape'][1]}")
    if 'cardio_distribution' in stats and stats['cardio_distribution']:
        print(f"   患病人数: {stats['cardio_distribution'].get(1, 0):,}")
        print(f"   健康人数: {stats['cardio_distribution'].get(0, 0):,}")
    print()
    
    # 生成图表
    print("4. 生成图表...")
    print("   - 年龄分布直方图")
    analyzer.plot_age_distribution()
    
    print("   - 血压箱线图")
    analyzer.plot_blood_pressure_boxplot()
    
    print("   - 特征相关性热力图")
    analyzer.plot_correlation_heatmap()
    
    print("   - 分类特征对比图")
    analyzer.plot_categorical_vs_cardio()
    
    print("   - 疾病分布饼图")
    analyzer.plot_cardio_distribution()
    
    print(f"   共生成 {len(analyzer.figures)} 个图表")
    print()
    
    # 生成 HTML 报告
    print("5. 生成 HTML 报告...")
    output_path = 'analysis/report.html'
    report_path = analyzer.generate_html_report(output_path)
    
    print()
    print("=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    print(f"\n📊 报告已生成: {os.path.abspath(report_path)}")
    print(f"📝 日志文件: logs/analysis_*.log")
    print(f"\n💡 请用浏览器打开 report.html 查看完整报告")
    print("=" * 60)


if __name__ == '__main__':
    main()

