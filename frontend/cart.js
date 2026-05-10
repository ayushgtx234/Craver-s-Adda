// Craver's Adda - Cart Utility
// All cart operations use localStorage so state persists across pages

const CART_KEY = 'cravers_cart';

const Cart = {
    get() {
        return JSON.parse(localStorage.getItem(CART_KEY) || '[]');
    },

    add(item) {
        const cart = this.get();
        const existing = cart.find(i => i.id === item.id);
        if (existing) {
            existing.qty = (existing.qty || 1) + 1;
        } else {
            cart.push({ ...item, qty: 1 });
        }
        localStorage.setItem(CART_KEY, JSON.stringify(cart));
        this._dispatch();
    },

    remove(id) {
        let cart = this.get();
        const existing = cart.find(i => i.id === id);
        if (existing && existing.qty > 1) {
            existing.qty -= 1;
        } else {
            cart = cart.filter(i => i.id !== id);
        }
        localStorage.setItem(CART_KEY, JSON.stringify(cart));
        this._dispatch();
    },

    clear() {
        localStorage.removeItem(CART_KEY);
        this._dispatch();
    },

    count() {
        return this.get().reduce((sum, i) => sum + (i.qty || 1), 0);
    },

    total() {
        return this.get().reduce((sum, i) => sum + (parseFloat(i.price) * (i.qty || 1)), 0);
    },

    // Dispatch custom event so all pages can react
    _dispatch() {
        window.dispatchEvent(new CustomEvent('cartUpdated', { detail: { count: this.count() } }));
    }
};
