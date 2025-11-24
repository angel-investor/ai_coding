"""
主程序入口
提供命令行界面选择不同功能
"""

import sys
import os


def print_menu():
    """打印菜单"""
    print("\n" + "=" * 60)
    print("心血管疾病预测系统")
    print("=" * 60)
    print("\n请选择功能:")
    print("  1. 数据分析 - 生成交互式 HTML 分析报告")
    print("  2. 模型训练 - 训练 XGBoost 预测模型")
    print("  3. 启动服务器 - 启动 Flask API 服务")
    print("  4. 测试预测 - 测试模型预测功能")
    print("  5. 退出")
    print("=" * 60)


def run_analysis():
    """运行数据分析"""
    from scripts.run_analysis import main
    main()


def train_model():
    """训练模型"""
    from scripts.train_model import main
    main()


def start_server():
    """启动服务器"""
    from scripts.start_server import main
    main()


def test_prediction():
    """测试预测"""
    from model.predictor import ModelPredictor
    from utils.config import Config
    
    config = Config()
    predictor = ModelPredictor(config.MODEL_PATH)
    
    if not predictor.load_model():
        print("模型加载失败，请先训练模型")
        return
    
    print("\n请输入测试数据（示例）:")
    
    # 示例数据
    test_data = {
        'age': 50,
        'gender': 2,
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
    
    print(f"\n使用示例数据: {test_data}")
    
    result = predictor.predict(test_data)
    
    if result:
        print("\n预测结果:")
        print(f"  预测类别: {result['prediction']}")
        print(f"  概率分布: {result['probability']}")
        print(f"  置信度: {result['confidence']:.2%}")
    else:
        print("预测失败")


def main():
    """主函数"""
    while True:
        print_menu()
        
        try:
            choice = input("\n请输入选项 (1-5): ").strip()
            
            if choice == '1':
                run_analysis()
            elif choice == '2':
                train_model()
            elif choice == '3':
                start_server()
            elif choice == '4':
                test_prediction()
            elif choice == '5':
                print("\n再见！")
                sys.exit(0)
            else:
                print("\n无效选项，请重新输入")
            
            input("\n按 Enter 键继续...")
            
        except KeyboardInterrupt:
            print("\n\n程序已中断")
            sys.exit(0)
        except Exception as e:
            print(f"\n错误: {e}")
            input("\n按 Enter 键继续...")


if __name__ == "__main__":
    main()

