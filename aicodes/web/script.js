// API 基础 URL
const API_BASE_URL = 'http://localhost:5000/api';

// 标签切换
function showTab(tabName) {
    // 隐藏所有标签内容
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // 移除所有按钮的激活状态
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // 显示选中的标签
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
}

// 预测表单提交
document.getElementById('predict-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const resultCard = document.getElementById('result-card');
    const resultContent = document.getElementById('result-content');
    
    // 禁用提交按钮
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span> 预测中...';
    
    // 收集表单数据
    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = parseFloat(value);
    });
    
    try {
        // 发送预测请求
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayPredictionResult(result.data);
            resultCard.style.display = 'block';
            resultCard.scrollIntoView({ behavior: 'smooth' });
        } else {
            alert('预测失败: ' + (result.error || '未知错误'));
        }
    } catch (error) {
        console.error('预测错误:', error);
        alert('网络错误，请检查服务器是否运行');
    } finally {
        // 恢复提交按钮
        submitBtn.disabled = false;
        submitBtn.textContent = '开始预测';
    }
});

// 显示预测结果
function displayPredictionResult(data) {
    const resultContent = document.getElementById('result-content');
    const prediction = data.prediction;
    const probability = data.probability;
    const confidence = (data.confidence * 100).toFixed(2);
    
    const hasDisease = prediction === 1;
    const riskLevel = hasDisease ? probability.class_1 : probability.class_0;
    const riskPercent = (riskLevel * 100).toFixed(2);
    
    const resultClass = hasDisease ? 'result-positive' : 'result-negative';
    const resultIcon = hasDisease ? '⚠️' : '✅';
    const resultTitle = hasDisease ? '存在心血管疾病风险' : '心血管健康状况良好';
    
    resultContent.innerHTML = `
        <div class="${resultClass}">
            <div class="result-title">${resultIcon} ${resultTitle}</div>
            <div class="result-probability">
                风险概率: <strong>${riskPercent}%</strong>
            </div>
            <div class="result-probability">
                预测置信度: <strong>${confidence}%</strong>
            </div>
        </div>
        
        <div class="result-advice">
            <h3>健康建议</h3>
            ${hasDisease ? `
                <ul style="line-height: 1.8; margin-top: 10px;">
                    <li>建议尽快咨询专业心血管科医生</li>
                    <li>定期监测血压、血糖和胆固醇水平</li>
                    <li>保持健康的生活方式，适度运动</li>
                    <li>控制体重，保持健康饮食</li>
                    <li>戒烟限酒，减少压力</li>
                </ul>
            ` : `
                <ul style="line-height: 1.8; margin-top: 10px;">
                    <li>继续保持良好的生活习惯</li>
                    <li>定期进行健康体检</li>
                    <li>保持适度运动，每周至少150分钟</li>
                    <li>均衡饮食，多吃蔬菜水果</li>
                    <li>保持良好的心理状态</li>
                </ul>
            `}
            <p style="margin-top: 15px; color: #666; font-size: 0.9rem;">
                <strong>注意：</strong>本预测结果仅供参考，不能替代专业医疗诊断。
                如有身体不适，请及时就医。
            </p>
        </div>
    `;
}

// 聊天表单提交
document.getElementById('chat-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const input = document.getElementById('question-input');
    const question = input.value.trim();
    
    if (!question) return;
    
    // 显示用户消息
    addMessage(question, 'user');
    
    // 清空输入框
    input.value = '';
    
    // 禁用表单
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span>';
    
    try {
        // 发送问答请求
        const response = await fetch(`${API_BASE_URL}/voice`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });
        
        const result = await response.json();
        
        if (result.success) {
            addMessage(result.answer, 'bot', result.audio_url);
        } else {
            addMessage('抱歉，回答生成失败: ' + (result.error || '未知错误'), 'bot');
        }
    } catch (error) {
        console.error('问答错误:', error);
        addMessage('网络错误，请检查服务器是否运行', 'bot');
    } finally {
        // 恢复表单
        submitBtn.disabled = false;
        submitBtn.textContent = '发送';
    }
});

// 添加聊天消息
function addMessage(text, sender, audioUrl = null) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${sender}`;
    
    let content = `<div>${text}</div>`;
    
    // 如果有音频 URL，添加音频播放器
    if (audioUrl) {
        content += `
            <div class="audio-player">
                <audio controls style="width: 100%; margin-top: 10px;">
                    <source src="${audioUrl}" type="audio/mpeg">
                    您的浏览器不支持音频播放。
                </audio>
            </div>
        `;
    }
    
    messageDiv.innerHTML = content;
    messagesContainer.appendChild(messageDiv);
    
    // 滚动到底部
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('心血管疾病预测系统已加载');
    
    // 添加欢迎消息
    addMessage('您好！我是心血管健康助手，有什么可以帮助您的吗？', 'bot');
});

