// TJC Attendance Portal - Client Application Logic
// St. Joseph's College - The Josephite Choir

const API_BASE = '/api';
const CATEGORIES = ["Alto", "Bass", "Soprano", "Tenor", "Band", "Conductors"];

// Global App State
let state = {
  adminPin: localStorage.getItem('tjc_admin_pin') || '',
  allStudents: [],
  attendanceMap: {}, // reg_no -> boolean (true=present, false=absent)
  currentMarkCategory: 'All Parts',
  currentCreditsCategory: 'All Parts',
  selectedEventId: null,
  currentEventRoster: [],
  allCreditsRows: [],
  pendingPinAction: null
};

// Initialize Application on Page Load
document.addEventListener('DOMContentLoaded', () => {
  // Setup Lucide icons
  lucide.createIcons();

  // Check stored Admin PIN status
  checkAdminAuth();

  // Set today's date in date pickers
  const todayStr = new Date().toISOString().split('T')[0];
  const markDateInput = document.getElementById('markEventDate');
  const viewerDateInput = document.getElementById('viewerDateInput');
  if (markDateInput) markDateInput.value = todayStr;
  if (viewerDateInput) viewerDateInput.value = todayStr;

  // Load Initial Dashboard
  loadDashboardData();
  initMarkCategories();
  initCreditsCategories();
});

// ================= UI HELPERS & NOTIFICATIONS =================

function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `pointer-events-auto flex items-center gap-2 px-4 py-3 rounded-xl shadow-xl text-sm font-semibold border transition-all duration-300 transform translate-y-2 opacity-0 ${
    type === 'success' ? 'bg-emerald-800 text-white border-emerald-600' :
    type === 'error' ? 'bg-rose-800 text-white border-rose-600' :
    'bg-slate-800 text-white border-slate-600'
  }`;

  const iconName = type === 'success' ? 'check-circle' : type === 'error' ? 'alert-triangle' : 'info';
  toast.innerHTML = `<i data-lucide="${iconName}" class="w-4 h-4"></i> <span>${message}</span>`;
  container.appendChild(toast);
  lucide.createIcons();

  // Animate in
  setTimeout(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  }, 10);

  // Auto remove after 3.5s
  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function getAuthHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  if (state.adminPin) {
    headers['X-Admin-PIN'] = state.adminPin;
  }
  return headers;
}

// ================= NAVIGATION =================

function switchTab(tabId) {
  const tabs = ['home', 'mark', 'viewer', 'credits', 'members'];
  tabs.forEach(t => {
    const section = document.getElementById(`tab-${t}`);
    const navBtn = document.getElementById(`nav-${t}`);
    if (section) {
      if (t === tabId) {
        section.classList.remove('hidden');
      } else {
        section.classList.add('hidden');
      }
    }
    if (navBtn) {
      if (t === tabId) {
        navBtn.classList.add('bg-white/20', 'text-white', 'font-bold');
      } else {
        navBtn.classList.remove('bg-white/20', 'font-bold');
      }
    }
  });

  window.scrollTo({ top: 0, behavior: 'smooth' });
  lucide.createIcons();

  // Refresh tab-specific data
  if (tabId === 'home') loadDashboardData();
  if (tabId === 'mark') loadMarkTab();
  if (tabId === 'viewer') loadViewerTab();
  if (tabId === 'credits') loadCreditsLedger(state.currentCreditsCategory);
  if (tabId === 'members') loadMembersList();
}

function toggleMobileMenu() {
  const menu = document.getElementById('mobileMenu');
  if (menu) menu.classList.toggle('hidden');
}

// ================= AUTHENTICATION & PIN MODAL =================

