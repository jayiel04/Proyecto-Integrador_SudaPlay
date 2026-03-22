document.addEventListener('DOMContentLoaded', () => {
    const profileDropdown = document.querySelector('.profile-dropdown');
    const profileToggle = document.querySelector('.profile-dropdown-toggle');

    window.closeAllPanels = (except = '') => {
        const dropdown = document.querySelector('.profile-dropdown');
        const dropdownToggle = document.querySelector('.profile-dropdown-toggle');
        if (except !== 'profile' && dropdown && dropdownToggle) {
            dropdown.classList.remove('open');
            dropdownToggle.setAttribute('aria-expanded', 'false');
        }

        const chatToggle = document.querySelector('.profile-chat-toggle');
        const chatPanel = document.querySelector('.profile-chat-panel');
        if (except !== 'chat' && chatToggle && chatPanel) {
            chatPanel.classList.remove('visible');
            chatPanel.setAttribute('aria-hidden', 'true');
            chatToggle.setAttribute('aria-expanded', 'false');
        }

        const notifWidget = document.querySelector('.profile-notification-widget');
        const notifToggle = notifWidget ? notifWidget.querySelector('.notification-toggle') : null;
        const notifPanel = notifWidget ? notifWidget.querySelector('.notification-panel') : null;
        if (except !== 'notifications' && notifWidget && notifToggle && notifPanel) {
            notifWidget.classList.remove('open');
            notifToggle.setAttribute('aria-expanded', 'false');
            notifPanel.setAttribute('aria-hidden', 'true');
        }
    };


    if (profileDropdown && profileToggle) {
        const closeMenu = () => {
            profileDropdown.classList.remove('open');
            profileToggle.setAttribute('aria-expanded', 'false');
        };
        const profileCloseBtns = profileDropdown.querySelectorAll('.profile-dropdown-close');

        profileToggle.addEventListener('click', (event) => {
            event.stopPropagation();
            const willOpen = !profileDropdown.classList.contains('open');
            if (willOpen) {
                window.closeAllPanels('profile');
            }
            const isOpen = profileDropdown.classList.toggle('open');
            profileToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });

        profileCloseBtns.forEach((profileCloseBtn) => {
            profileCloseBtn.addEventListener('click', (event) => {
                event.preventDefault();
                event.stopPropagation();
                closeMenu();
            });
        });

        document.addEventListener('click', (event) => {
            if (!profileDropdown.contains(event.target)) {
                closeMenu();
            }
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                closeMenu();
            }
        });

    }

    const profileChatToggle = document.querySelector('.profile-chat-toggle');
    const profileChatPanel = document.querySelector('.profile-chat-panel');

    if (profileChatToggle && profileChatPanel) {
        const chatMessagesContainer = profileChatPanel.querySelector('.profile-chat-messages');
        const chatStatusLabel = profileChatPanel.querySelector('.profile-chat-status');
        const chatForm = profileChatPanel.querySelector('.profile-chat-input-form');
        const chatInputField = chatForm ? chatForm.querySelector('.profile-chat-input') : null;
        const chatCloseBtn = profileChatPanel.querySelector('.profile-chat-close');
        const endpoint = profileChatToggle.dataset.messagesEndpoint;
        const avatarScript = document.getElementById('navbar-avatar-variants-data');
        const avatarVariants = avatarScript ? JSON.parse(avatarScript.textContent || '[]') : [];
        const chatbotAvatarImg = profileChatPanel.querySelector('.profile-chatbot-avatar-img');
        const botAvatarDefault = profileChatPanel.dataset.botAvatar || '';
        let avatarIndex = 0;
        const rotationAvatars = avatarVariants.length ? avatarVariants : (botAvatarDefault ? [botAvatarDefault] : []);
        const CHATBOT_AVATAR_STORAGE_KEY = 'sudaplay.chatbot_avatar_frozen_src';
        const CHATBOT_AVATAR_ROTATE_MS = 2000;
        const CHATBOT_AVATAR_FREEZE_AFTER_MS = 30000;

        if (chatbotAvatarImg && rotationAvatars.length) {
            let frozenAvatarSrc = '';
            try {
                frozenAvatarSrc = localStorage.getItem(CHATBOT_AVATAR_STORAGE_KEY) || '';
            } catch (_) {
                frozenAvatarSrc = '';
            }

            if (frozenAvatarSrc && rotationAvatars.includes(frozenAvatarSrc)) {
                chatbotAvatarImg.src = frozenAvatarSrc;
            } else {
                chatbotAvatarImg.src = rotationAvatars[0];

                if (rotationAvatars.length > 1) {
                    const rotationIntervalId = setInterval(() => {
                        avatarIndex = (avatarIndex + 1) % rotationAvatars.length;
                        chatbotAvatarImg.src = rotationAvatars[avatarIndex];
                    }, CHATBOT_AVATAR_ROTATE_MS);

                    setTimeout(() => {
                        clearInterval(rotationIntervalId);
                        try {
                            localStorage.setItem(CHATBOT_AVATAR_STORAGE_KEY, chatbotAvatarImg.src || '');
                        } catch (_) {
                            // ignore storage failures
                        }
                    }, CHATBOT_AVATAR_FREEZE_AFTER_MS);
                }
            }
        }

        const fallbackResponses = [
            { text: 'Estoy aquí para ayudarte, ¿qué necesitas?' },
            { text: 'Si quieres subir un juego, puedo explicarte los pasos.' },
            { text: 'Completa tu perfil para atraer más jugadores.' },
        ];
        let autoResponses = [...fallbackResponses];
        let autoResponseIndex = 0;
        let greetingShown = false;

        const formatTime = () => {
            const now = new Date();
            return now.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
        };

        const appendMessage = (text, sender = 'bot', meta = '', avatarUrl = '') => {
            if (!chatMessagesContainer) {
                return;
            }
            const row = document.createElement('div');
            row.className = `profile-chat-message-row ${sender}`;
            const card = document.createElement('article');
            card.className = `profile-chat-message ${sender}`;
            const content = document.createElement('span');
            content.textContent = text;
            card.appendChild(content);
            if (meta) {
                const metaEl = document.createElement('small');
                metaEl.className = 'meta';
                metaEl.textContent = meta;
                card.appendChild(metaEl);
            }
            if (avatarUrl) {
                const avatarEl = document.createElement('img');
                avatarEl.className = 'profile-chat-message-avatar';
                avatarEl.src = avatarUrl;
                avatarEl.alt = sender === 'user' ? 'Tu avatar' : 'Avatar del bot';
                row.appendChild(avatarEl);
            }
            row.appendChild(card);
            chatMessagesContainer.appendChild(row);
            chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
        };

        const ensureGreeting = () => {
            if (greetingShown) {
                return;
            }
            appendMessage('Hola, ¿en qué te puedo ayudar?', 'bot');
            greetingShown = true;
        };

        const botAvatarUrl = () => chatbotAvatarImg ? chatbotAvatarImg.src : '';

        const handleAutoReply = () => {
            if (!autoResponses.length) {
                return;
            }
            const response = autoResponses[autoResponseIndex % autoResponses.length];
            autoResponseIndex += 1;
            const botText = (response && response.text) || '¿En qué más puedo ayudarte?';
            const botMeta = `${(response && response.author) || 'Chat SudaPlay'} · ${formatTime()}`;
            setTimeout(() => appendMessage(botText, 'bot', botMeta, botAvatarUrl()), 600);
        };

        const fetchMessages = async () => {
            if (!endpoint) {
                chatStatusLabel.textContent = 'Chat sin configurar.';
                return;
            }

            chatStatusLabel.textContent = 'Actualizando...';

            try {
                const response = await fetch(endpoint, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
                if (!response.ok) {
                    throw new Error('No se pudieron cargar los mensajes');
                }
                const payload = await response.json();
                const records = Array.isArray(payload.messages) ? payload.messages : [];
                if (records.length) {
                    autoResponses = records;
                    autoResponseIndex = 0;
                } else {
                    autoResponses = [...fallbackResponses];
                }
                chatStatusLabel.textContent = records.length ? '' : 'Sin nuevos mensajes';
            } catch (error) {
                chatStatusLabel.textContent = 'Error al cargar los mensajes';
                autoResponses = [...fallbackResponses];
            }
        };

        const closeChat = () => {
            profileChatPanel.classList.remove('visible');
            profileChatPanel.setAttribute('aria-hidden', 'true');
            profileChatToggle.setAttribute('aria-expanded', 'false');
        };
        const openChat = () => {
            profileChatPanel.classList.add('visible');
            profileChatPanel.setAttribute('aria-hidden', 'false');
            profileChatToggle.setAttribute('aria-expanded', 'true');
            ensureGreeting();
            fetchMessages();
        };

        profileChatToggle.addEventListener('click', (event) => {
            event.stopPropagation();
            if (profileChatPanel.classList.contains('visible')) {
                closeChat();
                return;
            }
            window.closeAllPanels('chat');
            openChat();
        });

        if (chatCloseBtn) {
            chatCloseBtn.addEventListener('click', (event) => {
                event.stopPropagation();
                closeChat();
            });
        }

        if (chatForm && chatInputField) {
            chatForm.addEventListener('submit', (event) => {
                event.preventDefault();
                const userText = chatInputField.value.trim();
                if (!userText) {
                    return;
                }
                appendMessage(userText, 'user', formatTime(), profileChatPanel.dataset.userAvatar || '');
                chatInputField.value = '';
                chatInputField.focus();
                handleAutoReply();
            });
        }

        document.addEventListener('click', (event) => {
            if (!profileChatPanel.contains(event.target) && !profileChatToggle.contains(event.target)) {
                closeChat();
            }
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                closeChat();
            }
        });
    }

    const notificationWidget = document.querySelector('.profile-notification-widget');
    const notificationToggle = notificationWidget ? notificationWidget.querySelector('.notification-toggle') : null;
    const notificationPanel = notificationWidget ? notificationWidget.querySelector('.notification-panel') : null;
    const notificationCloseBtn = notificationPanel ? notificationPanel.querySelector('.notification-panel-close') : null;
    const notificationList = notificationPanel ? notificationPanel.querySelector('.notification-list') : null;
    const notificationBadge = notificationToggle ? notificationToggle.querySelector('.notification-badge') : null;

    // Upload progress helper (keeps a transient item inside notifications)
    const uploadProgressId = 'notification-upload-progress';
    const getUploadItem = () => {
        if (!notificationList) return null;
        let item = document.getElementById(uploadProgressId);
        if (!item) {
            item = document.createElement('li');
            item.id = uploadProgressId;
            item.className = 'notification-item upload-progress';
            item.innerHTML = `
                <div class="upload-progress-header">
                    <strong>Subiendo juego…</strong>
                    <span class="upload-progress-status" data-status-text>Preparando</span>
                </div>
                <div class="upload-progress-bar">
                    <div class="upload-progress-bar-fill" style="width:0%"></div>
                </div>
            `;
            notificationList.prepend(item);
        }
        return item;
    };

    const updateUploadProgress = (percent, statusText) => {
        const item = getUploadItem();
        if (!item) return;
        if (typeof percent === 'number' && Number.isFinite(percent)) {
            const clamped = Math.max(0, Math.min(100, Math.round(percent)));
            const bar = item.querySelector('.upload-progress-bar-fill');
            if (bar) {
                bar.style.width = `${clamped}%`;
            }
        }
        if (statusText) {
            const statusEl = item.querySelector('[data-status-text]');
            if (statusEl) {
                statusEl.textContent = statusText;
            }
        }
    };

    const markUploadState = (state, statusText) => {
        const item = getUploadItem();
        if (!item) return;
        item.classList.remove('upload-progress-error', 'upload-progress-success');
        if (state === 'success') {
            item.classList.add('upload-progress-success');
            updateUploadProgress(100, statusText || 'Procesando archivo…');
        } else if (state === 'error') {
            item.classList.add('upload-progress-error');
            updateUploadProgress(undefined, statusText || 'Error al subir');
        } else if (statusText) {
            updateUploadProgress(undefined, statusText);
        }
    };

    const removeUploadProgress = (delayMs = 5000) => {
        const item = document.getElementById(uploadProgressId);
        if (!item) return;
        setTimeout(() => {
            item.remove();
        }, delayMs);
    };

    window.sudaplayUploadNotifier = {
        start: (text) => updateUploadProgress(0, text || 'Preparando'),
        update: (percent, text) => updateUploadProgress(percent, text || 'Subiendo…'),
        success: (text) => {
            markUploadState('success', text || 'Procesando archivo…');
            removeUploadProgress(6500);
        },
        error: (text) => {
            markUploadState('error', text || 'Error al subir');
            removeUploadProgress(8000);
        },
        clear: () => removeUploadProgress(0),
    };

    const renderNotifications = (items) => {
        if (!notificationList) return;
        notificationList.innerHTML = '';
        items.forEach((notif) => {
            if (notif.type === 'empty') {
                const li = document.createElement('li');
                li.className = 'notification-empty';
                li.textContent = notif.text;
                notificationList.appendChild(li);
                return;
            }
            const li = document.createElement('li');
            li.className = 'notification-item';
            li.setAttribute('role', 'listitem');
            const dot = notif.type === 'friend_request' ? '<span class="notification-dot"></span>' : '';
            li.innerHTML = `
                <strong>${notif.text}</strong>
                <span class="notification-timestamp">${notif.created_at ? new Date(notif.created_at).toLocaleString() : 'Ahora'}</span>
                ${dot}
            `;
            if (notif.url || notif.id.startsWith('db-')) {
                li.addEventListener('click', () => {
                    if (notif.id.startsWith('db-')) {
                        fetch('/auth/api/notifications/read/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCookie('csrftoken')
                            },
                            body: JSON.stringify({ notification_id: notif.id })
                        }).finally(() => {
                            if (notif.url) {
                                window.location.href = notif.url;
                            }
                        });
                    } else if (notif.url) {
                        window.location.href = notif.url;
                    }
                });
            }
            notificationList.appendChild(li);
        });
    };

    const loadNotifications = () => {
        if (!notificationToggle) return;
        const endpoint = notificationToggle.dataset.notificationsEndpoint;
        if (!endpoint) return;
        fetch(endpoint, { credentials: 'include' })
            .then((response) => response.ok ? response.json() : null)
            .then((data) => {
                if (!data) {
                    renderNotifications([{ type: 'empty', text: 'Sin notificaciones' }]);
                    return;
                }
                const count = data.unread_count || 0;
                if (notificationBadge) {
                    notificationBadge.style.display = count > 0 ? 'block' : 'none';
                }
                renderNotifications(data.notifications || []);
            })
            .catch(() => {
                renderNotifications([{ type: 'empty', text: 'No se pudieron cargar las notificaciones' }]);
            });
    };

    if (notificationToggle && notificationPanel && notificationWidget) {
        const closeNotifications = () => {
            notificationWidget.classList.remove('open');
            notificationToggle.setAttribute('aria-expanded', 'false');
            notificationPanel.setAttribute('aria-hidden', 'true');
        };
        notificationToggle.addEventListener('click', (event) => {
            event.stopPropagation();
            const willOpen = !notificationWidget.classList.contains('open');
            if (willOpen) {
                window.closeAllPanels('notifications');
            }
            const isOpen = notificationWidget.classList.toggle('open');
            notificationToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
            notificationPanel.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
            if (isOpen) {
                renderNotifications([{ type: 'empty', text: 'Cargando notificaciones...' }]);
                loadNotifications();
            }
        });

        if (notificationCloseBtn) {
            const handleNotificationClose = (event) => {
                event.preventDefault();
                event.stopPropagation();
                closeNotifications();
            };
            notificationCloseBtn.addEventListener('click', handleNotificationClose);
            notificationCloseBtn.addEventListener('touchend', handleNotificationClose, { passive: false });
        }

        document.addEventListener('click', (event) => {
            if (!notificationWidget.contains(event.target)) {
                closeNotifications();
            }
        });

        // Actualizar notificaciones al cambiar de página (carga inicial) y cada 5 minutos
        loadNotifications();
        setInterval(loadNotifications, 300000); // 5 * 60 * 1000 = 300000 ms
    }


});
