/* ============================================================
   ChatApp — Frontend Logic
   ============================================================ */

const API = `${window.location.origin}/api`;
const WS_URL = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;

// ============================================================
// STATE
// ============================================================
const state = {
    token: localStorage.getItem('chat_token') || null,
    user: null,
    groups: [],
    users: [],
    currentChat: null,       // { type: 'group'|'direct', id, name }
    messages: [],
    ws: null,
    typingTimeout: null,
};

// ============================================================
// DOM REFS
// ============================================================
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

const dom = {
    authScreen:     $('#auth-screen'),
    chatScreen:     $('#chat-screen'),
    loginForm:      $('#login-form'),
    registerForm:   $('#register-form'),
    loginUsername:   $('#login-username'),
    loginPassword:   $('#login-password'),
    btnLogin:        $('#btn-login'),
    loginError:      $('#login-error'),
    regUsername:     $('#reg-username'),
    regEmail:        $('#reg-email'),
    regFullname:     $('#reg-fullname'),
    regPassword:     $('#reg-password'),
    btnRegister:     $('#btn-register'),
    registerError:   $('#register-error'),
    showRegister:    $('#show-register'),
    showLogin:       $('#show-login'),
    userAvatar:      $('#user-avatar'),
    userDisplayName: $('#user-display-name'),
    btnLogout:       $('#btn-logout'),
    btnSettings:     $('#btn-settings'),
    searchInput:     $('#search-input'),
    groupsList:      $('#groups-list'),
    usersList:       $('#users-list'),
    btnCreateGroup:  $('#btn-create-group'),
    chatEmpty:       $('#chat-empty'),
    chatActive:      $('#chat-active'),
    chatTitle:       $('#chat-title'),
    chatSubtitle:    $('#chat-subtitle'),
    messagesContainer: $('#messages-container'),
    messagesList:    $('#messages-list'),
    messageInput:    $('#message-input'),
    btnSend:         $('#btn-send'),
    btnSchedule:     $('#btn-schedule'),
    scheduleBar:     $('#schedule-bar'),
    scheduleTime:    $('#schedule-time'),
    btnCancelSchedule: $('#btn-cancel-schedule'),
    typingIndicator: $('#typing-indicator'),
    typingText:      $('#typing-text'),
    btnGroupMembers: $('#btn-group-members'),
    membersPanel:    $('#members-panel'),
    membersList:     $('#members-list'),
    btnCloseMembers: $('#btn-close-members'),
    btnBackSidebar:  $('#btn-back-sidebar'),
    modalOverlay:    $('#modal-overlay'),
    groupName:       $('#group-name'),
    groupDesc:       $('#group-desc'),
    groupPrivate:    $('#group-private'),
    btnCloseModal:   $('#btn-close-modal'),
    btnCancelGroup:  $('#btn-cancel-group'),
    btnConfirmGroup: $('#btn-confirm-group'),
    membersModalOverlay:     $('#members-modal-overlay'),
    membersModalTitle:       $('#members-modal-title'),
    membersModalList:        $('#members-modal-list'),
    btnCloseMembersModal:    $('#btn-close-members-modal'),
    settingsModalOverlay:    $('#settings-modal-overlay'),
    btnCloseSettings:        $('#btn-close-settings'),
};

// ============================================================
// UTILITIES
// ============================================================
function toast(msg, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.textContent = msg;
    container.appendChild(t);
    setTimeout(() => { t.remove(); }, 3500);
}

function initials(name) {
    if (!name) return '?';
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return name.substring(0, 2).toUpperCase();
}

function hashColor(str) {
    let h = 0;
    for (let i = 0; i < str.length; i++) h = str.charCodeAt(i) + ((h << 5) - h);
    const hue = Math.abs(h) % 360;
    return `hsl(${hue}, 55%, 55%)`;
}

function formatTime(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================
// THEME & SETTINGS
// ============================================================
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('chat_theme', theme);
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.theme === theme);
    });
}

function applyAccent(color) {
    document.documentElement.style.setProperty('--accent', color);
    document.documentElement.style.setProperty('--accent-hover', color + 'dd');
    document.documentElement.style.setProperty('--accent-soft', color + '26');
    document.documentElement.style.setProperty('--msg-own', color);
    localStorage.setItem('chat_accent', color);
    document.querySelectorAll('.accent-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.accent === color);
    });
}