async function checkAdminAuth() {
  const statusBtn = document.getElementById('adminStatusBtn');
  const lockIcon = document.getElementById('adminLockIcon');
  const statusText = document.getElementById('adminStatusText');

  if (!state.adminPin) {
    if (statusText) statusText.textContent = 'Admin PIN';
    if (statusBtn) statusBtn.className = 'flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-white/10 text-white border border-white/20 hover:bg-white/20 transition-all shadow-sm';
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/auth/status`, { headers: getAuthHeaders() });
    const data = await res.json();
    if (data.is_authenticated) {
      if (statusText) statusText.textContent = 'Unlocked';
      if (statusBtn) statusBtn.className = 'flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-600/90 text-white border border-emerald-400 hover:bg-emerald-600 transition-all shadow-sm';
      if (lockIcon) lockIcon.setAttribute('data-lucide', 'unlock');
      lucide.createIcons();
    } else {
      state.adminPin = '';
      localStorage.removeItem('tjc_admin_pin');
      if (statusText) statusText.textContent = 'Admin PIN';
    }
  } catch (err) {
    console.error('Auth check error:', err);
  }
}

function openPinModal(callback = null) {
  state.pendingPinAction = callback;
  const modal = document.getElementById('pinModal');
  const pinInput = document.getElementById('adminPinInput');
  const errorMsg = document.getElementById('pinErrorMsg');
  if (errorMsg) errorMsg.classList.add('hidden');
  if (pinInput) {
    pinInput.value = '';
    setTimeout(() => pinInput.focus(), 100);
  }
  if (modal) modal.classList.remove('hidden');
}

function closePinModal() {
  const modal = document.getElementById('pinModal');
  if (modal) modal.classList.add('hidden');
  state.pendingPinAction = null;
}

async function verifyAndSavePin() {
  const pinInput = document.getElementById('adminPinInput');
  const errorMsg = document.getElementById('pinErrorMsg');
  const remember = document.getElementById('rememberPin').checked;
  const pin = pinInput.value.trim();

  if (!pin) {
    errorMsg.textContent = 'Please enter a PIN.';
    errorMsg.classList.remove('hidden');
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/auth/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pin })
    });

    if (res.ok) {
      state.adminPin = pin;
      if (remember) {
        localStorage.setItem('tjc_admin_pin', pin);
      }
      closePinModal();
      checkAdminAuth();
      showToast('Admin Mode unlocked!');

      if (typeof state.pendingPinAction === 'function') {
        const action = state.pendingPinAction;
        state.pendingPinAction = null;
        action();
      }
    } else {
      errorMsg.textContent = 'Incorrect PIN. Please try again.';
      errorMsg.classList.remove('hidden');
    }
  } catch (e) {
    errorMsg.textContent = 'Network or server error verifying PIN.';
    errorMsg.classList.remove('hidden');
  }
}

// ================= VIEW 1: HOME / DASHBOARD =================

async function loadDashboardData() {
  try {
    // 1. Fetch Students count
    const studentsRes = await fetch(`${API_BASE}/students`);
    if (studentsRes.ok) {
      const students = await studentsRes.json();
      state.allStudents = students;
      const statElem = document.getElementById('statTotalMembers');
      if (statElem) statElem.textContent = `${students.length} Members`;
    }

    // 2. Fetch Events
    const eventsRes = await fetch(`${API_BASE}/events`);
    if (eventsRes.ok) {
      const events = await eventsRes.json();
      const statEventsElem = document.getElementById('statTotalEvents');
      if (statEventsElem) statEventsElem.textContent = `${events.length} Events`;

      // Render recent events list
      const recentContainer = document.getElementById('recentEventsList');
      if (recentContainer) {
        if (events.length === 0) {
          recentContainer.innerHTML = `
            <div class="py-6 text-center text-slate-400 text-sm">
              <i data-lucide="calendar-x" class="w-8 h-8 mx-auto mb-2 text-slate-300"></i>
              No events recorded yet. Click <strong>Mark Attendance</strong> above to record your first session!
            </div>
          `;
        } else {
          recentContainer.innerHTML = events.slice(0, 5).map(ev => `
            <div class="py-3 sm:py-4 flex items-center justify-between gap-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-tjcNavy/5 border border-tjcNavy/10 flex items-center justify-center font-bold text-tjcNavy text-xs">
                  ${ev.duration_hours}h
                </div>
                <div>
                  <h4 class="font-bold text-slate-800 text-sm">${ev.event_name}</h4>
                  <p class="text-xs text-slate-500">${ev.event_date}</p>
                </div>
              </div>
              <button onclick="inspectEventFromDashboard(${ev.event_id}, '${ev.event_date}')" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-tjcNavy hover:text-tjcGold transition-colors flex items-center gap-1">
                View Roster <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
              </button>
            </div>
          `).join('');
        }
        lucide.createIcons();
      }
    }
  } catch (err) {
    console.error('Error loading dashboard data:', err);
  }
}

function inspectEventFromDashboard(eventId, eventDate) {
  switchTab('viewer');
  const dateInput = document.getElementById('viewerDateInput');
  if (dateInput) dateInput.value = eventDate;
  loadEventsForDate(eventDate, eventId);
}

// ================= VIEW 2: MARK ATTENDANCE =================

function initMarkCategories() {
  const container = document.getElementById('markCategoryTabs');
  if (!container) return;

  const parts = ['All Parts', ...CATEGORIES];
  container.innerHTML = parts.map(part => `
    <button onclick="setMarkCategory('${part}')" id="markTab-${part.replace(/\s+/g, '')}" class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
      part === state.currentMarkCategory ? 'bg-tjcNavy text-tjcGold shadow-sm' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
    }">
      ${part}
    </button>
  `).join('');
}

function setMarkCategory(part) {
  state.currentMarkCategory = part;
  initMarkCategories();
  filterMarkRoster();
}

function applyPresetTitle(val) {
  if (!val) return;
  const nameInput = document.getElementById('markEventName');
  if (nameInput) nameInput.value = val;
}

async function loadMarkTab() {
  try {
    const res = await fetch(`${API_BASE}/students`);
    if (res.ok) {
      state.allStudents = await res.json();
      // Initialize attendance map if empty
      state.allStudents.forEach(s => {
        if (!(s.reg_no in state.attendanceMap)) {
          state.attendanceMap[s.reg_no] = false; // Default to absent until toggled
        }
      });
      filterMarkRoster();
      updateMarkCounters();
    }
  } catch (err) {
    showToast('Failed to load student roster', 'error');
  }
}

function filterMarkRoster() {
  const query = (document.getElementById('markSearchInput')?.value || '').trim().toLowerCase();
  const container = document.getElementById('markRosterContainer');
  if (!container) return;

  const filtered = state.allStudents.filter(s => {
    const matchesCategory = (state.currentMarkCategory === 'All Parts' || s.part === state.currentMarkCategory);
    const matchesSearch = (!query || s.student_name.toLowerCase().includes(query) || s.reg_no.toLowerCase().includes(query));
    return matchesCategory && matchesSearch;
  });

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="p-8 text-center text-slate-400 text-sm">
        <i data-lucide="user-x" class="w-8 h-8 mx-auto mb-2 text-slate-300"></i>
        No students found matching current filters.
      </div>
    `;
    lucide.createIcons();
    return;
  }

  // Render list of students
  container.innerHTML = filtered.map(s => {
    const isPresent = Boolean(state.attendanceMap[s.reg_no]);
    return `
      <div class="p-3.5 sm:p-4 flex items-center justify-between gap-4 hover:bg-slate-50 transition-colors">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-full ${isPresent ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-500'} flex items-center justify-center font-bold text-xs uppercase">
            ${s.student_name.slice(0, 2)}
          </div>
          <div>
            <h4 class="font-bold text-slate-900 text-sm leading-tight">${s.student_name.toUpperCase()}</h4>
            <div class="flex items-center gap-2 mt-0.5">
              <span class="text-xs text-slate-500 font-mono">${s.reg_no}</span>
              <span class="text-slate-300">&bull;</span>
              <span class="inline-block px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700">${s.part}</span>
            </div>
          </div>
        </div>

        <!-- Custom Switch Control -->
        <div class="flex items-center gap-2">
          <span class="text-xs font-semibold ${isPresent ? 'text-emerald-700' : 'text-slate-400'} hidden sm:inline">
            ${isPresent ? 'Present' : 'Absent'}
          </span>
          <label class="switch">
            <input type="checkbox" ${isPresent ? 'checked' : ''} onchange="toggleStudentAttendance('${s.reg_no}', this.checked)">
            <span class="slider"></span>
          </label>
        </div>
      </div>
    `;
  }).join('');

  lucide.createIcons();
}

