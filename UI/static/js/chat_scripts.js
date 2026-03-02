/* ─────────────────────────────────────────────────────────────────────────
   chat_scripts.js
   Requires window.CHAT_CONFIG to be set by the template before this file
   is loaded:
     window.CHAT_CONFIG = { interviewId, csrfToken,
                            patientModel, patientTemperature,
                            interviewerModel, interviewerTemperature }
   ───────────────────────────────────────────────────────────────────────── */

const INTERVIEW_ID = window.CHAT_CONFIG.interviewId;
const CSRF         = window.CHAT_CONFIG.csrfToken;
const SEND_URL     = `/chat/${INTERVIEW_ID}/send/`;
const SETTINGS_URL = `/chat/${INTERVIEW_ID}/settings/`;
const NOTES_URL    = `/chat/${INTERVIEW_ID}/notes/`;
const AUTOGEN_URL  = `/chat/${INTERVIEW_ID}/autogenerate-question/`;

/* ── Initialise sliders and model selects from saved ChatSettings ── */
(function initSettings() {
  const cfg = window.CHAT_CONFIG;

  const tempSlider = document.getElementById('tempSlider');
  const tempValue  = document.getElementById('tempValue');
  if (tempSlider) { tempSlider.value = cfg.patientTemperature; }
  if (tempValue)  { tempValue.textContent = cfg.patientTemperature; }

  const modelSelect = document.getElementById('modelSelect');
  if (modelSelect) { modelSelect.value = cfg.patientModel; }

  const intSlider = document.getElementById('interviewerTempSlider');
  const intValue  = document.getElementById('interviewerTempValue');
  if (intSlider) { intSlider.value = cfg.interviewerTemperature; }
  if (intValue)  { intValue.textContent = cfg.interviewerTemperature; }

  const intModelSelect = document.getElementById('interviewerModelSelect');
  if (intModelSelect) { intModelSelect.value = cfg.interviewerModel; }
})();

/* ── Auto-grow textarea ── */
const msgInput = document.getElementById('messageInput');
msgInput.addEventListener('input', () => {
  msgInput.style.height = 'auto';
  msgInput.style.height = Math.min(msgInput.scrollHeight, 120) + 'px';
});

/* ── Scroll to bottom ── */
function scrollBottom() {
  const el = document.getElementById('chatMessages');
  el.scrollTop = el.scrollHeight;
}
scrollBottom();

/* ── Key handler ── */
function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

/* ── Append a message bubble ── */
function appendBubble(role, content, ts, dateLabel) {
  const empty = document.getElementById('emptyState');
  if (empty) empty.remove();

  const now     = new Date();
  const timeStr = ts || now.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
  const align   = role === 'user' ? 'text-end' : '';

  const dateSep = dateLabel
    ? `<div class="text-center my-2"><span style="font-size:.7rem;color:#adb5bd;background:#f8f9fa;padding:2px 10px;border-radius:20px;">${dateLabel}</span></div>`
    : '';

  const html = `${dateSep}
    <div class="msg-row msg-${role}">
      <div>
        <div class="msg-bubble">${escHtml(content)}</div>
        <div class="msg-ts ${align}">${timeStr}</div>
      </div>
    </div>`;

  const indicator = document.getElementById('typingIndicator');
  indicator.insertAdjacentHTML('beforebegin', html);
  scrollBottom();
}

function escHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/\n/g, '<br>');
}

/* ── Typing indicator ── */
function showTyping() {
  document.getElementById('typingIndicator').style.display = 'flex';
  scrollBottom();
}
function hideTyping() {
  document.getElementById('typingIndicator').style.display = 'none';
}

/* ── Auto-send helpers ── */
let autoSendRunning = false;
let ignoreNextAutogen = false;

