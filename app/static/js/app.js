/* ============================================
   MyCRM Shared JavaScript
   ============================================ */

const API_BASE = ''; //localStorage.getItem('api_base') || 'http://localhost:5000';

// Safe storage wrapper to handle Tracking Prevention / Storage access errors
const safeStorage = {
    getItem(key) {
        try { return localStorage.getItem(key); }
        catch (e) { console.warn('Storage access blocked', e); return null; }
    },
    setItem(key, value) {
        try { localStorage.setItem(key, value); }
        catch (e) { console.warn('Storage access blocked', e); }
    },
    removeItem(key) {
        try { localStorage.removeItem(key); }
        catch (e) { console.warn('Storage access blocked', e); }
    }
};

// Auth utilities
const Auth = {
    getToken() { return safeStorage.getItem('token'); },
    getUser() {
        const u = safeStorage.getItem('user');
        return u ? JSON.parse(u) : null;
    },
    setSession(token, user) {
        safeStorage.setItem('token', token);
        safeStorage.setItem('user', JSON.stringify(user));
    },
    clearSession() {
        safeStorage.removeItem('token');
        safeStorage.removeItem('user');
    },
    isLoggedIn() { return !!this.getToken(); },
    guard() {
        if (!this.isLoggedIn()) {
            window.location.href = 'login.html';
            return false;
        }
        return true;
    },
    logout() {
        this.clearSession();
        window.location.href = 'login.html';
    }
};

// API helper
async function api(url, options = {}) {
    const fullUrl = url.startsWith('http') ? url : `${API_BASE}${url}`;
    const token = Auth.getToken();

    // Build headers only when needed. Do not send Content-Type for GET requests without a body.
    const headers = { ...(options.headers || {}) };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (options.body !== undefined && options.body !== null) headers['Content-Type'] = 'application/json';

    const opts = { headers, ...options };

    if (opts.body && typeof opts.body === 'object') {
        opts.body = JSON.stringify(opts.body);
    }
    try {
        const res = await fetch(fullUrl, opts);
        if (res.status === 401) {
            Auth.clearSession();
            window.location.href = 'login.html';
            return null;
        }
        const data = res.status !== 204 ? await res.json().catch(() => ({})) : {};
        if (!res.ok) {
            throw new Error(data.message || `HTTP ${res.status}`);
        }
        return data;
    } catch (err) {
        showToast(err.message || 'Network error', 'error');
        throw err;
    }
}

// Toast notifications
function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}

// Loading overlay
function showLoading(show = true) {
    let overlay = document.querySelector('.loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<div class="spinner"></div>';
        document.body.appendChild(overlay);
    }
    overlay.classList.toggle('active', show);
}

// Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value || 0);
}

// Format date
function formatDate(iso) {
    if (!iso) return '-';
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// Format datetime
function formatDateTime(iso) {
    if (!iso) return '-';
    const d = new Date(iso);
    return d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

// Avatar color based on name
function avatarColor(name) {
    const colors = ['blue', 'purple', 'green', 'orange', 'red', 'teal'];
    let hash = 0;
    for (let i = 0; i < (name || '').length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
    return colors[Math.abs(hash) % colors.length];
}

// Initials from name
function initials(name) {
    if (!name) return '?';
    return name.split(' ').map(n => n[0]).slice(0, 2).join('');
}

// Status badge class
function statusBadge(status) {
    const map = {
        'open': 'badge-info',
        'won': 'badge-success',
        'lost': 'badge-danger',
        'customer': 'badge-success',
        'prospect': 'badge-warning',
        'lead': 'badge-info',
        'closed': 'badge-neutral'
    };
    return map[(status || '').toLowerCase()] || 'badge-neutral';
}

// Render navbar
function renderNavbar(activePage) {
    const user = Auth.getUser();
    const addNewHtml = activePage === 'dashboard' ? '' : '<a href="contact_form.html" class="btn-primary">+ Add new</a>';
    const html = `
        <div class="top-bar">
            <a href="#" onclick="alert('Feedback form coming soon'); return false;">Send Feedback</a>
            <a href="#" onclick="alert('Forums coming soon'); return false;">Forums</a>
            <a href="#" onclick="alert('Help center coming soon'); return false;">Help</a>
            <a href="#" onclick="alert('Blog coming soon'); return false;">Blog</a>
            <a href="#" onclick="alert('Account settings coming soon'); return false;">Account</a>
            <a href="#" onclick="Auth.logout(); return false;">Logout</a>
        </div>
        <nav class="navbar">
            <a href="index.html" class="brand">
                <div class="brand-icon">&#8962;</div>
                <div>MyCRM <small>by pythoncoder</small></div>
            </a>
            <ul class="nav-links">
                <li><a href="index.html" class="${activePage === 'dashboard' ? 'active' : ''}">Dashboard</a></li>
                <li><a href="activities.html" class="${activePage === 'activities' ? 'active' : ''}">Activities</a></li>
                <li><a href="contacts.html" class="${activePage === 'contacts' ? 'active' : ''}">Contacts</a></li>
                <li><a href="deals.html" class="${activePage === 'deals' ? 'active' : ''}">Deals</a></li>
                <li><a href="companies.html" class="${activePage === 'companies' ? 'active' : ''}">Companies</a></li>
            </ul>
            <div class="search-box">
                <input type="text" id="globalSearch" placeholder="Search..." autocomplete="off">
                <button onclick="performGlobalSearch()">&#128269;</button>
                <div class="search-dropdown" id="searchDropdown"></div>
            </div>
            ${addNewHtml}
        </nav>
    `;
    const el = document.getElementById('navbar');
    if (el) el.innerHTML = html;
}

// Global search
let searchTimeout;
function setupGlobalSearch() {
    const input = document.getElementById('globalSearch');
    const dropdown = document.getElementById('searchDropdown');
    if (!input || !dropdown) return;

    input.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const q = e.target.value.trim();
        if (!q) { dropdown.classList.remove('active'); return; }
        searchTimeout = setTimeout(() => doSearch(q), 300);
    });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            clearTimeout(searchTimeout);
            performGlobalSearch();
        }
    });

    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.remove('active');
        }
    });
}