function toggleStudentAttendance(regNo, isChecked) {
  state.attendanceMap[regNo] = Boolean(isChecked);
  updateMarkCounters();
}

function updateMarkCounters() {
  const total = state.allStudents.length;
  let present = 0;
  for (const reg in state.attendanceMap) {
    if (state.attendanceMap[reg]) present++;
  }
  const absent = total - present;

  const cntPresent = document.getElementById('cntPresent');
  const cntAbsent = document.getElementById('cntAbsent');
  const saveBarCount = document.getElementById('saveBarCount');

  if (cntPresent) cntPresent.textContent = present;
  if (cntAbsent) cntAbsent.textContent = absent;
  if (saveBarCount) saveBarCount.textContent = total;
}

function bulkSetAttendance(status) {
  const query = (document.getElementById('markSearchInput')?.value || '').trim().toLowerCase();
  state.allStudents.forEach(s => {
    const matchesCategory = (state.currentMarkCategory === 'All Parts' || s.part === state.currentMarkCategory);
    const matchesSearch = (!query || s.student_name.toLowerCase().includes(query) || s.reg_no.toLowerCase().includes(query));
    if (matchesCategory && matchesSearch) {
      state.attendanceMap[s.reg_no] = status;
    }
  });
  filterMarkRoster();
  updateMarkCounters();
}