function setInputBarDisabled(disabled) {
  const sendBtn    = document.getElementById('sendBtn');
  const autoGenBtn = document.getElementById('autoGenBtn');
  const toneSelect = document.getElementById('toneSelect');
  const icon       = document.getElementById('sendIcon');

  msgInput.disabled    = disabled;
  toneSelect.disabled  = disabled;
  if (autoGenBtn) { autoGenBtn.disabled = disabled; autoGenBtn.style.opacity = disabled ? '0.5' : '1'; }

  msgInput.style.opacity   = disabled ? '0.5' : '1';
  toneSelect.style.opacity = disabled ? '0.5' : '1';

  if (disabled) {
    icon.className = 'bi bi-stop-circle-fill';
    sendBtn.classList.remove('btn-primary');
    sendBtn.classList.add('btn-danger');
    sendBtn.disabled = false;          // stop button must always be clickable
    sendBtn.title    = 'Stop';
    sendBtn.onclick  = stopAutoSend;
  } else {
    icon.className = 'bi bi-send-fill';
    sendBtn.classList.remove('btn-danger');
    sendBtn.classList.add('btn-primary');
    sendBtn.disabled = false;
    sendBtn.title    = 'Send';
    sendBtn.onclick  = sendMessage;
  }
}

function stopAutoSend() {
  autoSendRunning   = false;
  ignoreNextAutogen = true;   // discard the in-flight autogen response if one is pending
  const autoGenToggle = document.getElementById('autoGenToggle');
  const warning       = document.getElementById('autoGenWarning');
  if (autoGenToggle) autoGenToggle.checked = false;
  if (warning) warning.style.display = 'none';
  setInputBarDisabled(false);
}

function onAutoGenToggleChange(checkbox) {
  const warning = document.getElementById('autoGenWarning');
  if (checkbox.checked) {
    if (warning) warning.style.display = 'flex';
    autoSendRunning = true;
    setInputBarDisabled(true);
    triggerAutogenQuestion(true);
  } else {
    stopAutoSend();
  }
}


/* ── Send message ── */
async function sendMessage() {
  const content = msgInput.value.trim();
  if (!content) return;

  const tone    = document.getElementById('toneSelect').value;
  const sendBtn = document.getElementById('sendBtn');

  appendBubble('user', content);
  msgInput.value = '';
  msgInput.style.height = 'auto';
  sendBtn.disabled = true;

  showTyping();

  try {
    const fd = new FormData();
    fd.append('message', content);
    fd.append('tone', tone);
    fd.append('csrfmiddlewaretoken', CSRF);

    const res  = await fetch(SEND_URL, { method: 'POST', body: fd });
    const data = await res.json();

    hideTyping();

    if (data.error) {
      appendBubble('system', '⚠ ' + data.error);
      sendBtn.disabled = false;
      return;
    }

    appendBubble('patient', data.response);

    const autoGenToggle = document.getElementById('autoGenToggle');
    if (autoGenToggle && autoGenToggle.checked) {
      autoSendRunning = true;
      setInputBarDisabled(true);
      await triggerAutogenQuestion(true);
      return;
    }

  } catch (err) {
    hideTyping();
    appendBubble('system', '⚠ Network error — please try again.');
  } finally {
    if (!autoSendRunning) {
      sendBtn.disabled = false;
      msgInput.focus();
    }
  }
}