async function doSearch(q) {
    const dropdown = document.getElementById('searchDropdown');
    try {
        const data = await api(`/api/search?q=${encodeURIComponent(q)}`);
        if (!data) return;
        let html = '';
        if (data.contacts && data.contacts.length) {
            html += `<div class="search-section"><h4>Contacts</h4>` +
                data.contacts.slice(0, 5).map(c =>
                    `<div class="search-item" onclick="location.href='contact_form.html?id=${c.id}'">${c.name} <span style="color:#6B7280;font-size:12px">${c.company || ''}</span></div>`
                ).join('') + `</div>`;
        }
        if (data.deals && data.deals.length) {
            html += `<div class="search-section"><h4>Deals</h4>` +
                data.deals.slice(0, 5).map(d =>
                    `<div class="search-item" onclick="location.href='deal_form.html?id=${d.id}'">${d.title} <span style="color:#6B7280;font-size:12px">$${d.value}</span></div>`
                ).join('') + `</div>`;
        }
        if (data.activities && data.activities.length) {
            html += `<div class="search-section"><h4>Activities</h4>` +
                data.activities.slice(0, 5).map(a =>
                    `<div class="search-item" onclick="location.href='activities.html'">${a.kind}: ${a.notes || ''}</div>`
                ).join('') + `</div>`;
        }
        if (!html) html = '<div class="search-section"><div class="search-item">No results found</div></div>';
        dropdown.innerHTML = html;
        dropdown.classList.add('active');
    } catch (e) {
        dropdown.classList.remove('active');
    }
}

function performGlobalSearch() {
    const q = document.getElementById('globalSearch')?.value.trim();
    if (q) window.location.href = `contacts.html?q=${encodeURIComponent(q)}`;
}

// Delete confirmation modal
function confirmDelete(message, onConfirm) {
    let overlay = document.getElementById('confirmModal');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'confirmModal';
        overlay.className = 'modal-overlay';
        overlay.innerHTML = `
            <div class="modal">
                <div class="modal-header"><h3>Confirm Delete</h3><button class="modal-close" onclick="closeConfirm()">&times;</button></div>
                <div class="modal-body"><p id="confirmMessage"></p><div class="form-actions"><button class="btn-secondary" onclick="closeConfirm()">Cancel</button><button class="btn-danger" id="confirmBtn">Delete</button></div></div>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    document.getElementById('confirmMessage').textContent = message || 'Are you sure you want to delete this item?';
    const btn = document.getElementById('confirmBtn');
    btn.onclick = () => { closeConfirm(); onConfirm(); };
    overlay.classList.add('active');
}

function closeConfirm() {
    document.getElementById('confirmModal')?.classList.remove('active');
}

// Init on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    setupGlobalSearch();
});