async function submitAttendance() {
  const eventName = (document.getElementById('markEventName')?.value || '').trim();
  const eventHours = parseFloat(document.getElementById('markEventHours')?.value || '2.0');
  const eventDate = document.getElementById('markEventDate')?.value;

  if (!eventName) {
    showToast('Please enter an Event / Rehearsal Name.', 'error');
    document.getElementById('markEventName')?.focus();
    return;
  }
  if (!eventDate) {
    showToast('Please select a valid date.', 'error');
    return;
  }
  if (isNaN(eventHours) || eventHours <= 0) {
    showToast('Please enter a valid duration in hours.', 'error');
    return;
  }

  // Construct attendance payload
  const records = state.allStudents.map(s => ({
    reg_no: s.reg_no,
    is_present: Boolean(state.attendanceMap[s.reg_no])
  }));

  const payload = {
    event_name: eventName,
    event_date: eventDate,
    duration_hours: eventHours,
    records: records
  };

  const doSave = async () => {
    try {
      const res = await fetch(`${API_BASE}/attendance/save`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });

      if (res.status === 401) {
        showToast('Admin PIN required to save attendance.', 'error');
        openPinModal(doSave);
        return;
      }

      if (!res.ok) {
        const err = await res.json();
        showToast(err.detail || 'Failed to save attendance', 'error');
        return;
      }

      const result = await res.json();
      showToast(`Saved! ${result.present_count} present, ${result.absent_count} absent.`);

      // Reset form and switches
      document.getElementById('markEventName').value = '';
      state.allStudents.forEach(s => state.attendanceMap[s.reg_no] = false);
      filterMarkRoster();
      updateMarkCounters();

      // Switch to Day Viewer to show saved report
      setTimeout(() => {
        inspectEventFromDashboard(result.event_id, result.event_date);
      }, 800);

    } catch (err) {
      showToast('Network error while saving attendance.', 'error');
    }
  };

  if (!state.adminPin) {
    openPinModal(doSave);
  } else {
    doSave();
  }
}

// ================= VIEW 3: DAY VIEWER & PRINT =================