function initSettings() {
    const savedTheme = localStorage.getItem('chat_theme') || 'dark';
    const savedAccent = localStorage.getItem('chat_accent') || '#6c5ce7';
    applyTheme(savedTheme);
    applyAccent(savedAccent);
}

dom.btnSettings.addEventListener('click', () => {
    dom.settingsModalOverlay.classList.add('active');
});

dom.btnCloseSettings.addEventListener('click', () => {
    dom.settingsModalOverlay.classList.remove('active');
});

dom.settingsModalOverlay.addEventListener('click', (e) => {
    if (e.target === dom.settingsModalOverlay) dom.settingsModalOverlay.classList.remove('active');
});

document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.addEventListener('click', () => applyTheme(btn.dataset.theme));
});

document.querySelectorAll('.accent-btn').forEach(btn => {
    btn.addEventListener('click', () => applyAccent(btn.dataset.accent));
});

initSettings();

// ============================================================
// SCHEDULE MESSAGE
// ============================================================
let scheduleMode = false;

dom.btnSchedule.addEventListener('click', () => {
    scheduleMode = !scheduleMode;
    dom.btnSchedule.classList.toggle('active', scheduleMode);
    dom.scheduleBar.classList.toggle('active', scheduleMode);
    if (scheduleMode) {
        const now = new Date();
        now.setMinutes(now.getMinutes() + 30);
        const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
        dom.scheduleTime.value = local;
        dom.scheduleTime.min = new Date().toISOString().slice(0, 16);
    }
});

dom.btnCancelSchedule.addEventListener('click', () => {
    scheduleMode = false;
    dom.btnSchedule.classList.remove('active');
    dom.scheduleBar.classList.remove('active');
});

async function cancelScheduledMessage(msgId) {
    try {
        await apiFetch(`/messages/scheduled/${msgId}`, { method: 'DELETE' });
        toast('Отложенное сообщение отменено', 'info');
        if (state.currentChat) {
            if (state.currentChat.type === 'group') {
                await loadGroupMessages(state.currentChat.id);
            } else {
                await loadDirectMessages(state.currentChat.id);
            }
        }
    } catch (err) {
        toast(err.message, 'error');
    }
}

async function apiFetch(path, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    if (state.token) headers['Authorization'] = `Bearer ${state.token}`;

    const res = await fetch(`${API}${path}`, { ...options, headers });

    if (res.status === 204) return null;

    const data = await res.json().catch(() => null);

    if (!res.ok) {
        const detail = data?.detail || `Ошибка ${res.status}`;
        throw new Error(detail);
    }
    return data;
}

// ============================================================
// AUTH
// ============================================================
dom.showRegister.addEventListener('click', (e) => {
    e.preventDefault();
    dom.loginForm.classList.remove('active');
    dom.registerForm.classList.add('active');
    dom.loginError.classList.remove('show');
});

dom.showLogin.addEventListener('click', (e) => {
    e.preventDefault();
    dom.registerForm.classList.remove('active');
    dom.loginForm.classList.add('active');
    dom.registerError.classList.remove('show');
});

dom.btnLogin.addEventListener('click', handleLogin);
dom.loginPassword.addEventListener('keydown', (e) => { if (e.key === 'Enter') handleLogin(); });
dom.loginUsername.addEventListener('keydown', (e) => { if (e.key === 'Enter') dom.loginPassword.focus(); });

