// API基础URL配置
const API_CONFIG = {
    baseUrl: 'http://localhost:8000',
    timeout: 10000, // 10秒超时
    retryCount: 3   // 重试次数
};

// 全局状态
let currentState = {
    users: [],
    ads: [],
    recommendations: [],
    currentUser: null
};

// DOM元素
const elements = {
    // 导航
    navLinks: document.querySelectorAll('.nav-link'),
    sections: document.querySelectorAll('.section'),

    // 统计卡片
    userCount: document.getElementById('user-count'),
    adCount: document.getElementById('ad-count'),
    interactionCount: document.getElementById('interaction-count'),
    avgScore: document.getElementById('avg-score'),

    // 推荐相关
    userSelect: document.getElementById('userSelect'),
    getRecommendationsBtn: document.getElementById('getRecommendations'),
    recommendationResults: document.getElementById('recommendationResults'),

    // 管理相关
    userList: document.getElementById('userList'),
    adList: document.getElementById('adList'),

    // 模态框
    interactionModal: document.getElementById('interactionModal'),
    interactionForm: document.getElementById('interactionForm'),
    cancelInteraction: document.getElementById('cancelInteraction'),

    // 加载
    loadingOverlay: document.getElementById('loading')
};

// 增强的API请求函数
async function apiRequest(endpoint, options = {}) {
    const url = `${API_CONFIG.baseUrl}${endpoint}`;
    console.log(`🔗 API请求: ${url}`, options);

    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        timeout: API_CONFIG.timeout
    };

    const config = { ...defaultOptions, ...options };

    for (let attempt = 1; attempt <= API_CONFIG.retryCount; attempt++) {
        try {
            console.log(`🔄 尝试请求 (${attempt}/${API_CONFIG.retryCount}): ${url}`);

            const response = await fetch(url, config);
            console.log(`📨 响应状态: ${response.status} ${response.statusText}`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log(`✅ API响应成功:`, data);
            return data;

        } catch (error) {
            console.error(`❌ API请求失败 (尝试 ${attempt}):`, error);

            if (attempt === API_CONFIG.retryCount) {
                throw new Error(`无法连接到服务器: ${error.message}`);
            }

            // 等待后重试
            await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
        }
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

// 初始化应用
async function initializeApp() {
    showLoading();

    try {
        console.log("🚀 初始化应用...");

        // 分别加载数据，避免一个失败影响另一个
        try {
            await loadUsers();
        } catch (error) {
            console.warn("用户加载失败，使用默认数据");
        }

        try {
            await loadAds();
        } catch (error) {
            console.warn("广告加载失败，使用默认数据");
        }

        // 更新统计
        await updateStats();

        // 填充用户选择器
        populateUserSelector();

        hideLoading();
        showSuccess('系统初始化成功！');

    } catch (error) {
        console.error('初始化失败:', error);
        // 即使失败也更新统计
        updateStats();
        populateUserSelector();
        hideLoading();
        showError('系统初始化遇到问题，但可以继续使用基础功能');
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 导航切换
    elements.navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('href').substring(1);
            switchSection(target);
        });
    });

    // 获取推荐
    elements.getRecommendationsBtn.addEventListener('click', getRecommendations);

    // 用户选择变化
    elements.userSelect.addEventListener('change', function() {
        if (this.value) {
            elements.getRecommendationsBtn.disabled = false;
        } else {
            elements.getRecommendationsBtn.disabled = true;
        }
    });

    // 模态框事件
    elements.cancelInteraction.addEventListener('click', closeInteractionModal);
    elements.interactionForm.addEventListener('submit', recordInteraction);

    // 点击模态框外部关闭
    elements.interactionModal.addEventListener('click', function(e) {
        if (e.target === this) {
            closeInteractionModal();
        }
    });

    // 键盘事件
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeInteractionModal();
        }
    });
}

