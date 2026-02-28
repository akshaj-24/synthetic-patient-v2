let allInterviews = [];
  let filtered      = [];
  let sortCol       = 'createdAt';
  let sortDir       = -1;
//   const isSuperuser = {{ request.user.is_superuser|yesno:"true,false" }};


  const previewModal        = new bootstrap.Modal(document.getElementById('previewModal'));
  const patientProfileModal = new bootstrap.Modal(document.getElementById('patientProfileModal'));
  const archiveModal        = new bootstrap.Modal(document.getElementById('archiveModal'));
  const deleteModal         = new bootstrap.Modal(document.getElementById('deleteModal'));


  // ── Fetch ──
  async function fetchInterviews() {
    const mine     = document.getElementById('mineToggle').checked ? 1 : 0;
    const archived = document.getElementById('archivedToggle').checked ? 1 : 0;
    const res  = await fetch(`/chat/list/api/?mine=${mine}&archived=${archived}`);
    const data = await res.json();
    allInterviews = data.interviews;
    applyFilterAndSort();
  }


  // ── Filter + Sort ──
  document.getElementById('searchInput').addEventListener('input', applyFilterAndSort);


  function applyFilterAndSort() {
    const q = document.getElementById('searchInput').value.toLowerCase();
    filtered = allInterviews.filter(i =>
      (i.title        || '').toLowerCase().includes(q) ||
      (i.patient_name || '').toLowerCase().includes(q) ||
      (i.disorder     || '').toLowerCase().includes(q) ||
      (i.createdBy    || '').toLowerCase().includes(q) ||
      String(i.id).includes(q)
    );
    sortData();
    renderTable();
  }


  function sortTable(col) {
    sortDir = sortCol === col ? sortDir * -1 : 1;
    sortCol = col;
    document.querySelectorAll('[id^="sort-"]').forEach(el => {
      el.className = 'bi bi-arrow-down-up';
      el.style.color = '#aaa';
    });
    const icon = document.getElementById(`sort-${col}`);
    if (icon) {
      icon.className = `bi ${sortDir === 1 ? 'bi-arrow-up' : 'bi-arrow-down'}`;
      icon.style.color = '#000';
    }
    sortData();
    renderTable();
  }


  function sortData() {
    filtered.sort((a, b) => {
      if (sortCol === 'id' || sortCol === 'turn_count')
        return sortDir * ((a[sortCol] || 0) - (b[sortCol] || 0));
      return sortDir * (a[sortCol] || '').toString().localeCompare((b[sortCol] || '').toString());
    });
  }


  // ── Render ──
  function renderTable() {
    const tbody = document.getElementById('interviewTableBody');
    if (!filtered.length) {
      tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted py-4">No sessions found.</td></tr>';
      return;
    }
    const canAct = (i) => i.is_mine || isSuperuser;


    tbody.innerHTML = filtered.map(i => `
      <tr class="${i.archived ? 'table-secondary' : ''}">
        <td class="text-muted small">#${i.id}</td>
        <td>
          ${i.title}
          ${i.archived ? '<span class="badge bg-secondary ms-1" style="font-size:.7rem">Archived</span>' : ''}
        </td>
        <td class="small">${i.createdBy}</td>
        <td>
          ${i.patient_name}
          ${i.patient_id ? `<button class="btn btn-link btn-sm p-0 ms-1" title="View Patient" onclick="openPatientProfile(${i.patient_id})">
            <i class="bi bi-person-badge"></i></button>` : ''}
        </td>
        <td class="small">${i.disorder}</td>
        <td class="text-center">${i.turn_count}</td>
        <td class="small">${i.createdAt}</td>
        <td class="small">${i.updated_at}</td>
        <td>
          <div class="d-flex gap-1">
            <button class="btn btn-sm btn-outline-secondary" title="Preview" onclick="openPreview(${i.id})">
              <i class="bi bi-chat-left-text"></i>
            </button>
            <a href="/chat/${i.id}/" class="btn btn-sm btn-dark" title="Load">
              <i class="bi bi-box-arrow-in-right"></i>
            </a>
            <button class="btn btn-sm btn-outline-secondary ${canAct(i) ? '' : 'disabled'}"
                    title="${i.archived ? 'Unarchive' : 'Archive'}"
                    ${canAct(i) ? `onclick="confirmArchive(${i.id}, ${i.archived})"` : 'disabled'}>
              <i class="bi ${i.archived ? 'bi-archive-fill' : 'bi-archive'}"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger ${canAct(i) ? '' : 'disabled'}"
                    title="Delete"
                    ${canAct(i) ? `onclick="confirmDelete(${i.id})"` : 'disabled'}>
              <i class="bi bi-trash"></i>
            </button>
          </div>
        </td>
      </tr>
    `).join('');
  }


  // ── Preview Modal ──
  async function openPreview(interviewId) {
    document.getElementById('previewModalBody').innerHTML = 'Loading...';
    previewModal.show();
    const res  = await fetch(`/chat/${interviewId}/preview/`);
    const data = await res.json();
    if (!data.messages.length) {
      document.getElementById('previewModalBody').innerHTML = '<p class="text-muted">No messages yet.</p>';
      return;
    }
    const roleBg = { user: '#e9ecef', patient: '#d1ecf1', system: '#fff3cd' };
    document.getElementById('previewModalBody').innerHTML = `
      <p class="text-muted small mb-3">Showing last ${data.messages.length} of ${data.total} messages</p>
      ${data.messages.map(m => `
        <div class="mb-2 p-2 rounded small" style="background:${roleBg[m.role] || '#e9ecef'}">
          <strong class="text-capitalize">${m.role}</strong>
          <span class="text-muted ms-2">${m.timestamp}</span>
          <div class="mt-1">${m.content}</div>
        </div>
      `).join('')}
    `;
  }


  // ── Patient Profile Modal ──
  async function openPatientProfile(patientId) {
    document.getElementById('patientProfileBody').innerHTML = 'Loading...';
    patientProfileModal.show();
    const res = await fetch(`/chat/patients/${patientId}/`);
    const p   = await res.json();
    const f = (label, val) => {
      if (!val && val !== 0) return '';
      const display = Array.isArray(val) ? val.join(', ') : val;
      return `<div class="text-muted small fw-bold text-uppercase mb-0">${label}</div>
              <div class="mb-2" style="word-break:break-word;white-space:pre-wrap;">${display}</div>`;
    };
    document.getElementById('patientProfileBody').innerHTML = `
      <h5>${p.name || 'Unknown'}</h5>
      <div class="row">
        <div class="col-md-6">
          ${f('Age', p.age)}${f('Gender', p.gender)}${f('Ethnicity', p.ethnicity)}
          ${f('Education', p.education)}${f('Occupation', p.occupation)}
          ${f('Disorder', p.disorder)}${f('Type', p.type)}
          ${f('Emotions', p.base_emotions)}
        </div>
        <div class="col-md-6">
          ${f('Helpless Beliefs', p.helpless_beliefs)}
          ${f('Unlovable Beliefs', p.unlovable_beliefs)}
          ${f('Worthless Beliefs', p.worthless_beliefs)}
          ${f('Intermediate Belief', p.intermediate_belief)}
          ${f('Trigger', p.trigger)}
          ${f('Auto Thoughts', p.auto_thoughts)}
          ${f('Coping Strategies', p.coping_strategies)}
          ${f('Behavior', p.behavior)}
        </div>
      </div>
      <hr>
      <h6 class="text-muted small fw-bold text-uppercase">Background & History</h6>
      ${f('Childhood History', p.childhood_history)}
      ${f('Education History', p.education_history)}
      ${f('Occupation History', p.occupation_history)}
      ${f('Relationship History', p.relationship_history)}
      ${f('Medical History', p.medical_history)}
      ${f('Personal History', p.personal_history)}
      ${f('Family Tree', p.family_tree)}
      ${f('Timeline', p.timeline)}
      <hr>
      ${f('Intake', p.intake)}
      ${f('Vignette', p.vignette)}
    `;
  }



  // ── Archive Confirm ──
  let pendingArchiveId      = null;
  let pendingArchiveState   = null;


  function confirmArchive(interviewId, isArchived) {
    pendingArchiveId    = interviewId;
    pendingArchiveState = isArchived;
    const action = isArchived ? 'Unarchive' : 'Archive';
    document.getElementById('archiveModalTitle').textContent = `${action} Session`;
    document.getElementById('archiveModalBody').textContent  = `Are you sure you want to ${action.toLowerCase()} this session?`;
    document.getElementById('confirmArchiveBtn').textContent = action;
    archiveModal.show();
  }


  document.getElementById('confirmArchiveBtn').addEventListener('click', async () => {
    if (!pendingArchiveId) return;
    const res  = await fetch(`/chat/${pendingArchiveId}/archive/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') }
    });
    const data = await res.json();
    archiveModal.hide();
    if (data.archived !== undefined) fetchInterviews();
  });


  // ── Delete Confirm ──
  let pendingDeleteId = null;


  function confirmDelete(interviewId) {
    pendingDeleteId = interviewId;
    deleteModal.show();
  }


  document.getElementById('confirmDeleteBtn').addEventListener('click', async () => {
    if (!pendingDeleteId) return;
    const res  = await fetch(`/chat/${pendingDeleteId}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') }
    });
    const data = await res.json();
    deleteModal.hide();
    if (data.deleted) fetchInterviews();
  });


  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }


  // ── Init ──
  fetchInterviews();