async function handleLogin() {
    const username = dom.loginUsername.value.trim();
    const password = dom.loginPassword.value;

    if (!username || !password) {
        showError(dom.loginError, 'Заполните все поля');
        return;
    }

    dom.btnLogin.disabled = true;
    try {
        const data = await apiFetch('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
        state.token = data.access_token;
        localStorage.setItem('chat_token', data.access_token);
        await enterChat();
    } catch (err) {
        showError(dom.loginError, err.message);
    } finally {
        dom.btnLogin.disabled = false;
    }
}

dom.btnRegister.addEventListener('click', handleRegister);
dom.regPassword.addEventListener('keydown', (e) => { if (e.key === 'Enter') handleRegister(); });

async function handleRegister() {
    const username = dom.regUsername.value.trim();
    const email = dom.regEmail.value.trim() || null;
    const full_name = dom.regFullname.value.trim() || null;
    const password = dom.regPassword.value;

    if (!username || !password) {
        showError(dom.registerError, 'Имя пользователя и пароль обязательны');
        return;
    }

    dom.btnRegister.disabled = true;
    try {
        await apiFetch('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, full_name, password }),
        });
        // after registration, auto-login
        const data = await apiFetch('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
        state.token = data.access_token;
        localStorage.setItem('chat_token', data.access_token);
        await enterChat();
    } catch (err) {
        showError(dom.registerError, err.message);
    } finally {
        dom.btnRegister.disabled = false;
    }
}

function showError(el, msg) {
    el.textContent = msg;
    el.classList.add('show');
}

// ============================================================
// ENTER / EXIT CHAT
// ============================================================
async function enterChat() {
    try {
        state.user = await apiFetch('/auth/me');
    } catch {
        logout();
        return;
    }

    dom.authScreen.classList.remove('active');
    dom.chatScreen.classList.add('active');

    dom.userDisplayName.textContent = state.user.full_name || state.user.username;
    dom.userAvatar.textContent = initials(state.user.full_name || state.user.username);
    dom.userAvatar.style.background = hashColor(state.user.username);

    showEmptyChat();
    await Promise.all([loadGroups(), loadUsers()]);
    connectWebSocket();
}

dom.btnLogout.addEventListener('click', logout);

function logout() {
    state.token = null;
    state.user = null;
    state.currentChat = null;
    state.messages = [];
    localStorage.removeItem('chat_token');
    disconnectWebSocket();
    dom.chatScreen.classList.remove('active');
    dom.authScreen.classList.add('active');
    dom.loginUsername.value = '';
    dom.loginPassword.value = '';
    dom.loginError.classList.remove('show');
}

// ============================================================
// LOAD DATA
// ============================================================
async function loadGroups() {
    try {
        state.groups = await apiFetch('/groups/');
    } catch { state.groups = []; }
    renderGroups();
}

async function loadUsers() {
    try {
        state.users = await apiFetch('/users/');
    } catch { state.users = []; }
    renderUsers();
}

function renderGroups(filter = '') {
    dom.groupsList.innerHTML = '';
    const lower = filter.toLowerCase();
    state.groups
        .filter(g => !lower || g.name.toLowerCase().includes(lower))
        .forEach(g => {
            const el = document.createElement('div');
            el.className = 'chat-item' + (state.currentChat?.type === 'group' && state.currentChat.id === g.id ? ' active' : '');
            el.innerHTML = `
                <div class="item-avatar" style="background:${hashColor(g.name)}">${initials(g.name)}</div>
                <div class="item-info">
                    <div class="item-name">${escapeHtml(g.name)}</div>
                    <div class="item-preview">${g.is_private ? 'Приватная' : 'Публичная'}</div>
                </div>
            `;
            el.addEventListener('click', () => openGroupChat(g));
            dom.groupsList.appendChild(el);
        });
}

function renderUsers(filter = '') {
    dom.usersList.innerHTML = '';
    const lower = filter.toLowerCase();
    state.users
        .filter(u => u.id !== state.user?.id)
        .filter(u => !lower || u.username.toLowerCase().includes(lower) || (u.full_name && u.full_name.toLowerCase().includes(lower)))
        .forEach(u => {
            const el = document.createElement('div');
            el.className = 'chat-item' + (state.currentChat?.type === 'direct' && state.currentChat.id === u.id ? ' active' : '');
            el.innerHTML = `
                <div class="item-avatar" style="background:${hashColor(u.username)}">${initials(u.full_name || u.username)}</div>
                <div class="item-info">
                    <div class="item-name">${escapeHtml(u.full_name || u.username)}</div>
                    <div class="item-preview">@${escapeHtml(u.username)}</div>
                </div>
            `;
            el.addEventListener('click', () => openDirectChat(u));
            dom.usersList.appendChild(el);
        });
}

// ============================================================
// OPEN CHATS
// ============================================================
async function openGroupChat(group) {
    state.currentChat = { type: 'group', id: group.id, name: group.name };

    dom.chatEmpty.classList.remove('active');
    dom.chatActive.classList.add('active');
    dom.chatTitle.textContent = group.name;
    dom.chatSubtitle.textContent = group.is_private ? 'Приватная группа' : 'Публичная группа';
    dom.btnGroupMembers.style.display = 'flex';
    dom.messageInput.focus();

    renderGroups();
    renderUsers();
    await loadGroupMessages(group.id);
}

async function openDirectChat(user) {
    state.currentChat = { type: 'direct', id: user.id, name: user.full_name || user.username };

    dom.chatEmpty.classList.remove('active');
    dom.chatActive.classList.add('active');
    dom.chatTitle.textContent = user.full_name || user.username;
    dom.chatSubtitle.textContent = `@${user.username}`;
    dom.btnGroupMembers.style.display = 'none';
    dom.messageInput.focus();

    renderGroups();
    renderUsers();
    await loadDirectMessages(user.id);
}

function showEmptyChat() {
    state.currentChat = null;
    dom.chatActive.classList.remove('active');
    dom.chatEmpty.classList.add('active');
    dom.membersPanel.classList.remove('active');
    renderGroups();
    renderUsers();
}

// ============================================================
// LOAD MESSAGES
// ============================================================
async function loadGroupMessages(groupId) {
    try {
        state.messages = await apiFetch(`/messages/group/${groupId}?limit=200`);
    } catch { state.messages = []; }
    renderMessages();
    scrollToBottom();
}

async function loadDirectMessages(userId) {
    try {
        state.messages = await apiFetch(`/messages/direct/${userId}?limit=200`);
    } catch { state.messages = []; }
    renderMessages();
    scrollToBottom();
}

function renderMessages() {
    dom.messagesList.innerHTML = '';

    let lastSenderId = null;
    let lastTime = null;
    let groupEl = null;

    state.messages.forEach((msg) => {
        const senderId = msg.sender_id;
        const msgTime = new Date(msg.created_at).getTime();
        const sameSender = senderId === lastSenderId;
        const closeInTime = lastTime && (msgTime - lastTime < 5 * 60 * 1000);

        if (!sameSender || !closeInTime) {
            groupEl = document.createElement('div');
            groupEl.className = 'message-group';
            dom.messagesList.appendChild(groupEl);

            const isOwn = senderId === state.user?.id;
            const senderName = msg.sender_username || `User #${senderId}`;
            const header = document.createElement('div');
            header.className = 'message-group-header';
            header.innerHTML = `
                <div class="msg-avatar" style="background:${hashColor(senderName)}">${initials(senderName)}</div>
                <span class="msg-sender">${escapeHtml(senderName)}</span>
                <span class="msg-time">${formatTime(msg.created_at)}</span>
            `;
            if (isOwn) header.style.justifyContent = 'flex-end';
            groupEl.appendChild(header);

            lastSenderId = senderId;
            lastTime = msgTime;
        }

        const isOwn = senderId === state.user?.id;
        const bubble = document.createElement('div');
        bubble.className = 'message ' + (isOwn ? 'own' : 'other');
        if (msg.is_deleted) bubble.classList.add('deleted');
        if (msg.scheduled_at && !msg.is_sent) bubble.classList.add('scheduled');

        const text = msg.is_deleted ? 'Сообщение удалено' : escapeHtml(msg.content);
        const edited = msg.edited_at && !msg.is_deleted ? '<div class="msg-edited">(ред.)</div>' : '';
        const scheduledTime = msg.scheduled_at && !msg.is_sent
            ? `<div class="msg-scheduled-time">Отправка: ${new Date(msg.scheduled_at).toLocaleString('ru-RU')}</div>`
            : '';
        const cancelBtn = msg.scheduled_at && !msg.is_sent && msg.sender_id === state.user?.id
            ? `<button class="btn-cancel-msg" data-msg-id="${msg.id}">Отмена</button>`
            : '';

        bubble.innerHTML = `<div class="msg-text">${text}</div>${edited}${scheduledTime}${cancelBtn}`;
        groupEl.appendChild(bubble);

        if (cancelBtn) {
            bubble.querySelector('.btn-cancel-msg').addEventListener('click', (e) => {
                e.stopPropagation();
                cancelScheduledMessage(msg.id);
            });
        }
    });
}

function scrollToBottom() {
    requestAnimationFrame(() => {
        dom.messagesContainer.scrollTop = dom.messagesContainer.scrollHeight;
    });
}

// ============================================================
// SEND MESSAGE
// ============================================================
dom.btnSend.addEventListener('click', sendMessage);
dom.messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

dom.messageInput.addEventListener('input', () => {
    if (state.ws && state.ws.readyState === WebSocket.OPEN && state.currentChat) {
        const payload = { type: 'typing' };
        if (state.currentChat.type === 'group') payload.group_id = state.currentChat.id;
        else payload.receiver_id = state.currentChat.id;
        state.ws.send(JSON.stringify(payload));
    }
});

function sendMessage() {
    const content = dom.messageInput.value.trim();
    if (!content || !state.currentChat) return;

    if (scheduleMode && dom.scheduleTime.value) {
        const scheduledAt = new Date(dom.scheduleTime.value).toISOString();
        const payload = {
            content,
            scheduled_at: scheduledAt,
        };
        if (state.currentChat.type === 'group') payload.group_id = state.currentChat.id;
        else payload.receiver_id = state.currentChat.id;

        apiFetch('/messages/schedule', {
            method: 'POST',
            body: JSON.stringify(payload),
        }).then(() => {
            toast('Сообщение запланировано', 'success');
            scheduleMode = false;
            dom.btnSchedule.classList.remove('active');
            dom.scheduleBar.classList.remove('active');
        }).catch(err => {
            toast(err.message, 'error');
        });
    } else {
        if (!state.ws || state.ws.readyState !== WebSocket.OPEN) return;
        const payload = {
            type: state.currentChat.type === 'group' ? 'group_message' : 'direct_message',
            content,
        };
        if (state.currentChat.type === 'group') payload.group_id = state.currentChat.id;
        else payload.receiver_id = state.currentChat.id;
        state.ws.send(JSON.stringify(payload));
    }

    dom.messageInput.value = '';
}

// ============================================================
// WEBSOCKET
// ============================================================
function connectWebSocket() {
    disconnectWebSocket();
    if (!state.token) return;

    const ws = new WebSocket(`${WS_URL}/${state.token}`);

    ws.onopen = () => {
        console.log('[WS] Connected');
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleWsMessage(data);
        } catch {}
    };

    ws.onclose = (event) => {
        console.log('[WS] Disconnected', event.code);
        if (state.token && event.code !== 4001) {
            setTimeout(connectWebSocket, 3000);
        }
    };

    ws.onerror = (err) => {
        console.error('[WS] Error', err);
    };

    state.ws = ws;
}