function loadViewerTab() {
  const dateInput = document.getElementById('viewerDateInput');
  const dateVal = dateInput ? dateInput.value : new Date().toISOString().split('T')[0];
  loadEventsForDate(dateVal);
}

async function loadEventsForDate(dateStr, selectEventId = null) {
  const select = document.getElementById('viewerEventSelect');
  if (!select) return;

  select.innerHTML = '<option value="">Loading events...</option>';

  try {
    const res = await fetch(`${API_BASE}/events?date=${dateStr}`);
    if (!res.ok) throw new Error();
    const events = await res.json();

    if (events.length === 0) {
      select.innerHTML = '<option value="">No events found for this date</option>';
      hideViewerRoster();
      return;
    }

    select.innerHTML = '<option value="">Choose an event...</option>' + events.map(e => `
      <option value="${e.event_id}" ${selectEventId && selectEventId === e.event_id ? 'selected' : ''}>
        ${e.event_name} (${e.duration_hours}h)
      </option>
    `).join('');

    if (selectEventId) {
      loadEventRoster(selectEventId);
    } else if (events.length === 1) {
      select.value = events[0].event_id;
      loadEventRoster(events[0].event_id);
    } else {
      hideViewerRoster();
    }
  } catch (err) {
    select.innerHTML = '<option value="">Failed to load events</option>';
  }
}

async function loadEventRoster(eventId) {
  if (!eventId) {
    hideViewerRoster();
    return;
  }

  state.selectedEventId = parseInt(eventId);

  try {
    const res = await fetch(`${API_BASE}/attendance/event/${eventId}`);
    if (!res.ok) throw new Error();
    const data = await res.json();

    // Populate Event Header
    document.getElementById('viewerEventHeader').classList.remove('hidden');
    document.getElementById('viewerEventTitle').textContent = data.event.event_name;
    document.getElementById('viewerEventDuration').textContent = `${data.event.duration_hours}h`;
    document.getElementById('viewerEventDate').textContent = data.event.event_date;
    document.getElementById('viewerRosterStats').textContent = `${data.total_present} Present, ${data.total_absent} Absent (Total: ${data.total_students})`;

    state.currentEventRoster = data.roster;
    renderViewerTable(data.roster);

  } catch (err) {
    showToast('Failed to load attendance roster', 'error');
  }
}

function renderViewerTable(roster) {
  const tbody = document.getElementById('viewerTableBody');
  if (!tbody) return;

  if (roster.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-6 text-center text-slate-400 italic">No attendance records found.</td></tr>';
    return;
  }

  tbody.innerHTML = roster.map(r => `
    <tr class="hover:bg-slate-50 transition-colors">
      <td class="px-6 py-3.5 font-bold text-slate-800">${r.student_name.toUpperCase()}</td>
      <td class="px-6 py-3.5 font-mono text-xs text-slate-500">${r.reg_no}</td>
      <td class="px-6 py-3.5"><span class="px-2 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-700">${r.part}</span></td>
      <td class="px-6 py-3.5">
        <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
          r.is_present ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
        }">
          <span class="w-1.5 h-1.5 rounded-full ${r.is_present ? 'bg-emerald-600' : 'bg-rose-600'}"></span>
          ${r.is_present ? 'Present' : 'Absent'}
        </span>
      </td>
    </tr>
  `).join('');
}

function filterViewerTable() {
  const q = (document.getElementById('viewerSearch')?.value || '').trim().toLowerCase();
  if (!state.currentEventRoster) return;
  const filtered = state.currentEventRoster.filter(r => 
    r.student_name.toLowerCase().includes(q) ||
    r.reg_no.toLowerCase().includes(q) ||
    r.part.toLowerCase().includes(q)
  );
  renderViewerTable(filtered);
}

function hideViewerRoster() {
  document.getElementById('viewerEventHeader')?.classList.add('hidden');
  const tbody = document.getElementById('viewerTableBody');
  if (tbody) {
    tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-slate-400 italic">Please select an event above to view its attendance sheet.</td></tr>';
  }
}