/* ── Autogenerate question ── */
async function triggerAutogenQuestion(autoSend = false) {
  ignoreNextAutogen = false;   // clear any stale cancel flag from a previous stop
  // Disable bar while fetching (no patient typing indicator — that's only for patient replies)
  setInputBarDisabled(true);

  // In manual mode the stop icon would be confusing — keep it looking like send (but disabled)
  if (!autoSend) {
    const icon    = document.getElementById('sendIcon');
    const sendBtn = document.getElementById('sendBtn');
    icon.className = 'bi bi-send-fill';
    sendBtn.classList.remove('btn-danger');
    sendBtn.classList.add('btn-primary');
    sendBtn.title    = 'Send';
    sendBtn.disabled = true;
    sendBtn.onclick  = sendMessage;
  }

  try {
    const res  = await fetch(AUTOGEN_URL, { method: 'POST', headers: { 'X-CSRFToken': CSRF } });
    const data = await res.json();

    if (data.question) {
      // Stop was pressed while this fetch was in-flight — discard the result
      if (ignoreNextAutogen) {
        ignoreNextAutogen = false;
        setInputBarDisabled(false);
        return;
      }

      msgInput.value = data.question;
      msgInput.style.height = 'auto';
      msgInput.style.height = Math.min(msgInput.scrollHeight, 120) + 'px';

      if (autoSend && autoSendRunning) {
        // Temporarily re-enable msgInput so sendMessage() can read it,
        // then sendMessage will take over the disable/enable cycle
        msgInput.disabled = false;
        await sendMessage();
      } else {
        // Manual click — restore bar and let the user review/edit
        setInputBarDisabled(false);
        msgInput.focus();
      }
    } else {
      setInputBarDisabled(false);
    }

  } catch (e) {
    appendBubble('system', '⚠ Could not autogenerate question.');
    setInputBarDisabled(false);
  }
}

/* ── Patient settings ── */
const tempSlider = document.getElementById('tempSlider');
const tempVal    = document.getElementById('tempValue');
tempSlider.addEventListener('input', () => { tempVal.textContent = tempSlider.value; });

async function updateSettings() {
  const btn = document.getElementById('updateSettingsBtn');
  btn.disabled  = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Saving…';

  try {
    await fetch(SETTINGS_URL, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF },
      body: JSON.stringify({
        temperature: parseFloat(tempSlider.value),
        model:       document.getElementById('modelSelect').value,
        settings_id: 'patient',
      }),
    });
    const status = document.getElementById('settingsSaveStatus');
    status.style.display = 'block';
    setTimeout(() => { status.style.display = 'none'; }, 2500);
  } catch (e) {
    alert('Failed to save settings.');
  } finally {
    btn.disabled  = false;
    btn.innerHTML = '<i class="bi bi-check2-circle me-1"></i> Update';
  }
}

/* ── Interviewer settings ── */
const interviewerTempSlider = document.getElementById('interviewerTempSlider');
const interviewerTempVal    = document.getElementById('interviewerTempValue');
interviewerTempSlider.addEventListener('input', () => {
  interviewerTempVal.textContent = interviewerTempSlider.value;
});

async function updateInterviewerSettings() {
  const btn = document.getElementById('updateInterviewerSettingsBtn');
  btn.disabled  = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Saving…';

  try {
    await fetch(SETTINGS_URL, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF },
      body: JSON.stringify({
        temperature: parseFloat(interviewerTempSlider.value),
        model:       document.getElementById('interviewerModelSelect').value,
        settings_id: 'interviewer',
      }),
    });
    const status = document.getElementById('interviewerSettingsSaveStatus');
    status.style.display = 'block';
    setTimeout(() => { status.style.display = 'none'; }, 2500);
  } catch (e) {
    alert('Failed to save settings.');
  } finally {
    btn.disabled  = false;
    btn.innerHTML = '<i class="bi bi-check2-circle me-1"></i> Update';
  }
}

/* ── Notes auto-save ── */
let notesTimer   = null;
const notesArea   = document.getElementById('notesTextarea');
const notesStatus = document.getElementById('notesSaveStatus');

notesArea.addEventListener('input', () => {
  notesStatus.textContent = '';
  clearTimeout(notesTimer);
  notesTimer = setTimeout(saveNotes, 1500);
});

async function saveNotes() {
  try {
    const res = await fetch(NOTES_URL, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF },
      body:    JSON.stringify({ notes: notesArea.value }),
    });
    if (res.ok) {
      notesStatus.textContent = 'Changes saved';
      notesStatus.style.color = '#198754';
    }
  } catch (e) {
    notesStatus.textContent = 'Save failed';
    notesStatus.style.color = '#dc3545';
  }
}