function disconnectWebSocket() {
    if (state.ws) {
        state.ws.onclose = null;
        state.ws.close();
        state.ws = null;
    }
}

function handleWsMessage(data) {
    switch (data.type) {
        case 'group_message':
            handleGroupMessage(data);
            break;
        case 'direct_message':
            handleDirectMessage(data);
            break;
        case 'typing':
            handleTyping(data);
            break;
        case 'read_receipt':
            break;
        case 'error':
            console.warn('[WS] Error:', data.error);
            break;
    }
}

function handleGroupMessage(data) {
    // if we're in this group chat, append message
    if (state.currentChat?.type === 'group' && state.currentChat.id === data.group_id) {
        appendMessage({
            id: data.message_id,
            content: data.content,
            sender_id: data.sender_id,
            sender_username: getUserName(data.sender_id),
            created_at: data.created_at,
            is_deleted: false,
        });
    }
    // update badge or preview in sidebar
    renderGroups();
}

function handleDirectMessage(data) {
    const otherId = data.sender_id === state.user?.id ? data.receiver_id : data.sender_id;

    if (state.currentChat?.type === 'direct' && state.currentChat.id === otherId) {
        appendMessage({
            id: data.message_id,
            content: data.content,
            sender_id: data.sender_id,
            sender_username: getUserName(data.sender_id),
            created_at: data.created_at,
            is_deleted: false,
        });
    }
    renderUsers();
}