function openPrintableReport() {
  if (!state.selectedEventId) return;
  window.open(`${API_BASE}/reports/html/${state.selectedEventId}`, '_blank');
}

function downloadEventCsv() {
  if (!state.selectedEventId) return;
  window.location.href = `${API_BASE}/reports/csv/${state.selectedEventId}`;
}

// ================= VIEW 4: CREDITS LEDGER =================

function initCreditsCategories() {
  const container = document.getElementById('creditsCategoryTabs');
  if (!container) return;

  const parts = ['All Parts', ...CATEGORIES];
  container.innerHTML = parts.map(part => `
    <button onclick="setCreditsCategory('${part}')" id="creditsTab-${part.replace(/\s+/g, '')}" class="px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
      part === state.currentCreditsCategory ? 'bg-tjcNavy text-tjcGold shadow-sm' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
    }">
      ${part}
    </button>
  `).join('');
}

function setCreditsCategory(part) {
  state.currentCreditsCategory = part;
  initCreditsCategories();
  loadCreditsLedger(part);
}

async function loadCreditsLedger(part = 'All Parts') {
  const tbody = document.getElementById('creditsTableBody');
  const countBadge = document.getElementById('creditsRecordCount');
  if (tbody) tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-slate-400 italic">Calculating attendance hours & credits...</td></tr>';

  try {
    const url = part && part !== 'All Parts' ? `${API_BASE}/credits?part=${encodeURIComponent(part)}` : `${API_BASE}/credits`;
    const res = await fetch(url);
    if (!res.ok) throw new Error();
    const data = await res.json();

    state.allCreditsRows = data.students;
    if (countBadge) countBadge.textContent = `${data.total_records} Students`;

    renderCreditsTable(data.students);
  } catch (err) {
    if (tbody) tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-6 text-center text-rose-500 font-semibold">Failed to load credits ledger.</td></tr>';
  }
}

function renderCreditsTable(students) {
  const tbody = document.getElementById('creditsTableBody');
  if (!tbody) return;

  if (students.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-slate-400 italic">No students found in this section.</td></tr>';
    return;
  }

  tbody.innerHTML = students.map(s => `
    <tr class="hover:bg-slate-50 transition-colors">
      <td class="px-6 py-3.5 font-bold text-slate-800">${s.student_name}</td>
      <td class="px-6 py-3.5 font-mono text-xs text-slate-500">${s.reg_no}</td>
      <td class="px-6 py-3.5"><span class="px-2 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-700">${s.part}</span></td>
      <td class="px-6 py-3.5 font-semibold text-slate-700">${s.total_hours} hrs</td>
      <td class="px-6 py-3.5 text-right">
        <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-extrabold bg-tjcGold/15 text-tjcGold-dark border border-tjcGold/40">
          <i data-lucide="award" class="w-3.5 h-3.5"></i> ${s.credits} Credits
        </span>
      </td>
    </tr>
  `).join('');

  lucide.createIcons();
}

function filterCreditsTable() {
  const q = (document.getElementById('creditsSearchInput')?.value || '').trim().toLowerCase();
  if (!state.allCreditsRows) return;
  const filtered = state.allCreditsRows.filter(s =>
    s.student_name.toLowerCase().includes(q) ||
    s.reg_no.toLowerCase().includes(q) ||
    s.part.toLowerCase().includes(q)
  );
  renderCreditsTable(filtered);
}

function downloadCreditsCsv() {
  const part = state.currentCreditsCategory;
  const url = part && part !== 'All Parts' ? `${API_BASE}/reports/credits/csv?part=${encodeURIComponent(part)}` : `${API_BASE}/reports/credits/csv`;
  window.location.href = url;
}

// ================= VIEW 5: MEMBERS DIRECTORY =================

