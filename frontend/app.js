const API_BASE = 'http://localhost:8000/api/v1';
const SESSION_ID = crypto.randomUUID();

// --- Auth & Session Logic ---
async function checkSession() {
    const authNav = document.getElementById('auth-nav');
    if (!authNav) return;
    try {
        const { data: { session } } = await supabaseClient.auth.getSession();
        if (session) {
            authNav.innerHTML = `
                <div style="display:flex;align-items:center;gap:10px;">
                    <a href="profile.html" class="signup-pill" style="background:rgba(255,255,255,0.1);border:1px solid var(--glass-border);">
                        <i class="fa-solid fa-user"></i> Account
                    </a>
                    <button id="logout-btn" style="background:none;border:none;color:var(--primary-red);cursor:pointer;font-size:0.8rem;font-weight:600;">Logout</button>
                </div>`;
            document.getElementById('logout-btn')?.addEventListener('click', async () => {
                await supabaseClient.auth.signOut();
                Cart.clear();
                window.location.reload();
            });
            const mob = document.getElementById('mobile-auth-nav');
            if (mob) mob.innerHTML = `<a href="profile.html"><i class="fa-solid fa-user-check" style="color:var(--primary-red);"></i></a>`;
        } else {
            authNav.innerHTML = `<a href="signup.html" class="signup-pill">Sign up</a>`;
            const mob = document.getElementById('mobile-auth-nav');
            if (mob) mob.innerHTML = `<a href="login.html"><i class="fa-solid fa-user"></i></a>`;
        }
    } catch (e) { console.error(e); }
}

// --- Cart Badge & Floating Button ---
function updateCartUI() {
    const count = Cart.count();
    const badge = document.getElementById('cart-badge');
    const fab   = document.getElementById('cart-fab');
    if (badge) badge.textContent = count;
    if (fab) {
        if (count > 0) {
            fab.style.transform = 'translateY(0) scale(1)';
            fab.style.opacity   = '1';
            fab.style.pointerEvents = 'auto';
            const lbl = fab.querySelector('.fab-label');
            if (lbl) lbl.textContent = `${count} item${count > 1 ? 's' : ''} · Proceed`;
        } else {
            fab.style.transform = 'translateY(80px) scale(0.9)';
            fab.style.opacity   = '0';
            fab.style.pointerEvents = 'none';
        }
    }
}

// Toast notification
function showToast(msg) {
    let toast = document.getElementById('cart-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'cart-toast';
        toast.style.cssText = `
            position:fixed;bottom:100px;left:50%;transform:translateX(-50%) translateY(20px);
            background:var(--primary-red);color:white;padding:12px 25px;border-radius:50px;
            font-weight:600;font-size:0.9rem;z-index:9999;opacity:0;transition:all 0.3s ease;
            white-space:nowrap;box-shadow:0 10px 30px rgba(229,45,39,0.4);`;
        document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.style.opacity = '1';
    toast.style.transform = 'translateX(-50%) translateY(0)';
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(-50%) translateY(20px)';
    }, 2500);
}

// Add to cart with auth guard
async function handleAddToCart(btn) {
    const { data: { session } } = await supabaseClient.auth.getSession();
    if (!session) {
        sessionStorage.setItem('redirect_after_login', window.location.href);
        window.location.href = 'signup.html';
        return;
    }
    const card = btn.closest('.product-card');
    const name  = card.querySelector('.product-title')?.textContent || 'Item';
    const priceText = card.querySelector('.product-price')?.textContent || '0';
    const price = priceText.replace('₹', '').replace('.00', '').trim();
    const img   = card.querySelector('.product-img')?.src || '';
    const id    = name.toLowerCase().replace(/\s+/g, '-');
    Cart.add({ id, name, price, img });
    showToast(`${name} added to cart!`);
}

// Navigate to address page
function proceedToCheckout() {
    if (Cart.count() === 0) return;
    window.location.href = 'address.html';
}

// Listen for cart updates on this page
window.addEventListener('cartUpdated', updateCartUI);

// --- Nav switch ---
const navItems = document.querySelectorAll('.nav-item');
const views    = document.querySelectorAll('.view-content');
function switchView(viewId) {
    if (!views.length) return;
    views.forEach(v => v.classList.toggle('active', v.id === viewId));
    navItems.forEach(i => i.classList.toggle('active', i.dataset.view === viewId));
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
navItems.forEach(item => {
    item.addEventListener('click', () => {
        if (item.dataset.view) switchView(item.dataset.view);
    });
});

// --- Surprise Me ---
async function triggerSurprise() {
    const recContainer = document.getElementById('rec-container');
    if (!recContainer) return;
    recContainer.style.opacity = '0.3';
    try {
        const r = await fetch(`${API_BASE}/surprise?session_id=${SESSION_ID}&user_id=default-user`);
        if (!r.ok) throw new Error();
        const dish = await r.json();
        const dishImg = document.getElementById('dish-image');
        if (dishImg) dishImg.src = dish.image_url;
        const dishName = document.getElementById('dish-name');
        if (dishName) dishName.textContent = dish.dish_name;
        const dishPrice = document.getElementById('dish-price');
        if (dishPrice) dishPrice.textContent = `₹${dish.price}`;
        recContainer.classList.add('visible');
    } catch(e) { console.error(e); }
    finally { recContainer.style.opacity = '1'; }
}
document.getElementById('try-another-btn')?.addEventListener('click', triggerSurprise);
document.getElementById('order-btn')?.addEventListener('click', () => {
    const n = document.getElementById('dish-name')?.textContent;
    const p = document.getElementById('dish-price')?.textContent.replace('₹','');
    const i = document.getElementById('dish-image')?.src;
    window.location.href = `checkout.html?name=${encodeURIComponent(n)}&price=${p}&img=${encodeURIComponent(i)}`;
});

// Init
document.addEventListener('DOMContentLoaded', () => {
    checkSession();
    updateCartUI();
    // Attach add-to-cart to all product cards
    document.querySelectorAll('.add-cart').forEach(btn => {
        btn.addEventListener('click', () => handleAddToCart(btn));
    });
    // Floating button click
    document.getElementById('cart-fab')?.addEventListener('click', proceedToCheckout);
});
