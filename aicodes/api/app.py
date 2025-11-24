"""
Flask 应用主文件
提供 RESTful API 接口
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.model_predictor import ModelPredictor
from audio.deepseek_client import DeepSeekClient
from audio.cosyvoice_client import CosyVoiceClient
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger('api')


def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__)
    CORS(app)
    
    # 加载配置
    config = Config()
    
    # 初始化模型预测器
    predictor = ModelPredictor(config.MODEL_DIR)
    try:
        predictor.load_model()
        logger.info("模型加载成功")
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
    
    # 初始化 DeepSeek 客户端
    deepseek_client = DeepSeekClient(
        api_key=config.DEEPSEEK_API_KEY,
        api_url=config.DEEPSEEK_API_URL
    )
    
    # 初始化 CosyVoice 客户端
    cosyvoice_client = CosyVoiceClient(
        appkey=config.COSYVOICE_APPKEY,
        token=config.COSYVOICE_TOKEN
    )
    
    @app.route('/')
    def index():
        """首页"""
        return jsonify({
            'message': '心血管疾病预测 API',
            'version': '1.0.0',
            'endpoints': {
                'predict': '/api/predict',
                'chat': '/api/chat',
                'voice': '/api/voice',
                'model_info': '/api/model/info',
                'health_advice': '/api/health/advice'
            }
        })
    
    @app.route('/api/predict', methods=['POST'])
    def predict():
        """
        预测接口
        接收特征数据，返回预测结果
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': '请提供输入数据'}), 400
            
            # 进行预测
            result = predictor.predict(data)
            
            logger.info(f"预测成功: {result}")
            return jsonify({
                'success': True,
                'data': result
            })
            
        except Exception as e:
            logger.error(f"预测接口错误: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        """
        文本问答接口
        使用 DeepSeek API 回答问题
        """
        try:
            data = request.get_json()
            question = data.get('question', '')
            
            if not question:
                return jsonify({'error': '请提供问题'}), 400
            
            # 调用 DeepSeek API
            answer = deepseek_client.ask_question(question)
            
            logger.info(f"问答成功: {question[:50]}...")
            return jsonify({
                'success': True,
                'question': question,
                'answer': answer
            })
            
        except Exception as e:
            logger.error(f"问答接口错误: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/voice', methods=['POST'])
    def voice():
        """
        语音问答接口
        接收问题，返回文本答案和语音文件
        """
        try:
            data = request.get_json()
            question = data.get('question', '')
            
            if not question:
                return jsonify({'error': '请提供问题'}), 400
            
            # 1. 使用 DeepSeek 生成文本答案
            answer = deepseek_client.ask_question(question)
            
            # 2. 使用 CosyVoice 生成语音
            audio_path = cosyvoice_client.text_to_speech(answer)
            
            if audio_path is None:
                logger.warning("语音合成失败，仅返回文本")
                return jsonify({
                    'success': True,
                    'question': question,
                    'answer': answer,
                    'audio_url': None
                })
            
            # 生成音频访问URL
            audio_filename = os.path.basename(audio_path)
            audio_url = f'/api/audio/{audio_filename}'
            
            logger.info(f"语音问答成功: {question[:50]}...")
            return jsonify({
                'success': True,
                'question': question,
                'answer': answer,
                'audio_url': audio_url
            })
            
        except Exception as e:
            logger.error(f"语音问答接口错误: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/health/advice', methods=['POST'])
    def health_advice():
        """
        健康建议接口
        根据用户数据和预测结果生成健康建议
        """
        try:
            data = request.get_json()
            user_data = data.get('user_data', {})
            
            if not user_data:
                return jsonify({'error': '请提供用户数据'}), 400
            
            # 先进行预测
            prediction_result = predictor.predict(user_data)
            
            # 生成健康建议
            advice = deepseek_client.generate_health_advice(
                user_data, 
                prediction_result
            )
            
            logger.info("健康建议生成成功")
            return jsonify({
                'success': True,
                'prediction': prediction_result,
                'advice': advice
            })
            
        except Exception as e:
            logger.error(f"健康建议接口错误: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/model/info', methods=['GET'])
    def model_info():
        """获取模型信息"""
        try:
            feature_names = predictor.get_feature_names()
            
            info = {
                'model_type': 'XGBoost Classifier',
                'feature_count': len(feature_names),
                'feature_names': feature_names
            }
            
            return jsonify({
                'success': True,
                'data': info
            })
            
        except Exception as e:
            logger.error(f"获取模型信息错误: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/audio/<filename>')
    def serve_audio(filename):
        """提供音频文件"""
        audio_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'audio', 
            'output'
        )
        return send_from_directory(audio_dir, filename)
    
    @app.route('/web')
    @app.route('/web/')
    def serve_index():
        """提供主页"""
        web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web')
        return send_from_directory(web_dir, 'index.html')
    
    @app.route('/web/<path:filename>')
    def serve_web(filename):
        """提供静态网页文件"""
        web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web')
        return send_from_directory(web_dir, filename)
    
    return app


if __name__ == '__main__':
    app = create_app()
    config = Config()
    
    logger.info(f"启动服务器: {config.FLASK_HOST}:{config.FLASK_PORT}")
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )
