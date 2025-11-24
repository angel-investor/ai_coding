"""
Flask 预测 API
提供心血管疾病预测接口
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import setup_logger

# 设置日志
logger = setup_logger('api', log_dir='./logs')

# 创建 Flask 应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局变量
model = None
scaler = None
feature_names = None


def load_model():
    """加载模型和预处理器"""
    global model, scaler, feature_names
    
    try:
        model_dir = './model'
        
        # 加载模型
        model_path = os.path.join(model_dir, 'xgb_model.pkl')
        model = joblib.load(model_path)
        logger.info(f"模型加载成功: {model_path}")
        
        # 加载标准化器
        scaler_path = os.path.join(model_dir, 'scaler.pkl')
        scaler = joblib.load(scaler_path)
        logger.info(f"标准化器加载成功: {scaler_path}")
        
        # 加载特征名
        features_path = os.path.join(model_dir, 'feature_names.pkl')
        feature_names = joblib.load(features_path)
        logger.info(f"特征名加载成功，共 {len(feature_names)} 个特征")
        
        return True
        
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        return False


@app.route('/')
def home():
    """系统首页"""
    web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web')
    return send_from_directory(web_dir, 'home.html')


@app.route('/api')
def api_info():
    """API 信息"""
    return jsonify({
        'message': '心血管疾病预测 API',
        'version': '1.0.0',
        'endpoints': {
            'predict': '/predict',
            'health': '/health',
            'features': '/features',
            'qa_audio': '/qa_audio'
        }
    })


@app.route('/health')
def health():
    """健康检查"""
    status = 'ok' if model is not None else 'error'
    return jsonify({
        'status': status,
        'model_loaded': model is not None,
        'scaler_loaded': scaler is not None,
        'features_count': len(feature_names) if feature_names else 0
    })


@app.route('/features')
def get_features():
    """获取特征列表"""
    if feature_names is None:
        return jsonify({'error': '模型未加载'}), 500
    
    return jsonify({
        'features': feature_names,
        'count': len(feature_names)
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    预测接口
    
    请求体示例:
    {
        "age": 50,
        "gender": 2,
        "height": 170,
        "weight": 70,
        "ap_hi": 120,
        "ap_lo": 80,
        "cholesterol": 1,
        "gluc": 1,
        "smoke": 0,
        "alco": 0,
        "active": 1
    }
    
    返回示例:
    {
        "success": true,
        "prediction": 0,
        "probability": {
            "healthy": 0.85,
            "disease": 0.15
        },
        "risk_level": "低风险",
        "message": "预测成功"
    }
    """
    try:
        # 检查模型是否加载
        if model is None or scaler is None or feature_names is None:
            logger.error("模型未加载")
            return jsonify({
                'success': False,
                'error': '模型未加载，请先训练模型'
            }), 500
        
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            logger.warning("请求数据为空")
            return jsonify({
                'success': False,
                'error': '请提供输入数据'
            }), 400
        
        logger.info(f"收到预测请求: {data}")
        
        # 验证必需字段
        missing_features = [f for f in feature_names if f not in data]
        if missing_features:
            logger.warning(f"缺少特征: {missing_features}")
            return jsonify({
                'success': False,
                'error': f'缺少必需特征: {missing_features}'
            }), 400
        
        # 构建特征向量
        features = []
        for feature in feature_names:
            value = data.get(feature)
            if value is None:
                logger.warning(f"特征 {feature} 为 None")
                return jsonify({
                    'success': False,
                    'error': f'特征 {feature} 不能为空'
                }), 400
            features.append(float(value))
        
        # 转换为 numpy 数组
        X = np.array([features])
        
        # 标准化
        X_scaled = scaler.transform(X)
        
        # 预测
        prediction = int(model.predict(X_scaled)[0])
        probability = model.predict_proba(X_scaled)[0]
        
        # 确定风险等级
        disease_prob = float(probability[1])
        if disease_prob < 0.3:
            risk_level = '低风险'
        elif disease_prob < 0.6:
            risk_level = '中风险'
        else:
            risk_level = '高风险'
        
        # 构建响应
        result = {
            'success': True,
            'prediction': prediction,
            'prediction_label': '患病' if prediction == 1 else '健康',
            'probability': {
                'healthy': float(probability[0]),
                'disease': float(probability[1])
            },
            'risk_level': risk_level,
            'message': '预测成功'
        }
        
        logger.info(f"预测结果: {result}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"预测失败: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'预测失败: {str(e)}'
        }), 500


@app.route('/qa_audio', methods=['POST'])
def qa_audio():
    """
    语音问答接口
    
    请求体:
    {
        "question": "如何预防心血管疾病？"
    }
    
    返回:
    {
        "success": true,
        "text": "回答内容",
        "audio_url": "/static/audio/xxx.wav"
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data or 'question' not in data:
            logger.warning("请求数据缺少 question 字段")
            return jsonify({
                'success': False,
                'error': '请提供问题（question 字段）'
            }), 400
        
        question = data['question'].strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': '问题不能为空'
            }), 400
        
        logger.info(f"收到语音问答请求: {question[:50]}...")
        
        # 导入语音问答模块
        from audio.qa_audio import qa_pipeline
        
        # 执行问答流程
        result = qa_pipeline(question)
        
        if result['success']:
            response = {
                'success': True,
                'text': result['text'],
                'audio_url': result['audio_url']
            }
            
            if result.get('error'):
                response['warning'] = result['error']
            
            logger.info("语音问答成功")
            return jsonify(response)
        else:
            logger.error(f"语音问答失败: {result.get('error')}")
            return jsonify({
                'success': False,
                'error': result.get('error', '处理失败')
            }), 500
            
    except Exception as e:
        logger.error(f"语音问答接口错误: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    """提供音频文件"""
    audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'audio')
    return send_from_directory(audio_dir, filename)


@app.route('/analysis/<path:filename>')
def serve_analysis(filename):
    """提供分析报告文件"""
    analysis_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'analysis')
    return send_from_directory(analysis_dir, filename)


@app.route('/web/<path:filename>')
def serve_web(filename):
    """提供静态网页文件"""
    web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web')
    return send_from_directory(web_dir, filename)


def create_app():
    """创建并配置应用"""
    # 加载模型
    if not load_model():
        logger.warning("模型加载失败，API 功能受限")
    
    return app


if __name__ == '__main__':
    # 创建应用
    app = create_app()
    
    # 启动服务器
    logger.info("=" * 50)
    logger.info("启动 Flask 服务器")
    logger.info("=" * 50)
    logger.info("主机: 0.0.0.0")
    logger.info("端口: 5000")
    logger.info("=" * 50)
    
    print("\n" + "=" * 60)
    print("🚀 Flask 服务器启动成功")
    print("=" * 60)
    print("访问地址:")
    print("  🏠 系统首页: http://localhost:5000/")
    print("  🔬 疾病预测: http://localhost:5000/web/predict.html")
    print("  🎙️ 语音问答: http://localhost:5000/web/qa_audio.html")
    print("  📊 数据分析: http://localhost:5000/analysis/report.html")
    print("  💚 健康检查: http://localhost:5000/health")
    print("=" * 60)
    print("API 接口:")
    print("  POST /predict    - 疾病预测接口")
    print("  POST /qa_audio   - 语音问答接口")
    print("  GET  /features   - 获取特征列表")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

