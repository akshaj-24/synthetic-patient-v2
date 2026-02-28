const sectionFields = {
    identity:   [
      { id: 'name',       deps: ['gender'] },
      { id: 'age',        deps: [] },
      { id: 'gender',     deps: [] },
      { id: 'ethnicity',  deps: [] },
      { id: 'marital_status', deps: ['age'] },
      { id: 'education',  deps: ['age'] },
      { id: 'occupation', deps: ['education'] },
    ],
    clinical: [
      { id: 'disorder',      deps: [] },
      { id: 'type',          deps: ['disorder'] },
      { id: 'base_emotions', deps: ['disorder', 'type'] },
      { id: 'intake',        deps: ['disorder', 'type', 'base_emotions', 'name', 'age', 'gender', 'occupation', 'trigger'] },
    ],
    cbt: [
      { id: 'helpless_beliefs',    deps: ['disorder', 'type', 'base_emotions'] },
      { id: 'unlovable_beliefs',   deps: ['helpless_beliefs'] },
      { id: 'worthless_beliefs',   deps: ['unlovable_beliefs'] },
      { id: 'intermediate_belief', deps: ['helpless_beliefs', 'unlovable_beliefs', 'worthless_beliefs'] },
      { id: 'trigger',             deps: ['disorder', 'intermediate_belief'] },
      { id: 'auto_thoughts',       deps: ['trigger', 'intermediate_belief', 'base_emotions'] },
      { id: 'coping_strategies',   deps: ['auto_thoughts', 'disorder', 'intake'] },
      { id: 'behavior',            deps: ['auto_thoughts', 'base_emotions', 'coping_strategies'] },
    ],
    background: [
      { id: 'childhood_history',    deps: ['disorder', 'name', 'age', 'occupation', 'intake'] },
      { id: 'education_history',    deps: ['disorder', 'name', 'age', 'occupation', 'intake'] },
      { id: 'occupation_history',   deps: ['disorder', 'name', 'age', 'occupation', 'intake'] },
      { id: 'relationship_history', deps: ['disorder', 'name', 'age', 'occupation', 'intake'] },
      { id: 'medical_history',      deps: ['disorder', 'name', 'age', 'occupation', 'intake'] },
      { id: 'personal_history',     deps: ['disorder', 'name', 'age', 'occupation', 'intake'] },
      { id: 'family_tree',          deps: ['name', 'childhood_history', 'education_history', 'occupation_history', 'relationship_history', 'medical_history', 'personal_history', 'disorder'] },
      { id: 'timeline',             deps: ['childhood_history', 'education_history', 'occupation_history', 'relationship_history', 'medical_history', 'personal_history', 'family_tree', 'age'] },
      { id: 'session_history',      deps: ['disorder', 'intake'] },
      ],
    narrative: [
      { id: 'vignette', deps: ['name', 'age', 'disorder', 'childhood_history', 'education_history', 'occupation_history', 'relationship_history', 'medical_history', 'personal_history', 'intake'] },
    ],
  };

  function getDeps(fieldId) {
  for (const section of Object.values(sectionFields)) {
    const entry = section.find(f => f.id === fieldId);
    if (entry) return entry.deps;
  }
  return [];
}

