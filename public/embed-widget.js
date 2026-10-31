/**
 * TrueFoundry AI Chat Embed Widget for CIVORA
 */
(function () {
  'use strict';

  // Prevent double injection
  if (window.__CIVORA_AI_WIDGET_LOADED__) return;
  window.__CIVORA_AI_WIDGET_LOADED__ = true;

  var config = window.AIChatConfig || {
    apiEndpoint: '/api/chat',
    title: 'CIVORA AI Engineer',
  };

  var endpoint = config.apiEndpoint || '/api/chat';
  if (endpoint.indexOf('your-backend-api.com') !== -1) {
    endpoint = '/api/chat';
  }
  var widgetTitle = config.title || 'CIVORA AI Engineer';

  // Stylesheet
  var style = document.createElement('style');
  style.id = 'civora-ai-chat-styles';
  style.textContent = [
    '#civora-widget-trigger {',
    '  position: fixed;',
    '  bottom: 24px;',
    '  right: 24px;',
    '  width: 56px;',
    '  height: 56px;',
    '  border-radius: 50%;',
    '  background: linear-gradient(135deg, #0071FF 0%, #7C3AED 100%);',
    '  border: 1px solid rgba(255, 255, 255, 0.25);',
    '  box-shadow: 0 4px 20px rgba(0, 113, 255, 0.45);',
    '  cursor: pointer;',
    '  z-index: 99999;',
    '  display: flex;',
    '  align-items: center;',
    '  justify-content: center;',
    '  transition: transform 0.25s ease, box-shadow 0.25s ease;',
    '}',
    '#civora-widget-trigger:hover {',
    '  transform: scale(1.08);',
    '  box-shadow: 0 6px 28px rgba(0, 113, 255, 0.7);',
    '}',
    '#civora-widget-badge {',
    '  position: absolute;',
    '  top: -3px;',
    '  right: -3px;',
    '  background: #10B981;',
    '  color: #01030F;',
    '  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;',
    '  font-size: 9px;',
    '  font-weight: 700;',
    '  padding: 2px 5px;',
    '  border-radius: 8px;',
    '  border: 1px solid #01030F;',
    '}',
    '#civora-chat-container {',
    '  position: fixed;',
    '  bottom: 92px;',
    '  right: 24px;',
    '  width: 380px;',
    '  max-width: calc(100vw - 32px);',
    '  height: 540px;',
    '  max-height: calc(100vh - 120px);',
    '  background: rgba(1, 3, 15, 0.95);',
    '  backdrop-filter: blur(16px);',
    '  -webkit-backdrop-filter: blur(16px);',
    '  border: 1px solid rgba(255, 255, 255, 0.15);',
    '  border-radius: 16px;',
    '  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.6), 0 0 30px rgba(0, 113, 255, 0.2);',
    '  z-index: 99999;',
    '  display: none;',
    '  flex-direction: column;',
    '  overflow: hidden;',
    '  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;',
    '}',
    '#civora-chat-container.active {',
    '  display: flex;',
    '}',
    '#civora-chat-header {',
    '  padding: 14px 16px;',
    '  background: rgba(4, 9, 23, 0.9);',
    '  border-bottom: 1px solid rgba(255, 255, 255, 0.1);',
    '  display: flex;',
    '  align-items: center;',
    '  justify-content: space-between;',
    '}',
    '#civora-chat-title-group h3 {',
    '  margin: 0;',
    '  font-size: 14px;',
    '  font-weight: 600;',
    '  color: #FFFFFF;',
    '  display: flex;',
    '  align-items: center;',
    '  gap: 8px;',
    '}',
    '#civora-chat-title-group p {',
    '  margin: 2px 0 0 0;',
    '  font-size: 11px;',
    '  color: #38BDF8;',
    '  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;',
    '}',
    '#civora-chat-close {',
    '  background: transparent;',
    '  border: none;',
    '  color: rgba(255, 255, 255, 0.6);',
    '  cursor: pointer;',
    '  padding: 4px;',
    '  display: flex;',
    '  align-items: center;',
    '  justify-content: center;',
    '  border-radius: 4px;',
    '}',
    '#civora-chat-close:hover {',
    '  color: #FFFFFF;',
    '  background: rgba(255, 255, 255, 0.1);',
    '}',
    '#civora-chat-messages {',
    '  flex: 1;',
    '  overflow-y: auto;',
    '  padding: 16px;',
    '  display: flex;',
    '  flex-direction: column;',
    '  gap: 12px;',
    '}',
    '.civora-msg {',
    '  max-width: 85%;',
    '  padding: 10px 14px;',
    '  border-radius: 12px;',
    '  font-size: 13px;',
    '  line-height: 1.45;',
    '  word-break: break-word;',
    '}',
    '.civora-msg-agent {',
    '  align-self: flex-start;',
    '  background: rgba(255, 255, 255, 0.05);',
    '  border: 1px solid rgba(255, 255, 255, 0.1);',
    '  color: #E2E8F0;',
    '}',
    '.civora-msg-user {',
    '  align-self: flex-end;',
    '  background: #0071FF;',
    '  color: #FFFFFF;',
    '}',
    '#civora-chat-chips {',
    '  display: flex;',
    '  flex-wrap: wrap;',
    '  gap: 6px;',
    '  margin-top: 6px;',
    '}',
    '.civora-chip {',
    '  background: rgba(255, 255, 255, 0.06);',
    '  border: 1px solid rgba(255, 255, 255, 0.15);',
    '  color: #94A3B8;',
    '  font-size: 11px;',
    '  padding: 4px 8px;',
    '  border-radius: 6px;',
    '  cursor: pointer;',
    '  transition: all 0.2s;',
    '}',
    '.civora-chip:hover {',
    '  background: rgba(0, 113, 255, 0.2);',
    '  border-color: #0071FF;',
    '  color: #FFFFFF;',
    '}',
    '#civora-chat-input-area {',
    '  padding: 12px;',
    '  border-top: 1px solid rgba(255, 255, 255, 0.1);',
    '  background: rgba(4, 9, 23, 0.7);',
    '  display: flex;',
    '  gap: 8px;',
    '}',
    '#civora-chat-input {',
    '  flex: 1;',
    '  background: rgba(255, 255, 255, 0.05);',
    '  border: 1px solid rgba(255, 255, 255, 0.15);',
    '  border-radius: 8px;',
    '  padding: 8px 12px;',
    '  color: #FFFFFF;',
    '  font-size: 13px;',
    '  outline: none;',
    '}',
    '#civora-chat-input:focus {',
    '  border-color: #0071FF;',
    '}',
    '#civora-chat-send {',
    '  background: #0071FF;',
    '  border: none;',
    '  border-radius: 8px;',
    '  color: #FFFFFF;',
    '  padding: 8px 14px;',
    '  cursor: pointer;',
    '  font-size: 12px;',
    '  font-weight: 600;',
    '  transition: background 0.2s;',
    '}',
    '#civora-chat-send:hover {',
    '  background: #38BDF8;',
    '}',
    '#civora-chat-send:disabled {',
    '  opacity: 0.5;',
    '  cursor: not-allowed;',
    '}'
  ].join('\n');
  document.head.appendChild(style);

  // Trigger button
  var trigger = document.createElement('div');
  trigger.id = 'civora-widget-trigger';
  trigger.setAttribute('aria-label', 'Open CIVORA AI Assistant');
  trigger.innerHTML = [
    '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">',
    '  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>',
    '</svg>',
    '<span id="civora-widget-badge">AI</span>'
  ].join('');

  // Container
  var container = document.createElement('div');
  container.id = 'civora-chat-container';
  container.innerHTML = [
    '<div id="civora-chat-header">',
    '  <div id="civora-chat-title-group">',
    '    <h3>',
    '      <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#10B981;"></span>',
    '      ' + widgetTitle,
    '    </h3>',
    '    <p>TrueForge // Gemma 4 MoE</p>',
    '  </div>',
    '  <button id="civora-chat-close" aria-label="Close Chat">',
    '    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">',
    '      <line x1="18" y1="6" x2="6" y2="18"></line>',
    '      <line x1="6" y1="6" x2="18" y2="18"></line>',
    '    </svg>',
    '  </button>',
    '</div>',
    '<div id="civora-chat-messages">',
    '  <div class="civora-msg civora-msg-agent">',
    '    Hello! I am your <strong>CIVORA AI Engineer</strong> powered by TrueFoundry and Gemma 4 26B-A4B MoE. How can I assist with repository setup, CI drift, or isolated sandboxing today?',
    '    <div id="civora-chat-chips">',
    '      <button class="civora-chip" data-q="Inspect anshgandhi68-sys/CIVORA">Inspect CIVORA</button>',
    '      <button class="civora-chip" data-q="What is CI Drift Detection?">What is CI Drift?</button>',
    '      <button class="civora-chip" data-q="How does Zero-Trust Gate work?">Zero-Trust Gate</button>',
    '    </div>',
    '  </div>',
    '</div>',
    '<form id="civora-chat-input-area">',
    '  <input type="text" id="civora-chat-input" placeholder="Ask CIVORA AI..." autocomplete="off" />',
    '  <button type="submit" id="civora-chat-send">Send</button>',
    '</form>'
  ].join('');

  document.body.appendChild(trigger);
  document.body.appendChild(container);

  function openWidget() {
    container.classList.add('active');
    var input = document.getElementById('civora-chat-input');
    if (input) input.focus();
  }

  function closeWidget() {
    container.classList.remove('active');
  }

  window.openCivoraAIChat = openWidget;
  window.closeCivoraAIChat = closeWidget;

  // Global click delegate for any button with .open-ai-chat
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.open-ai-chat, [data-open-chat]');
    if (btn) {
      e.preventDefault();
      openWidget();
    }
  });

  // Toggle widget via floating button
  trigger.addEventListener('click', function () {
    var isOpen = container.classList.contains('active');
    if (isOpen) {
      closeWidget();
    } else {
      openWidget();
    }
  });

  var closeBtn = document.getElementById('civora-chat-close');
  if (closeBtn) {
    closeBtn.addEventListener('click', function () {
      closeWidget();
    });
  }

  // Handle messages
  var messagesDiv = document.getElementById('civora-chat-messages');
  var form = document.getElementById('civora-chat-input-area');
  var input = document.getElementById('civora-chat-input');
  var sendBtn = document.getElementById('civora-chat-send');

  function appendMessage(text, isUser) {
    var msg = document.createElement('div');
    msg.className = 'civora-msg ' + (isUser ? 'civora-msg-user' : 'civora-msg-agent');
    msg.innerHTML = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    messagesDiv.appendChild(msg);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return msg;
  }

  function sendMessage(query) {
    if (!query || !query.trim()) return;
    appendMessage(query, true);

    input.value = '';
    sendBtn.disabled = true;

    var typingMsg = appendMessage('<em>Reasoning over repository & MCP tools...</em>', false);

    fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: query }),
    })
      .then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
      })
      .then(function (data) {
        var replyText = data.response || data.reply || data.message || 'I have completed the analysis.';
        typingMsg.innerHTML = replyText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
      })
      .catch(function (err) {
        typingMsg.innerHTML = 'Unable to reach backend endpoint (' + endpoint + '). Ensure backend server is running.';
      })
      .finally(function () {
        sendBtn.disabled = false;
        input.focus();
      });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    sendMessage(input.value);
  });

  messagesDiv.addEventListener('click', function (e) {
    if (e.target && e.target.classList.contains('civora-chip')) {
      var q = e.target.getAttribute('data-q');
      sendMessage(q);
    }
  });
})();