async function loadMembersList() {
  const tbody = document.getElementById('membersTableBody');
  const countBadge = document.getElementById('membersCountBadge');
  if (tbody) tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-6 text-center text-slate-400 italic">Loading choir members...</td></tr>';

  try {
    const res = await fetch(`${API_BASE}/students`);
    if (!res.ok) throw new Error();
    const students = await res.json();
    state.allStudents = students;

    if (countBadge) countBadge.textContent = `${students.length} Members`;
    renderMembersTable(students);
  } catch (err) {
    if (tbody) tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-6 text-center text-rose-500 font-semibold">Failed to load members list.</td></tr>';
  }
}

function renderMembersTable(students) {
  const tbody = document.getElementById('membersTableBody');
  if (!tbody) return;

  if (students.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-slate-400 italic">No registered members found.</td></tr>';
    return;
  }

  tbody.innerHTML = students.map(s => `
    <tr class="hover:bg-slate-50 transition-colors">
      <td class="px-6 py-3.5 font-bold text-slate-800">${s.student_name.toUpperCase()}</td>
      <td class="px-6 py-3.5 font-mono text-xs text-slate-500">${s.reg_no}</td>
      <td class="px-6 py-3.5"><span class="px-2 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-700">${s.part}</span></td>
      <td class="px-6 py-3.5 text-right">
        <button onclick="confirmDeleteStudent('${s.reg_no}', '${s.student_name.replace(/'/g, "\\'")}')" class="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors" title="Delete Member">
          <i data-lucide="trash-2" class="w-4 h-4"></i>
        </button>
      </td>
    </tr>
  `).join('');

  lucide.createIcons();
}

function filterMembersList() {
  const part = document.getElementById('membersFilterPart')?.value || 'All Parts';
  const q = (document.getElementById('membersSearchInput')?.value || '').trim().toLowerCase();

  const filtered = state.allStudents.filter(s => {
    const matchesPart = (part === 'All Parts' || s.part === part);
    const matchesSearch = (!q || s.student_name.toLowerCase().includes(q) || s.reg_no.toLowerCase().includes(q));
    return matchesPart && matchesSearch;
  });

  renderMembersTable(filtered);
}

async function submitNewStudent(event) {
  event.preventDefault();
  const name = document.getElementById('newStudentName').value.trim();
  const regNo = document.getElementById('newStudentReg').value.trim();
  const part = document.getElementById('newStudentPart').value;

  if (!name || !regNo || !part) {
    showToast('Please fill all fields.', 'error');
    return;
  }

  const doAdd = async () => {
    try {
      const res = await fetch(`${API_BASE}/students`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ student_name: name, reg_no: regNo, part: part })
      });

      if (res.status === 401) {
        showToast('Admin PIN required to add members.', 'error');
        openPinModal(doAdd);
        return;
      }

      if (res.status === 409) {
        showToast(`Registration ID '${regNo}' is already taken.`, 'error');
        return;
      }

      if (!res.ok) {
        const err = await res.json();
        showToast(err.detail || 'Failed to add student.', 'error');
        return;
      }

      showToast(`${name} added to ${part}!`);
      document.getElementById('addStudentForm').reset();
      loadMembersList();
    } catch (err) {
      showToast('Network error while adding member.', 'error');
    }
  };

  if (!state.adminPin) {
    openPinModal(doAdd);
  } else {
    doAdd();
  }
}

async function confirmDeleteStudent(regNo, name) {
  if (!confirm(`Are you sure you want to remove ${name} (${regNo}) from the choir?`)) return;

  const doDelete = async () => {
    try {
      const res = await fetch(`${API_BASE}/students/${encodeURIComponent(regNo)}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });

      if (res.status === 401) {
        showToast('Admin PIN required to delete members.', 'error');
        openPinModal(doDelete);
        return;
      }

      if (!res.ok) {
        showToast('Failed to delete student.', 'error');
        return;
      }

      showToast(`${name} removed successfully.`);
      loadMembersList();
    } catch (err) {
      showToast('Network error while deleting member.', 'error');
    }
  };

  if (!state.adminPin) {
    openPinModal(doDelete);
  } else {
    doDelete();
  }
}
