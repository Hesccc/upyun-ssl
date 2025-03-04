// 主题切换功能
function setTheme(theme) {
    if (theme === 'system') {
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', systemDark ? 'dark' : 'light');
        localStorage.removeItem('theme');
        watchSystemTheme();
    } else {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', systemThemeHandler);
    }
}

function watchSystemTheme() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', systemThemeHandler);
}

function systemThemeHandler(e) {
    document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
}

// 初始化主题
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        setTheme(savedTheme);
    } else {
        setTheme('system');
        watchSystemTheme();
    }
}

// 表单验证
function validateForm() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    let isValid = true;

    document.querySelectorAll('.error').forEach(el => el.textContent = '');

    if (!username) {
        document.getElementById('usernameError').textContent = '用户名不能为空';
        isValid = false;
    }

    if (!password) {
        document.getElementById('passwordError').textContent = '密码不能为空';
        isValid = false;
    }

    return isValid;
}

// 初始化
initTheme();