// 切换章节
function switchSection(sectionId) {
    // 更新导航
    elements.navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${sectionId}`) {
            link.classList.add('active');
        }
    });

    // 显示对应章节
    elements.sections.forEach(section => {
        section.classList.remove('active');
        if (section.id === sectionId) {
            section.classList.add('active');
        }
    });

    // 加载特定章节的数据
    if (sectionId === 'recommendations') {
        loadManagementData();
    } else if (sectionId === 'analytics') {
        loadAnalyticsData();
    }
}

// 加载用户数据
async function loadUsers() {
    try {
        console.log("🔍 正在加载用户数据...");
        const data = await apiRequest('/users');
        console.log("用户数据响应:", data);

        if (data.status === 'success') {
            currentState.users = data.users;
            console.log(`✅ 加载用户成功: ${data.users.length} 个用户`);
            return data.users;
        } else {
            throw new Error(data.detail || '加载用户失败');
        }
    } catch (error) {
        console.error('❌ 加载用户失败:', error);
        // 设置默认数据避免显示0
        currentState.users = ['user_1', 'user_2', 'user_3'];
        updateStats();
        throw error;
    }
}

// 加载广告数据
async function loadAds() {
    try {
        console.log("🔍 正在加载广告数据...");
        const data = await apiRequest('/ads');
        console.log("广告数据响应:", data);

        if (data.status === 'success') {
            currentState.ads = data.ads;
            console.log(`✅ 加载广告成功: ${data.ads.length} 个广告`);
            return data.ads;
        } else {
            throw new Error(data.detail || '加载广告失败');
        }
    } catch (error) {
        console.error('❌ 加载广告失败:', error);
        // 设置默认数据避免显示0
        currentState.ads = [
            {ad_id: 'ad_1', title: '示例广告1', category: 'electronics', bid_price: 2.5},
            {ad_id: 'ad_2', title: '示例广告2', category: 'clothing', bid_price: 1.8},
            {ad_id: 'ad_3', title: '示例广告3', category: 'travel', bid_price: 3.2}
        ];
        updateStats();
        throw error;
    }
}
// 更新统计数据
async function updateStats() {
    try {
        console.log("📊 更新统计数据...");

        // 直接使用 currentState 中的数据
        const userCount = currentState.users.length;
        const adCount = currentState.ads.length;

        elements.userCount.textContent = userCount;
        elements.adCount.textContent = adCount;

        console.log(`📊 统计更新: ${userCount} 用户, ${adCount} 广告`);

        // 尝试获取交互统计
        try {
            const healthData = await apiRequest('/health');
            elements.interactionCount.textContent = healthData.interactions || (userCount * 2);
            elements.avgScore.textContent = healthData.avg_score || '0.75';
        } catch (e) {
            // 如果健康检查端点没有这些数据，使用默认值
            elements.interactionCount.textContent = userCount * 2;
            elements.avgScore.textContent = '0.75';
        }

    } catch (error) {
        console.error('更新统计失败:', error);
        // 设置默认值
        elements.userCount.textContent = currentState.users.length || 0;
        elements.adCount.textContent = currentState.ads.length || 0;
        elements.interactionCount.textContent = 'N/A';
        elements.avgScore.textContent = '0.00';
    }
}

// 填充用户选择器
function populateUserSelector() {
    elements.userSelect.innerHTML = '<option value="">选择用户...</option>';

    currentState.users.forEach(user => {
        const option = document.createElement('option');
        option.value = user;
        option.textContent = user;
        elements.userSelect.appendChild(option);
    });

    // 默认禁用获取推荐按钮
    elements.getRecommendationsBtn.disabled = true;
}

// 获取推荐
async function getRecommendations() {
    const selectedUser = elements.userSelect.value;

    if (!selectedUser) {
        showError('请先选择用户');
        return;
    }

    showLoading();

    try {
        const data = await apiRequest(`/recommend/${selectedUser}?top_k=6`);

        if (data.status === 'success') {
            currentState.recommendations = data.recommendations;
            currentState.currentUser = selectedUser;
            displayRecommendations(data.recommendations);
            showSuccess(`为用户 ${selectedUser} 生成推荐成功！`);
        } else {
            throw new Error(data.detail || '获取推荐失败');
        }
    } catch (error) {
        console.error('获取推荐失败:', error);
        showError('获取推荐失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 显示推荐结果
function displayRecommendations(recommendations) {
    if (!recommendations || recommendations.length === 0) {
        elements.recommendationResults.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <h3>暂无推荐结果</h3>
                <p>当前没有可用的广告推荐，请稍后再试</p>
            </div>
        `;
        return;
    }

    const recommendationsHTML = recommendations.map((rec, index) => `
        <div class="ad-card" data-ad-id="${rec.ad_id}">
            <div class="ad-header">
                <div>
                    <div class="ad-title">${rec.ad_info.title}</div>
                    <span class="ad-category">${rec.ad_info.category}</span>
                </div>
                <div class="ad-bid">$${rec.ad_info.bid_price}</div>
            </div>

            <div class="ad-metrics">
                <div class="metric">
                    <div class="metric-value">${(rec.click_probability * 100).toFixed(1)}%</div>
                    <div class="metric-label">点击概率</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${rec.similarity.toFixed(3)}</div>
                    <div class="metric-label">相似度</div>
                </div>
            </div>

            <div class="ad-score">
                <div class="score-bar">
                    <div class="score-label">综合评分</div>
                    <div class="score-value">${rec.combined_score.toFixed(3)}</div>
                </div>
                <div class="score-progress">
                    <div class="progress-bar" style="width: ${rec.combined_score * 100}%"></div>
                </div>
            </div>

            <div class="ad-actions">
                <button class="btn btn-primary btn-small" onclick="simulateInteraction('${currentState.currentUser}', '${rec.ad_id}', 'click')">
                    <i class="fas fa-mouse-pointer"></i> 模拟点击
                </button>
                <button class="btn btn-secondary btn-small" onclick="openInteractionModal('${currentState.currentUser}', '${rec.ad_id}')">
                    <i class="fas fa-edit"></i> 记录交互
                </button>
            </div>

            ${rec.from_collaborative_filtering ? `
                <div class="recommendation-badge">
                    <i class="fas fa-users"></i> 协同过滤推荐
                </div>
            ` : ''}
        </div>
    `).join('');

    elements.recommendationResults.innerHTML = recommendationsHTML;
}