function handleTyping(data) {
    if (data.user_id === state.user?.id) return;

    const name = getUserName(data.user_id);
    dom.typingText.textContent = `${name} печатает...`;
    dom.typingIndicator.style.display = 'flex';
    clearTimeout(state.typingTimeout);
    state.typingTimeout = setTimeout(() => {
        dom.typingIndicator.style.display = 'none';
    }, 3000);
}

function getUserName(userId) {
    if (userId === state.user?.id) return state.user.full_name || state.user.username;
    const u = state.users.find(u => u.id === userId);
    return u ? (u.full_name || u.username) : `User #${userId}`;
}

function appendMessage(msg) {
    state.messages.push(msg);

    const lastGroup = dom.messagesList.lastElementChild;
    const lastSenderId = state.messages.length >= 2 ? state.messages[state.messages.length - 2]?.sender_id : null;
    const sameSender = msg.sender_id === lastSenderId;
    const lastTime = state.messages.length >= 2 ? new Date(state.messages[state.messages.length - 2]?.created_at).getTime() : null;
    const msgTime = new Date(msg.created_at).getTime();
    const closeInTime = lastTime && (msgTime - lastTime < 5 * 60 * 1000);

    if (lastGroup && sameSender && closeInTime) {
        // append bubble to existing group
        const bubble = document.createElement('div');
        bubble.className = 'message ' + (msg.sender_id === state.user?.id ? 'own' : 'other');
        bubble.innerHTML = `<div class="msg-text">${escapeHtml(msg.content)}</div>`;
        lastGroup.appendChild(bubble);
    } else {
        // new group
        const groupEl = document.createElement('div');
        groupEl.className = 'message-group';

        const isOwn = msg.sender_id === state.user?.id;
        const senderName = msg.sender_username || getUserName(msg.sender_id);
        const header = document.createElement('div');
        header.className = 'message-group-header';
        header.innerHTML = `
            <div class="msg-avatar" style="background:${hashColor(senderName)}">${initials(senderName)}</div>
            <span class="msg-sender">${escapeHtml(senderName)}</span>
            <span class="msg-time">${formatTime(msg.created_at)}</span>
        `;
        if (isOwn) header.style.justifyContent = 'flex-end';
        groupEl.appendChild(header);

        const bubble = document.createElement('div');
        bubble.className = 'message ' + (isOwn ? 'own' : 'other');
        bubble.innerHTML = `<div class="msg-text">${escapeHtml(msg.content)}</div>`;
        groupEl.appendChild(bubble);

        dom.messagesList.appendChild(groupEl);
    }

    scrollToBottom();
}

