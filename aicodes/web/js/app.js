// API 基础 URL
const API_BASE_URL = 'http://localhost:5000';

// 全局变量
let currentPrediction = null;
let currentUserData = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    initForms();
});

// 初始化标签页切换
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            
            // 移除所有活动状态
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // 添加当前活动状态
            this.classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');
        });
    });
}

// 初始化表单
function initForms() {
    // 预测表单
    document.getElementById('predict-form').addEventListener('submit', handlePredict);
    
    // 聊天表单
    document.getElementById('chat-form').addEventListener('submit', handleChat);
    
    // 语音表单
    document.getElementById('voice-form').addEventListener('submit', handleVoice);
}

// 处理预测
async function handlePredict(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {};
    
    formData.forEach((value, key) => {
        data[key] = parseFloat(value);
    });
    
    // 保存用户数据
    currentUserData = data;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentPrediction = result.data;
            displayPredictionResult(result.data);
        } else {
            alert('预测失败: ' + result.error);
        }
    } catch (error) {
        console.error('预测错误:', error);
        alert('预测失败，请检查服务器连接');
    }
}

// 显示预测结果
function displayPredictionResult(data) {
    const resultDiv = document.getElementById('predict-result');
    const contentDiv = document.getElementById('result-content');
    
    const prediction = data.prediction === 1 ? '有心血管疾病风险' : '无明显心血管疾病风险';
    const riskLevel = data.risk_level;
    const probPositive = (data.probability.positive * 100).toFixed(2);
    const probNegative = (data.probability.negative * 100).toFixed(2);
    
    let riskClass = 'risk-low';
    if (riskLevel === '中风险') riskClass = 'risk-medium';
    if (riskLevel === '高风险') riskClass = 'risk-high';
    
    contentDiv.innerHTML = `
        <div class="risk-level ${riskClass}">
            ${riskLevel}
        </div>
        <p style="text-align: center; font-size: 1.2em; margin: 15px 0;">
            <strong>预测结果:</strong> ${prediction}
        </p>
        <div class="probability">
            <div class="prob-item">
                <div class="prob-value">${probNegative}%</div>
                <div>健康概率</div>
            </div>
            <div class="prob-item">
                <div class="prob-value">${probPositive}%</div>
                <div>患病概率</div>
            </div>
        </div>
    `;
    
    resultDiv.style.display = 'block';
    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

// 获取健康建议
async function getHealthAdvice() {
    if (!currentUserData || !currentPrediction) {
        alert('请先进行预测');
        return;
    }
    
    const adviceDiv = document.getElementById('health-advice');
    const contentDiv = document.getElementById('advice-content');
    
    contentDiv.innerHTML = '<p>正在生成健康建议...</p>';
    adviceDiv.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/health/advice`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_data: currentUserData
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            contentDiv.innerHTML = `<p>${result.advice}</p>`;
        } else {
            contentDiv.innerHTML = `<p style="color: red;">生成建议失败: ${result.error}</p>`;
        }
    } catch (error) {
        console.error('获取健康建议错误:', error);
        contentDiv.innerHTML = '<p style="color: red;">获取建议失败，请检查服务器连接</p>';
    }
}

// 处理聊天
async function handleChat(e) {
    e.preventDefault();
    
    const input = document.getElementById('chat-input');
    const question = input.value.trim();
    
    if (!question) return;
    
    // 显示用户消息
    addMessage('user', question, 'chat-messages');
    input.value = '';
    
    // 显示加载中
    const loadingId = addMessage('assistant', '正在思考...', 'chat-messages');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });
        
        const result = await response.json();
        
        // 移除加载消息
        document.getElementById(loadingId).remove();
        
        if (result.success) {
            addMessage('assistant', result.answer, 'chat-messages');
        } else {
            addMessage('assistant', '抱歉，回答失败: ' + result.error, 'chat-messages');
        }
    } catch (error) {
        console.error('聊天错误:', error);
        document.getElementById(loadingId).remove();
        addMessage('assistant', '抱歉，服务器连接失败', 'chat-messages');
    }
}

// 处理语音问答
async function handleVoice(e) {
    e.preventDefault();
    
    const input = document.getElementById('voice-input');
    const question = input.value.trim();
    
    if (!question) return;
    
    // 显示用户消息
    addMessage('user', question, 'voice-messages');
    input.value = '';
    
    // 显示加载中
    const loadingId = addMessage('assistant', '正在生成回答和语音...', 'voice-messages');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/voice`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });
        
        const result = await response.json();
        
        // 移除加载消息
        document.getElementById(loadingId).remove();
        
        if (result.success) {
            // 添加文本回答
            addMessage('assistant', result.answer, 'voice-messages');
            
            // 添加音频播放器
            if (result.audio_url) {
                addAudioPlayer(result.audio_url, 'voice-messages');
            }
        } else {
            addMessage('assistant', '抱歉，回答失败: ' + result.error, 'voice-messages');
        }
    } catch (error) {
        console.error('语音问答错误:', error);
        document.getElementById(loadingId).remove();
        addMessage('assistant', '抱歉，服务器连接失败', 'voice-messages');
    }
}

// 添加消息
function addMessage(role, content, containerId) {
    const container = document.getElementById(containerId);
    const messageId = 'msg-' + Date.now();
    
    const messageDiv = document.createElement('div');
    messageDiv.id = messageId;
    messageDiv.className = `message ${role}`;
    
    const label = role === 'user' ? '您' : 'AI助手';
    messageDiv.innerHTML = `
        <div class="message-label">${label}</div>
        <div>${content}</div>
    `;
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
    
    return messageId;
}

// 添加音频播放器
function addAudioPlayer(audioUrl, containerId) {
    const container = document.getElementById(containerId);
    
    const playerDiv = document.createElement('div');
    playerDiv.className = 'audio-player';
    playerDiv.innerHTML = `
        <audio controls>
            <source src="${API_BASE_URL}${audioUrl}" type="audio/mpeg">
            您的浏览器不支持音频播放。
        </audio>
    `;
    
    container.appendChild(playerDiv);
    container.scrollTop = container.scrollHeight;
}