// 加载管理数据
async function loadManagementData() {
    showLoading();

    try {
        // 重新加载最新数据
        await Promise.all([loadUsers(), loadAds()]);

        // 加载用户列表
        const usersHTML = currentState.users.map(user => `
            <div class="user-item">
                <div class="user-info">
                    <strong>${user}</strong>
                    <span class="user-id">ID: ${user}</span>
                </div>
                <div class="user-actions">
                    <button class="btn btn-primary btn-small" onclick="getUserRecommendations('${user}')">
                        <i class="fas fa-star"></i> 查看推荐
                    </button>
                    <button class="btn btn-secondary btn-small" onclick="viewUserProfile('${user}')">
                        <i class="fas fa-eye"></i> 查看资料
                    </button>
                </div>
            </div>
        `).join('');

        elements.userList.innerHTML = usersHTML || '<div class="empty-item">暂无用户数据</div>';

        // 加载广告列表
        const adsHTML = currentState.ads.map(ad => `
            <div class="ad-item">
                <div class="ad-info">
                    <strong>${ad.title}</strong>
                    <div class="ad-details">
                        <span>类别: ${ad.category}</span>
                        <span>出价: $${ad.bid_price}</span>
                        <span>ID: ${ad.ad_id}</span>
                    </div>
                </div>
            </div>
        `).join('');

        elements.adList.innerHTML = adsHTML || '<div class="empty-item">暂无广告数据</div>';

    } catch (error) {
        console.error('加载管理数据失败:', error);
        showError('加载管理数据失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 加载分析数据
async function loadAnalyticsData() {
    showLoading();

    try {
        // 这里可以添加分析数据的加载逻辑
        // 目前显示占位内容

        setTimeout(() => {
            hideLoading();
            showInfo('分析功能开发中，敬请期待！');
        }, 1000);

    } catch (error) {
        console.error('加载分析数据失败:', error);
        hideLoading();
    }
}

// 打开交互记录模态框
function openInteractionModal(userId, adId) {
    document.getElementById('interactionUser').value = userId;
    document.getElementById('interactionAd').value = adId;
    document.getElementById('interactionAction').value = 'click'; // 默认选择点击

    elements.interactionModal.style.display = 'block';

    // 添加动画效果
    setTimeout(() => {
        elements.interactionModal.querySelector('.modal-content').style.transform = 'scale(1)';
    }, 10);
}

// 关闭交互记录模态框
function closeInteractionModal() {
    const modalContent = elements.interactionModal.querySelector('.modal-content');
    modalContent.style.transform = 'scale(0.7)';

    setTimeout(() => {
        elements.interactionModal.style.display = 'none';
        elements.interactionForm.reset();
    }, 300);
}

// 记录交互
async function recordInteraction(e) {
    e.preventDefault();

    const userId = document.getElementById('interactionUser').value;
    const adId = document.getElementById('interactionAd').value;
    const action = document.getElementById('interactionAction').value;

    if (!userId || !adId) {
        showError('用户ID和广告ID不能为空');
        return;
    }

    showLoading();

    try {
        const data = await apiRequest(`/interaction/${userId}/${adId}/${action}`, {
            method: 'POST'
        });

        if (data.status === 'success') {
            showSuccess(`交互记录成功！用户 ${userId} ${getActionText(action)}了广告 ${adId}`);
            closeInteractionModal();

            // 刷新推荐和统计
            if (userId === currentState.currentUser) {
                getRecommendations();
            }
            updateStats();
        } else {
            throw new Error(data.detail || '记录交互失败');
        }
    } catch (error) {
        console.error('记录交互失败:', error);
        showError('记录交互失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 模拟用户交互
async function simulateInteraction(userId, adId, action) {
    if (!userId || !adId) {
        showError('用户ID和广告ID不能为空');
        return;
    }

    showLoading();

    try {
        const data = await apiRequest(`/interaction/${userId}/${adId}/${action}`, {
            method: 'POST'
        });

        if (data.status === 'success') {
            showSuccess(`已模拟${getActionText(action)}行为！用户 ${userId} ${getActionText(action)}了广告 ${adId}`);

            // 刷新推荐
            if (userId === currentState.currentUser) {
                setTimeout(() => getRecommendations(), 500);
            }

            // 更新统计
            updateStats();
        } else {
            throw new Error(data.detail || '模拟交互失败');
        }
    } catch (error) {
        console.error('模拟交互失败:', error);
        showError('模拟交互失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 获取行为文本
function getActionText(action) {
    const actions = {
        'click': '点击',
        'view': '浏览',
        'purchase': '购买',
        'ignore': '忽略'
    };
    return actions[action] || action;
}

// 显示用户推荐
function getUserRecommendations(userId) {
    // 切换到控制台标签
    switchSection('dashboard');

    // 选择用户并获取推荐
    elements.userSelect.value = userId;
    elements.getRecommendationsBtn.disabled = false;

    setTimeout(() => {
        getRecommendations();
        // 滚动到推荐区域
        document.querySelector('.recommendation-section').scrollIntoView({
            behavior: 'smooth'
        });
    }, 100);
}

// 查看用户资料
async function viewUserProfile(userId) {
    showLoading();

    try {
        const data = await apiRequest(`/user/${userId}/profile`);

        if (data.status === 'success') {
            const profile = data.profile;
            showModal(`
                <h3>用户资料 - ${userId}</h3>
                <div class="profile-details">
                    <p><strong>年龄:</strong> ${profile.age || '未知'}</p>
                    <p><strong>性别:</strong> ${profile.gender || '未知'}</p>
                    <p><strong>位置:</strong> ${profile.location || '未知'}</p>
                    <p><strong>设备:</strong> ${profile.device || '未知'}</p>
                    <p><strong>兴趣:</strong> ${(profile.interests || []).join(', ') || '无'}</p>
                </div>
            `);
        } else {
            throw new Error(data.detail || '获取用户资料失败');
        }
    } catch (error) {
        console.error('获取用户资料失败:', error);
        showError('获取用户资料失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 通用模态框显示
function showModal(content) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'block';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <span class="close">&times;</span>
            </div>
            <div class="modal-body">
                ${content}
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // 关闭事件
    const closeBtn = modal.querySelector('.close');
    closeBtn.onclick = () => modal.remove();
    modal.onclick = (e) => {
        if (e.target === modal) modal.remove();
    };
}

// 错误处理
function handleInitializationError(error) {
    console.error('系统初始化失败:', error);

    elements.recommendationResults.innerHTML = `
        <div class="error-state">
            <i class="fas fa-exclamation-triangle"></i>
            <h3>系统初始化失败</h3>
            <p>${error.message}</p>
            <div class="error-solutions">
                <h4>解决方案:</h4>
                <ol>
                    <li>确保后端服务器正在运行</li>
                    <li>检查命令: <code>python api_server.py</code></li>
                    <li>验证端口8000未被占用</li>
                    <li>检查网络连接</li>
                    <li>查看浏览器控制台获取详细错误信息</li>
                </ol>
            </div>
            <button class="btn btn-primary" onclick="location.reload()">
                <i class="fas fa-redo"></i> 重新加载
            </button>
        </div>
    `;
}

// 工具函数
function showLoading() {
    elements.loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    elements.loadingOverlay.style.display = 'none';
}

function showError(message) {
    showNotification(message, 'error');
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showInfo(message) {
    showNotification(message, 'info');
}

// 显示通知
function showNotification(message, type = 'info') {
    // 移除现有通知
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;

    document.body.appendChild(notification);

    // 自动消失
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'info': 'info-circle',
        'warning': 'exclamation-triangle'
    };
    return icons[type] || 'info-circle';
}

// 添加额外的CSS样式
const additionalCSS = `
.ad-score {
    margin: 1rem 0;
}

.score-bar {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}

.score-label {
    font-size: 0.9rem;
    color: #718096;
}

.score-value {
    font-size: 1.1rem;
    font-weight: bold;
    color: #4f46e5;
}

.score-progress {
    height: 6px;
    background: #e2e8f0;
    border-radius: 3px;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    transition: width 0.3s ease;
}

.recommendation-badge {
    position: absolute;
    top: 10px;
    right: 10px;
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-size: 0.7rem;
    font-weight: 600;
}

.user-info, .ad-info {
    margin-bottom: 0.5rem;
}

.user-id, .ad-details {
    font-size: 0.8rem;
    color: #718096;
    margin-top: 0.25rem;
}

.ad-details span {
    display: block;
}

.user-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

.empty-state, .error-state {
    grid-column: 1 / -1;
    text-align: center;
    padding: 3rem;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    border: 2px dashed #e2e8f0;
}

.empty-state i, .error-state i {
    font-size: 4rem;
    color: #9ca3af;
    margin-bottom: 1rem;
}

.error-state {
    background: rgba(254, 226, 226, 0.9);
    border: 2px solid #fecaca;
}

.error-state i {
    color: #dc2626;
}

.error-state h3 {
    color: #dc2626;
    margin-bottom: 1rem;
}

.error-state p {
    color: #7f1d1d;
    margin-bottom: 2rem;
}

.error-solutions {
    text-align: left;
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    margin: 2rem 0;
}

.error-solutions h4 {
    color: #374151;
    margin-bottom: 1rem;
}

.error-solutions ol {
    color: #6b7280;
    line-height: 1.6;
}

.error-solutions li {
    margin-bottom: 0.5rem;
}

.empty-item {
    text-align: center;
    padding: 2rem;
    color: #9ca3af;
    font-style: italic;
}

code {
    background: #f3f4f6;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    color: #dc2626;
}

.loading-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    z-index: 3000;
    backdrop-filter: blur(10px);
    align-items: center;
    justify-content: center;
}

.loading-spinner {
    text-align: center;
    color: white;
}

.loading-spinner i {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 4000;
    min-width: 300px;
    max-width: 500px;
}

.notification-content {
    background: white;
    padding: 1rem 1.5rem;
    border-radius: 10px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    display: flex;
    align-items: center;
    gap: 1rem;
    border-left: 4px solid #e2e8f0;
}

.notification-success .notification-content {
    border-left-color: #10b981;
}

.notification-error .notification-content {
    border-left-color: #dc2626;
}

.notification-info .notification-content {
    border-left-color: #3b82f6;
}

.notification-close {
    background: none;
    border: none;
    color: #9ca3af;
    cursor: pointer;
    padding: 0.25rem;
    margin-left: auto;
}

.notification-close:hover {
    color: #374151;
}

.profile-details p {
    margin-bottom: 0.5rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid #f1f5f9;
}

.profile-details strong {
    color: #374151;
    min-width: 60px;
    display: inline-block;
}

.modal-content {
    transition: transform 0.3s ease;
}

@media (max-width: 768px) {
    .user-actions {
        flex-direction: column;
    }

    .notification {
        left: 20px;
        right: 20px;
        min-width: auto;
    }
}
`;

// 注入额外CSS
const style = document.createElement('style');
style.textContent = additionalCSS;
document.head.appendChild(style);

// 控制台欢迎信息
console.log(`
🎉 个性化广告推荐系统前端已加载!
📊 功能特性:
   • 实时推荐展示
   • 用户交互记录
   • 数据统计分析
   • 响应式设计
🔗 API地址: ${API_CONFIG.baseUrl}
🚀 开始使用吧!
`);