// ============================================================
// SEARCH
// ============================================================
dom.searchInput.addEventListener('input', (e) => {
    const q = e.target.value;
    renderGroups(q);
    renderUsers(q);
});

// ============================================================
// GROUP CREATION MODAL
// ============================================================
dom.btnCreateGroup.addEventListener('click', () => {
    dom.modalOverlay.classList.add('active');
    dom.groupName.value = '';
    dom.groupDesc.value = '';
    dom.groupPrivate.checked = false;
    dom.groupName.focus();
});

dom.btnCloseModal.addEventListener('click', closeModal);
dom.btnCancelGroup.addEventListener('click', closeModal);
dom.modalOverlay.addEventListener('click', (e) => { if (e.target === dom.modalOverlay) closeModal(); });

function closeModal() { dom.modalOverlay.classList.remove('active'); }

dom.btnConfirmGroup.addEventListener('click', async () => {
    const name = dom.groupName.value.trim();
    if (!name) { toast('Введите название группы', 'error'); return; }

    try {
        const group = await apiFetch('/groups/', {
            method: 'POST',
            body: JSON.stringify({
                name,
                description: dom.groupDesc.value.trim() || null,
                is_private: dom.groupPrivate.checked,
            }),
        });
        closeModal();
        toast('Группа создана', 'success');
        await loadGroups();
        openGroupChat(group);
    } catch (err) {
        toast(err.message, 'error');
    }
});

// ============================================================
// MEMBERS PANEL
// ============================================================
dom.btnGroupMembers.addEventListener('click', async () => {
    if (!state.currentChat || state.currentChat.type !== 'group') return;

    try {
        const data = await apiFetch(`/groups/${state.currentChat.id}/members`);
        dom.membersList.innerHTML = '';
        data.members.forEach(name => {
            const el = document.createElement('div');
            el.className = 'member-item';
            el.innerHTML = `
                <div class="item-avatar" style="background:${hashColor(name)}; width:32px; height:32px; font-size:12px;">${initials(name)}</div>
                <span class="member-name">${escapeHtml(name)}</span>
            `;
            dom.membersList.appendChild(el);
        });
        dom.membersPanel.classList.add('active');
    } catch (err) {
        toast(err.message, 'error');
    }
});

dom.btnCloseMembers.addEventListener('click', () => {
    dom.membersPanel.classList.remove('active');
});

// ============================================================
// INIT — check saved token
// ============================================================
(async function init() {
    if (state.token) {
        await enterChat();
    }
})();
