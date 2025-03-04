// 主题管理
function setTheme(theme) {
    const buttons = document.querySelectorAll('.theme-btn');
    buttons.forEach(btn => btn.classList.remove('active'));

    if (theme === 'system') {
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', systemDark ? 'dark' : 'light');
        localStorage.removeItem('theme');
        watchSystemTheme();
        document.querySelector('[onclick="setTheme(\'system\')"]').classList.add('active');
    } else {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', systemThemeHandler);
        document.querySelector(`[onclick="setTheme('${theme}')"]`).classList.add('active');
    }
}

function watchSystemTheme() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', systemThemeHandler);
}

function systemThemeHandler(e) {
    if (!localStorage.getItem('theme')) {
        document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
    }
}

// 运行日志
async function loadLogs() {
    try {
        const response = await fetch('/api/ShowLogs');
        const data = await response.json();
        const logContainer = document.querySelector('#log-content');

        // 检查数据格式
        console.log('日志数据:', data);

        // 清空现有内容
        logContainer.innerHTML = '';

        // 插入新的日志条目
        if (Array.isArray(data.logs)) {
            data.logs.forEach((log, index) => {
                const entry = document.createElement('div');
                entry.className = 'log-entry';
                entry.textContent = `第${index + 1}行: ${log}`; // 添加行号
                logContainer.appendChild(entry);
            });

            // 自动滚动到底部
            logContainer.scrollTop = logContainer.scrollHeight;
        } else {
            console.error('日志数据格式不正确:', data.logs);
        }
    } catch (error) {
        console.error('日志加载失败:', error);
    }
}

// 修改密码
async function loadChangepwd() {
    const form = document.getElementById('change-pwd-form');
    form.addEventListener('submit', submitChangePwd);
}

// 修改密码
async function submitChangePwd(event) {
    event.preventDefault();
    clearErrors();

    const oldPwd = document.getElementById('old-pwd').value.trim();
    const newPwd = document.getElementById('new-pwd').value.trim();
    const confirmPwd = document.getElementById('confirm-pwd').value.trim();
    let isValid = true;

    if (!oldPwd) {
        document.getElementById('oldPwdError').textContent = '请输入当前密码';
        isValid = false;
    }

    if (!newPwd) {
        document.getElementById('newPwdError').textContent = '请输入新密码';
        isValid = false;
    }

    if (newPwd !== confirmPwd) {
        document.getElementById('confirmPwdError').textContent = '新密码和确认密码不匹配';
        isValid = false;
    }

    if (isValid) {
        try {
            const response = await fetch('/api/ChangePasswd', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ old_password: oldPwd, new_password: newPwd })
            });

            const result = await response.json();

            if (result.success) {
                document.getElementById('changePwdMsg').textContent = '密码修改成功！';
                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);
            } else {
                document.getElementById('changePwdMsg').textContent = result.message || '密码修改失败';
            }
        } catch (error) {
            console.error('密码修改请求失败:', error);
            document.getElementById('changePwdMsg').textContent = '请求失败，请稍后重试';
        }
    }
}

// 内容切换
function showContent(sectionId) {
    // 隐藏所有内容区域
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });

    // 显示选中的内容区域
    document.getElementById(sectionId).classList.add('active');

    // 当切换到日志页面时加载日志
    if (sectionId === 'logs') {
        loadLogs();
    } else if (sectionId === 'change-pwd') {
        loadChangepwd();
    } else if (sectionId === 'system-webhook') {
        loadWebhookInfo();
    }
}

// 表单验证
function submitCloudConfig(e) {
    e.preventDefault();
    clearErrors();

    const user = document.getElementById('cloud-user').value.trim();
    const pwd = document.getElementById('cloud-pwd').value.trim();
    let isValid = true;

    if (!user) {
        document.getElementById('userError').textContent = '请输入服务器账号';
        isValid = false;
    }

    if (!pwd) {
        document.getElementById('pwdError').textContent = '请输入服务器密码';
        isValid = false;
    }

    if (isValid) {
        // 提交逻辑
        console.log('提交配置:', { user, pwd });
        alert('配置保存成功！');
    }
    return false;
}

function clearErrors() {
    document.querySelectorAll('.error').forEach(el => {
        el.textContent = '';
    });
}

// Path: static/js/dashboard.js
// 主题初始化
function init() {
    const savedTheme = localStorage.getItem('theme') || 'system';
    setTheme(savedTheme);
    showContent('cloud-config');

    // 绑定修改密码表单提交事件
    const changePwdForm = document.querySelector('#change-pwd form');
    if (changePwdForm) {
        changePwdForm.addEventListener('submit', submitChangePwd);
    }

    // 加载 Webhook 信息
    loadWebhookInfo();
}

// Webhook 测试
function testWebhook() {
    const webhookUrl = document.getElementById('webhook-url').value;
    fetch(webhookUrl, {
        method: 'POST',
        headers: {
            'type': 'test',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ test: 'data' })
    })
    .then(response => response.json())
    .then(data => {
        alert('Webhook 测试成功: ' + JSON.stringify(data));
    })
    .catch(error => {
        alert('Webhook 测试失败: ' + error);
    });
}

// 获取 Webhook URL
async function loadWebhookInfo() {
    try {
        const response = await fetch('/api/WebhookInfo');
        const data = await response.json();
        console.log('Webhook 信息:', data);
        if (data.success) {
            document.getElementById('webhook-url').value = data.webhook_url;
        } else {
            console.error('获取 Webhook URL 失败:', data.message);
        }
    } catch (error) {
        console.error('请求 Webhook URL 失败:', error);
    }
}

init();