// ══════════ FIELD GENERATION ══════════
  async function generateField(fieldId, dependencies) {
    let firstMissing = null;
    for (const dep of dependencies) {
      const depEl = document.getElementById(dep);
      if (!depEl || !depEl.value.trim()) {
        depEl.classList.add('is-invalid-dep');
        if (!firstMissing) firstMissing = depEl;
      } else {
        depEl.classList.remove('is-invalid-dep');
      }
    }
    if (firstMissing) {
      firstMissing.scrollIntoView({ behavior: 'smooth', block: 'center' });
      firstMissing.focus();
      return;
    }

    const el = document.getElementById(fieldId);
    if (!el) return;
    setLoading(el, true);

    const depValues = {};
    dependencies.forEach(dep => depValues[dep] = document.getElementById(dep).value);

    try {
      const res = await fetch(`/chat/generate/field/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({ field: fieldId, dependencies: depValues })
      });
      const data = await res.json();
      if (el.tagName === 'SELECT') {
        const opt = [...el.options].find(o => o.value === data.value || o.text === data.value);
        if (opt) el.value = opt.value;
      } else {
        el.value = data.value;
      }
      el.classList.remove('is-invalid-dep');
    } catch (e) {
      alert('Generation failed. Try again.');
    } finally {
      setLoading(el, false);
    }
  }

  async function autogenerateSection(section) {
    for (const f of sectionFields[section]) await generateField(f.id, f.deps);
  }

  async function autogenerateAll() {
    for (const section of Object.keys(sectionFields)) await autogenerateSection(section);
  }

  function setLoading(el, loading) {
    if (loading) {
      el.classList.add('field-loading');
      el.disabled = true;
      if (el.tagName !== 'SELECT') el.placeholder = 'Generating...';
    } else {
      el.classList.remove('field-loading');
      el.disabled = false;
    }
  }

  // ══════════ PATIENT MODAL ══════════
  let allPatients   = [];
  let filteredPatients = [];
  let sortCol       = 'createdAt';
  let sortDir       = -1;   // -1 = desc, 1 = asc
  let onlyMine      = false;

  const patientModal = new bootstrap.Modal(document.getElementById('patientModal'));
  const profileModal = new bootstrap.Modal(document.getElementById('profileModal'));

  async function openPatientModal() {
    patientModal.show();
    await fetchPatients();
  }

async function quickCopy(patientId) {
    const res  = await fetch(`/chat/patients/${patientId}/`);
    const data = await res.json();
    fillForm(data);
    patientModal.hide();
}

async function quickLoad(patientId) {
    const res  = await fetch(`/chat/patients/${patientId}/`);
    const data = await res.json();
    fillForm(data);
    patientModal.hide();
}

  async function fetchPatients() {
    const url = `/chat/patients/list/?mine=${onlyMine ? 1 : 0}`;
    const res  = await fetch(url);
    const data = await res.json();
    allPatients = data.patients;
    applyFilterAndSort();
  }

  function toggleMyPatients() {
    onlyMine = document.getElementById('myPatientsToggle').checked;
    fetchPatients();
  }

  document.getElementById('patientSearch').addEventListener('input', function () {
    applyFilterAndSort();
  });

  function applyFilterAndSort() {
    const q = document.getElementById('patientSearch').value.toLowerCase();
    filteredPatients = allPatients.filter(p =>
      (p.name       || '').toLowerCase().includes(q) ||
      (p.disorder   || '').toLowerCase().includes(q) ||
      (p.profile_summary    || '').toLowerCase().includes(q) ||
      (p.gender     || '').toLowerCase().includes(q) ||
      (p.createdBy || '').toLowerCase().includes(q)
    );
    sortData();
    renderPatientTable(filteredPatients);
  }

  function sortTable(col) {
    if (sortCol === col) {
      sortDir *= -1;
    } else {
      sortCol = col;
      sortDir = 1;
    }
    // Update sort icons
    document.querySelectorAll('.sort-icon').forEach(el => el.classList.remove('active'));
    const icon = document.getElementById(`sort-${col}`);
    if (icon) {
      icon.classList.add('active');
      icon.className = icon.className.replace(/bi-arrow-\S+/, sortDir === 1 ? 'bi-arrow-up' : 'bi-arrow-down');
    }
    sortData();
    renderPatientTable(filteredPatients);
  }

  function sortData() {
    filteredPatients.sort((a, b) => {
      const aVal = (a[sortCol] ?? '').toString().toLowerCase();
      const bVal = (b[sortCol] ?? '').toString().toLowerCase();
      // Numeric sort for age
      if (sortCol === 'age') return sortDir * ((parseInt(a.age) || 0) - (parseInt(b.age) || 0));
      return sortDir * aVal.localeCompare(bVal);
    });
  }

function renderPatientTable(patients) {
    const tbody = document.getElementById('patientTableBody');
    if (!patients.length) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted py-4">No patients found.</td></tr>';
        return;
    }
    tbody.innerHTML = patients.map(p => {
        const summary = p.profile_summary || '—';
        const isLong = summary.length > 40;
        const preview = isLong ? summary.slice(0, 40) + '...' : summary;
        const id = `summary-${p.id}`;
        return `
        <tr>
            <td>${p.name || '—'}</td>
            <td>${p.age || '—'}</td>
            <td>${p.gender || '—'}</td>
            <td>${p.disorder || '—'}</td>
            <td style="max-width:220px;">
                <div class="d-flex justify-content-between align-items-start gap-1">
                    <div>
                        <span id="${id}-preview">${preview}</span>
                        <span id="${id}-full" style="display:none; white-space:pre-wrap;">${summary}</span>
                    </div>
                    ${isLong ? `
                    <a href="#" id="${id}-toggle" class="text-muted ms-1 flex-shrink-0" onclick="toggleSummary('${id}', event)">
                        <i id="${id}-icon" class="bi bi-chevron-down"></i>
                    </a>` : ''}
                </div>
            </td>
            <td>${p.createdBy || '—'}</td>
            <td>${p.createdAt || '—'}</td>
            <td>
                <div class="d-flex gap-1">
                    <button class="btn btn-sm btn-outline-secondary" title="View Profile" onclick="openProfile(${p.id})">
                        <i class="bi bi-box-arrow-up-right"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-dark" title="Copy to form" onclick="quickCopy(${p.id})">
                        <i class="bi bi-copy"></i>
                    </button>
                    <button class="btn btn-sm btn-dark" title="Load patient" onclick="quickLoad(${p.id})">
                        <i class="bi bi-box-arrow-in-right"></i>
                    </button>
                </div>
            </td>
        </tr>`;
    }).join('');
}

function toggleSummary(id, event) {
    event.preventDefault();
    const preview = document.getElementById(`${id}-preview`);
    const full    = document.getElementById(`${id}-full`);
    const icon    = document.getElementById(`${id}-icon`);
    const isHidden = full.style.display === 'none';
    full.style.display    = isHidden ? 'inline' : 'none';
    preview.style.display = isHidden ? 'none'   : 'inline';
    icon.className        = isHidden ? 'bi bi-chevron-up' : 'bi bi-chevron-down';
}




  // ══════════ PROFILE MODAL ══════════
  async function openProfile(patientId) {
    const res  = await fetch(`/chat/patients/${patientId}/`);
    const data = await res.json();

    document.getElementById('profileModalBody').innerHTML = renderProfile(data);
    document.getElementById('loadPatientBtn').onclick = () => { loadPatient(data); };
    document.getElementById('copyPatientBtn').onclick = () => { copyPatient(data); };

    patientModal.hide();
    profileModal.show();
  }


  function renderProfile(p) {
    const f = (label, val) => {
        if (!val && val !== 0) return '';
        const display = Array.isArray(val) ? val.join(', ') : val;
        return `<div class="profile-label">${label}</div>
                <div class="profile-value" style="word-break:break-word;white-space:pre-wrap;">${display}</div>`;
    };
      return `
          <h5 class="mb-3">${p.name || 'Unknown Patient'}</h5>
          <div class="row">
              <div class="col-md-6">
                  ${f('Age', p.age)} ${f('Gender', p.gender)} ${f('Ethnicity', p.ethnicity)} ${f('Marital Status', p.marital_status)}
                  ${f('Education', p.education)} ${f('Occupation', p.occupation)}
                  ${f('Disorder', p.disorder)} ${f('Patient Type', p.type)}
                  ${f('Starting Emotions', p.base_emotions)}
              </div>
              <div class="col-md-6">
                  ${f('Helpless Beliefs', p.helpless_beliefs)}
                  ${f('Unlovable Beliefs', p.unlovable_beliefs)}
                  ${f('Worthless Beliefs', p.worthless_beliefs)}
                  ${f('Intermediate Belief', p.intermediate_belief)}
                  ${f('Profile Summary', p.profile_summary)}
                  ${f('Automatic Thoughts', p.auto_thoughts)}
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
          ${f('Session History', p.session_history)}
          ${f('Family Tree', p.family_tree)}
          ${f('Timeline', p.timeline)}
          <hr>
          ${f('Intake', p.intake)}
          ${f('Vignette', p.vignette)}
          <hr>
          <small class="text-muted">Created by ${p.createdBy} on ${p.createdAt}</small>
      `;
  }


  function backToPatientList() {
    profileModal.hide();
    patientModal.show();
  }

  function loadPatient(p)  { fillForm(p); profileModal.hide(); patientModal.hide(); }
  function copyPatient(p)  { fillForm(p); profileModal.hide(); patientModal.hide(); }

  function fillForm(p) {
      const set = (id, val) => {
          const el = document.getElementById(id);
          if (!el || val === undefined || val === null) return;
          if (el.tagName === 'SELECT') {
              const opt = [...el.options].find(o => o.value === val || o.text === val);
              if (opt) el.value = opt.value;
          } else {
              el.value = Array.isArray(val) ? val.join(', ') : val;
          }
      };
      [
          'name', 'age', 'gender', 'ethnicity', 'marital_status', 'education', 'occupation',
          'disorder', 'type', 'base_emotions', 'intake',
          'helpless_beliefs', 'unlovable_beliefs', 'worthless_beliefs',
          'intermediate_belief', 'trigger', 'auto_thoughts',
          'coping_strategies', 'behavior',
          'childhood_history', 'education_history', 'occupation_history',
          'relationship_history', 'medical_history', 'personal_history', 'session_history',
          'family_tree', 'timeline', 'vignette'
      ].forEach(field => set(field, p[field]));
  }


  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }