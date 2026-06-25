const API = window.location.origin;
let tg = null;
let viewStack = [];
let categoriesCache = null;

function getTG() {
    if (tg) return tg;
    if (window.Telegram && window.Telegram.WebApp) {
        tg = window.Telegram.WebApp;
        tg.ready();
        tg.expand();
        tg.setHeaderColor('#0f0f13');
        tg.setBackgroundColor('#0f0f13');
        return tg;
    }
    return null;
}

function getUser() {
    const t = getTG();
    if (t && t.initDataUnsafe && t.initDataUnsafe.user) {
        return t.initDataUnsafe.user;
    }
    return { id: 0, username: 'Гость' };
}

function showView(id) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    const view = document.getElementById(id);
    if (view) {
        view.classList.remove('active');
        void view.offsetWidth;
        view.classList.add('active');
    }
    const backBtn = document.getElementById('backBtn');
    const title = document.getElementById('headerTitle');
    if (viewStack.length > 0) {
        backBtn.classList.remove('hidden');
    } else {
        backBtn.classList.add('hidden');
    }
    updateTitle();
}

function updateTitle() {
    const title = document.getElementById('headerTitle');
    const currentId = viewStack.length > 0 ? viewStack[viewStack.length - 1].view : 'homeView';
    const titles = { homeView: 'Кафе', productsView: '', variantsView: '', successView: 'Заказ' };
    title.textContent = titles[currentId] || 'Кафе';
    if (currentId === 'productsView' && viewStack.length > 0) {
        title.textContent = viewStack[viewStack.length - 1].data?.name || 'Меню';
    }
    if (currentId === 'variantsView' && viewStack.length > 0) {
        title.textContent = viewStack[viewStack.length - 1].data?.name || 'Выбор';
    }
}

function navigate(viewId, data) {
    viewStack.push({ view: viewId, data });
    showView(viewId);
}

function goBack() {
    if (viewStack.length > 0) {
        viewStack.pop();
    }
    if (viewStack.length > 0) {
        const prev = viewStack[viewStack.length - 1];
        showView(prev.view);
    } else {
        showView('homeView');
    }
}

function goHome() {
    viewStack = [];
    showView('homeView');
}

function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.remove('hidden');
    clearTimeout(t._timer);
    t._timer = setTimeout(() => t.classList.add('hidden'), 2500);
}

function showLoader() { document.getElementById('loader').classList.remove('hidden'); }
function hideLoader() { document.getElementById('loader').classList.add('hidden'); }

async function api(path) {
    try {
        const res = await fetch(API + path);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (e) {
        console.error(`API GET ${path} failed:`, e);
        throw e;
    }
}

async function apiPost(path, body) {
    try {
        const res = await fetch(API + path, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (e) {
        console.error(`API POST ${path} failed:`, e);
        throw e;
    }
}

function staggerChildren(container, delayStep = 50) {
    const children = container.children;
    for (let i = 0; i < children.length; i++) {
        children[i].style.opacity = '0';
        children[i].style.transform = 'translateY(12px)';
        setTimeout(() => {
            children[i].style.transition = 'opacity 0.35s ease, transform 0.35s cubic-bezier(0.22, 1, 0.36, 1)';
            children[i].style.opacity = '1';
            children[i].style.transform = 'translateY(0)';
        }, i * delayStep);
    }
}

async function loadCategories() {
    showLoader();
    try {
        const cats = categoriesCache || await api('/api/categories');
        if (!Array.isArray(cats)) throw new Error('Invalid response');
        categoriesCache = cats;
        const grid = document.getElementById('categoriesGrid');
        grid.innerHTML = '';
        cats.forEach(cat => {
            const card = document.createElement('div');
            card.className = 'category-card';
            card.onclick = () => loadProducts(cat);
            card.innerHTML = `
                <span class="category-emoji">${cat.emoji}</span>
                <div class="category-name">${cat.name}</div>
            `;
            grid.appendChild(card);
        });
        staggerChildren(grid, 60);
    } catch (e) {
        console.error('loadCategories error:', e);
        showToast('Сервер недоступен. Запустите python run.py server');
    }
    hideLoader();
}

async function loadProducts(category) {
    showLoader();
    try {
        const products = await api(`/api/products/${category.id}`);
        navigate('productsView', category);
        const list = document.getElementById('productsList');
        document.getElementById('categoryTitle').textContent = `${category.emoji} ${category.name}`;
        list.innerHTML = '';
        products.forEach((p, i) => {
            const card = document.createElement('div');
            card.className = 'product-card';
            card.onclick = () => loadVariants(p, category);
            card.innerHTML = `
                <div class="product-icon">${category.emoji}</div>
                <div class="product-info">
                    <div class="product-name">${p.name}</div>
                    <div class="product-desc">${p.description}</div>
                </div>
                <div class="product-arrow">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
                </div>
            `;
            list.appendChild(card);
        });
        staggerChildren(list, 50);
    } catch (e) {
        showToast('Ошибка загрузки товаров');
    }
    hideLoader();
}

async function loadVariants(product, category) {
    showLoader();
    try {
        const variants = await api(`/api/variants/${product.id}`);
        navigate('variantsView', product);
        document.getElementById('variantProductTitle').textContent = `${category.emoji} ${product.name}`;
        document.getElementById('variantProductDesc').textContent = product.description;
        const list = document.getElementById('variantsList');
        list.innerHTML = '';
        variants.forEach(v => {
            const card = document.createElement('div');
            card.className = 'variant-card';
            card.onclick = () => placeOrder(v, product);
            card.innerHTML = `
                <span class="variant-label">${v.label}</span>
                <span class="variant-price">${v.price} ₽</span>
            `;
            list.appendChild(card);
        });
        staggerChildren(list, 50);
    } catch (e) {
        showToast('Ошибка загрузки вариантов');
    }
    hideLoader();
}

async function placeOrder(variant, product) {
    const user = getUser();
    showLoader();
    try {
        const result = await apiPost('/api/order', {
            variant_id: variant.id,
            user_id: user.id,
            username: user.username || 'Гость',
        });
        hideLoader();
        if (result.ok) {
            navigate('successView', { name: 'Заказ' });
            document.getElementById('successDetails').innerHTML =
                `Заказ <strong>#${result.order_id}</strong><br>` +
                `${product.name} (${variant.label}) — ${variant.price} ₽<br><br>` +
                `Статус прийдёт сообщением в бот.`;
            const t = getTG();
            if (t && t.HapticFeedback) {
                t.HapticFeedback.notificationOccurred('success');
            }
        } else {
            showToast('Ошибка при оформлении заказа');
        }
    } catch (e) {
        hideLoader();
        showToast('Ошибка сети. Попробуйте ещё раз');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadCategories();
});
