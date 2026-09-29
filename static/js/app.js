// TJC Attendance Portal - Client Application Logic
// St. Joseph's College - The Josephite Choir

const API_BASE = '/api';
const CATEGORIES = ["Alto", "Bass", "Soprano", "Tenor", "Band", "Conductors"];

// Global App State
let state = {
  adminPin: localStorage.getItem('tjc_admin_pin') || sessionStorage.getItem('tjc_admin_pin') || '',
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
document.addEventListener('DOMContentLoaded', async () => {
  lucide.createIcons();

  // Set today's date in date pickers
  const todayStr = new Date().toISOString().split('T')[0];
  const markDateInput = document.getElementById('markEventDate');
  const viewerDateInput = document.getElementById('viewerDateInput');
  if (markDateInput) markDateInput.value = todayStr;
  if (viewerDateInput) viewerDateInput.value = todayStr;

  // Initialize clock / duration summary
  updateEventTimeSummary();

  // Check stored passcode/PIN status
  const storedPin = localStorage.getItem('tjc_admin_pin') || sessionStorage.getItem('tjc_admin_pin');
  if (storedPin) {
    state.adminPin = storedPin;
    try {
      const res = await fetch(`${API_BASE}/auth/status`, {
        headers: { 'X-Admin-PIN': storedPin }
      });
      if (res.ok) {
        const data = await res.json();
        if (data.is_authenticated) {
          showDashboard();
          return;
        }
      }
    } catch (err) {
      console.warn('Initial session validation error:', err);
    }
  }

  // Not authenticated: strictly lock the portal
  lockPortal(false);
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

// Universal authenticated fetch wrapper that handles passcode enforcement
async function apiFetch(url, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };
  if (state.adminPin) {
    headers['X-Admin-PIN'] = state.adminPin;
  }

  const response = await fetch(url, { ...options, headers });
  if (response.status === 401) {
    lockPortal(true);
    showToast('Access passcode required to view this page.', 'error');
    throw new Error('Unauthorized');
  }
  return response;
}

// ================= PASSCODE GATEKEEPER / LOCK SCREEN =================

function togglePasscodeVisibility() {
  const input = document.getElementById('portalPasscodeInput');
  const eyeIcon = document.getElementById('passcodeEyeIcon');
  if (!input) return;

  if (input.type === 'password') {
    input.type = 'text';
    if (eyeIcon) eyeIcon.setAttribute('data-lucide', 'eye-off');
  } else {
    input.type = 'password';
    if (eyeIcon) eyeIcon.setAttribute('data-lucide', 'eye');
  }
  lucide.createIcons();
}

async function submitLockScreenPasscode() {
  const input = document.getElementById('portalPasscodeInput');
  const errorDiv = document.getElementById('lockScreenError');
  const errorText = document.getElementById('lockScreenErrorText');
  const unlockBtn = document.getElementById('unlockPortalBtn');
  const remember = document.getElementById('rememberPasscodeDevice')?.checked ?? true;

  const pin = input ? input.value.trim() : '';
  if (!pin) {
    if (errorText) errorText.textContent = 'Please enter the access passcode.';
    if (errorDiv) errorDiv.classList.remove('hidden');
    return;
  }

  if (unlockBtn) {
    unlockBtn.disabled = true;
    unlockBtn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin text-tjcGold"></i> <span>Verifying...</span>';
    lucide.createIcons();
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
      } else {
        sessionStorage.setItem('tjc_admin_pin', pin);
      }

      if (errorDiv) errorDiv.classList.add('hidden');
      showDashboard();
      showToast('Portal unlocked. Welcome!', 'success');
    } else {
      if (errorText) errorText.textContent = 'Incorrect passcode. Please try again.';
      if (errorDiv) errorDiv.classList.remove('hidden');
      if (input) {
        input.classList.add('border-rose-400');
        input.select();
      }
    }
  } catch (err) {
    if (errorText) errorText.textContent = 'Network or server error. Please try again.';
    if (errorDiv) errorDiv.classList.remove('hidden');
  } finally {
    if (unlockBtn) {
      unlockBtn.disabled = false;
      unlockBtn.innerHTML = '<i data-lucide="unlock" class="w-4 h-4 text-tjcGold"></i> <span>Unlock Portal</span>';
      lucide.createIcons();
    }
  }
}

function showDashboard() {
  const lockScreen = document.getElementById('lockScreen');
  const appContainer = document.getElementById('appContainer');

  if (lockScreen) lockScreen.classList.add('hidden');
  if (appContainer) appContainer.classList.remove('hidden');

  loadDashboardData();
  initMarkCategories();
  initCreditsCategories();
  updateEventTimeSummary();
  lucide.createIcons();
}

function lockPortal(showMessage = true) {
  state.adminPin = '';
  localStorage.removeItem('tjc_admin_pin');
  sessionStorage.removeItem('tjc_admin_pin');
  state.allStudents = [];
  state.allCreditsRows = [];
  state.currentEventRoster = [];

  const lockScreen = document.getElementById('lockScreen');
  const appContainer = document.getElementById('appContainer');
  const input = document.getElementById('portalPasscodeInput');
  const errorDiv = document.getElementById('lockScreenError');

  if (errorDiv) errorDiv.classList.add('hidden');
  if (input) {
    input.value = '';
    input.classList.remove('border-rose-400');
  }

  if (appContainer) appContainer.classList.add('hidden');
  if (lockScreen) {
    lockScreen.classList.remove('hidden');
    setTimeout(() => input?.focus(), 150);
  }

  lucide.createIcons();
  if (showMessage) {
    showToast('Portal locked.');
  }
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

// ================= VIEW 1: HOME / DASHBOARD =================

async function loadDashboardData(showToastMsg = false) {
  try {
    // 1. Fetch Students count
    const studentsRes = await apiFetch(`${API_BASE}/students`);
    if (studentsRes.ok) {
      const students = await studentsRes.json();
      state.allStudents = students;
      const statElem = document.getElementById('statTotalMembers');
      if (statElem) statElem.textContent = `${students.length} Members`;
    }

    // 2. Fetch Events
    const eventsRes = await apiFetch(`${API_BASE}/events`);
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
                  <p class="text-xs text-slate-500">${ev.event_date}${ev.start_time ? ' • Starts ' + ev.start_time : ''}</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <button onclick="inspectEventFromDashboard(${ev.event_id}, '${ev.event_date}')" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-tjcNavy hover:text-tjcGold transition-colors flex items-center gap-1">
                  View Roster <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
                </button>
                <button onclick="confirmDeleteEventFromDashboard(${ev.event_id}, '${ev.event_name.replace(/'/g, "\\'")}')" class="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors" title="Delete Session">
                  <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                </button>
              </div>
            </div>
          `).join('');
        }
        lucide.createIcons();
      }
    }

    if (showToastMsg) {
      showToast('Dashboard stats updated.', 'success');
    }
  } catch (err) {
    console.error('Error loading dashboard data:', err);
    if (showToastMsg) showToast('Failed to refresh dashboard.', 'error');
  }
}

function inspectEventFromDashboard(eventId, eventDate) {
  switchTab('viewer');
  const dateInput = document.getElementById('viewerDateInput');
  if (dateInput) dateInput.value = eventDate;
  loadEventsForDate(eventDate, eventId);
}

// ================= VIEW 2: MARK ATTENDANCE =================

function setEventDuration(hours) {
  const hoursInput = document.getElementById('markEventHours');
  if (hoursInput) {
    hoursInput.value = hours;
    updateEventTimeSummary();
  }
}

function updateEventTimeSummary() {
  const timeInput = document.getElementById('markEventTime');
  const hoursInput = document.getElementById('markEventHours');
  const summaryElem = document.getElementById('eventTimeSummary');
  if (!summaryElem) return;

  const timeVal = timeInput ? timeInput.value : '16:30';
  const hours = parseFloat(hoursInput?.value || '2.0');

  if (!timeVal) {
    summaryElem.innerHTML = `Duration: <strong>${hours}h</strong> credit for attendees`;
    return;
  }

  // Parse start time (HH:MM)
  const parts = timeVal.split(':');
  if (parts.length < 2) return;
  const startH = parseInt(parts[0], 10);
  const startM = parseInt(parts[1], 10);

  // Format 12-hour start time
  const startPeriod = startH >= 12 ? 'PM' : 'AM';
  const startH12 = startH % 12 || 12;
  const startFormatted = `${startH12}:${startM < 10 ? '0' : ''}${startM} ${startPeriod}`;

  // Calculate end time
  const totalMinutes = Math.round(hours * 60);
  const endTotalMins = (startH * 60 + startM + totalMinutes) % (24 * 60);
  const endH = Math.floor(endTotalMins / 60);
  const endM = endTotalMins % 60;
  const endPeriod = endH >= 12 ? 'PM' : 'AM';
  const endH12 = endH % 12 || 12;
  const endFormatted = `${endH12}:${endM < 10 ? '0' : ''}${endM} ${endPeriod}`;

  summaryElem.innerHTML = `Counted from <strong>${startFormatted}</strong> to <strong>${endFormatted}</strong> (${hours} hrs credit)`;
}

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

// Internal refresh function: seamlessly merges newly added students without losing toggled attendance
async function refreshMarkRoster(showToastMsg = true) {
  const icon = document.getElementById('refreshRosterIcon');
  if (icon) icon.classList.add('animate-spin');

  try {
    const res = await apiFetch(`${API_BASE}/students`);
    if (res.ok) {
      const students = await res.json();
      state.allStudents = students;

      // Merge new students into attendance map without overwriting existing marks
      students.forEach(s => {
        if (!(s.reg_no in state.attendanceMap)) {
          state.attendanceMap[s.reg_no] = false;
        }
      });

      filterMarkRoster();
      updateMarkCounters();

      if (showToastMsg) {
        showToast(`Roster refreshed! ${students.length} members loaded.`, 'success');
      }
    }
  } catch (err) {
    if (showToastMsg) {
      showToast('Failed to refresh roster.', 'error');
    }
  } finally {
    if (icon) {
      setTimeout(() => icon.classList.remove('animate-spin'), 400);
    }
  }
}

async function loadMarkTab() {
  await refreshMarkRoster(false);
  updateEventTimeSummary();
}

function filterMarkRoster() {
  const part = state.currentMarkCategory;
  const query = (document.getElementById('markSearchInput')?.value || '').trim().toLowerCase();

  const filtered = state.allStudents.filter(s => {
    const matchesCategory = (part === 'All Parts' || s.part === part);
    const matchesSearch = (!query || s.student_name.toLowerCase().includes(query) || s.reg_no.toLowerCase().includes(query));
    return matchesCategory && matchesSearch;
  });

  renderMarkRoster(filtered);
}

function renderMarkRoster(students) {
  const container = document.getElementById('markRosterContainer') || document.getElementById('attendanceGrid');
  if (!container) return;

  if (students.length === 0) {
    container.innerHTML = `
      <div class="col-span-full py-12 text-center text-slate-400">
        <i data-lucide="users" class="w-10 h-10 mx-auto mb-2 text-slate-300"></i>
        No students found matching current filters.
      </div>
    `;
    lucide.createIcons();
    return;
  }

  container.innerHTML = students.map(s => {
    const isPresent = Boolean(state.attendanceMap[s.reg_no]);
    return `
      <div class="bg-white rounded-xl p-4 border transition-all shadow-sm flex items-center justify-between gap-3 ${
        isPresent ? 'border-emerald-300 bg-emerald-50/20' : 'border-slate-200'
      }">
        <div class="min-w-0 flex-1">
          <h4 class="font-bold text-slate-800 text-sm truncate uppercase">${s.student_name}</h4>
          <div class="flex items-center gap-2 mt-0.5">
            <span class="text-xs text-slate-500 font-mono">${s.reg_no}</span>
            <span class="text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600">${s.part}</span>
          </div>
        </div>

        <!-- Custom iOS/Tailwind Toggle Switch -->
        <label class="relative inline-flex items-center cursor-pointer shrink-0">
          <input 
            type="checkbox" 
            class="sr-only peer" 
            ${isPresent ? 'checked' : ''} 
            onchange="toggleAttendance('${s.reg_no}')"
          >
          <div class="w-12 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
        </label>
      </div>
    `;
  }).join('');

  lucide.createIcons();
}

function toggleAttendance(regNo) {
  state.attendanceMap[regNo] = !state.attendanceMap[regNo];
  updateMarkCounters();
  filterMarkRoster();
}

function markFiltered(status) {
  const part = state.currentMarkCategory;
  const query = (document.getElementById('markSearchInput')?.value || '').trim().toLowerCase();

  const filtered = state.allStudents.filter(s => {
    const matchesCategory = (part === 'All Parts' || s.part === part);
    const matchesSearch = (!query || s.student_name.toLowerCase().includes(query) || s.reg_no.toLowerCase().includes(query));
    return matchesCategory && matchesSearch;
  });

  filtered.forEach(s => {
    state.attendanceMap[s.reg_no] = status;
  });

  filterMarkRoster();
  updateMarkCounters();
  showToast(`Marked ${filtered.length} students ${status ? 'Present' : 'Absent'}`);
}

function updateMarkCounters() {
  const total = state.allStudents.length;
  let present = 0;
  for (const reg in state.attendanceMap) {
    if (state.attendanceMap[reg]) present++;
  }
  const absent = total - present;

  const cntPresent = document.getElementById('cntPresent') || document.getElementById('livePresentCount');
  const cntAbsent = document.getElementById('cntAbsent') || document.getElementById('liveAbsentCount');
  const saveBarCount = document.getElementById('saveBarCount');

  if (cntPresent) cntPresent.textContent = `${present}`;
  if (cntAbsent) cntAbsent.textContent = `${absent}`;
  if (saveBarCount) saveBarCount.textContent = `${total}`;
}

async function saveAttendance() {
  const eventName = (document.getElementById('markEventName')?.value || '').trim();
  const eventDate = document.getElementById('markEventDate')?.value;
  const eventTime = (document.getElementById('markEventTime')?.value || '').trim();
  const eventHours = parseFloat(document.getElementById('markEventHours')?.value || '2.0');

  if (!eventName) {
    showToast('Please specify an event name / session title.', 'error');
    document.getElementById('markEventName')?.focus();
    return;
  }

  if (!eventDate) {
    showToast('Please pick an event date.', 'error');
    return;
  }

  const records = state.allStudents.map(s => ({
    reg_no: s.reg_no,
    is_present: Boolean(state.attendanceMap[s.reg_no])
  }));

  const payload = {
    event_name: eventName,
    event_date: eventDate,
    duration_hours: eventHours,
    start_time: eventTime,
    records: records
  };

  try {
    const res = await apiFetch(`${API_BASE}/attendance/save`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });

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
    console.error('Save attendance error:', err);
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
    const res = await apiFetch(`${API_BASE}/events?date=${dateStr}`);
    if (!res.ok) throw new Error();
    const events = await res.json();

    if (events.length === 0) {
      select.innerHTML = '<option value="">No events found for this date</option>';
      hideViewerRoster();
      return;
    }

    select.innerHTML = '<option value="">Choose an event...</option>' + events.map(e => `
      <option value="${e.event_id}" ${selectEventId && selectEventId === e.event_id ? 'selected' : ''}>
        ${e.event_name} (${e.start_time ? e.start_time + ', ' : ''}${e.duration_hours}h)
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
    const res = await apiFetch(`${API_BASE}/attendance/event/${eventId}`);
    if (!res.ok) throw new Error();
    const data = await res.json();

    // Populate Event Header
    document.getElementById('viewerEventHeader').classList.remove('hidden');
    document.getElementById('viewerEventTitle').textContent = data.event.event_name;
    const timePrefix = data.event.start_time ? `${data.event.start_time} • ` : '';
    document.getElementById('viewerEventDuration').textContent = `${timePrefix}${data.event.duration_hours}h`;
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
  const pinQuery = state.adminPin ? `?pin=${encodeURIComponent(state.adminPin)}` : '';
  window.open(`${API_BASE}/reports/html/${state.selectedEventId}${pinQuery}`, '_blank');
}

function downloadEventCsv() {
  if (!state.selectedEventId) return;
  const pinQuery = state.adminPin ? `?pin=${encodeURIComponent(state.adminPin)}` : '';
  window.location.href = `${API_BASE}/reports/csv/${state.selectedEventId}${pinQuery}`;
}

async function confirmDeleteCurrentEvent() {
  if (!state.selectedEventId) {
    showToast('No event selected to delete.', 'error');
    return;
  }

  const eventTitle = document.getElementById('viewerEventTitle')?.textContent || 'this event';
  const eventDate = document.getElementById('viewerEventDate')?.textContent || '';

  if (!confirm(`Are you sure you want to permanently delete "${eventTitle}" (${eventDate})?\n\nThis will remove all recorded attendance for this session. This action cannot be undone.`)) {
    return;
  }

  try {
    const res = await apiFetch(`${API_BASE}/events/${state.selectedEventId}`, {
      method: 'DELETE'
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      showToast(err.detail || 'Failed to delete event.', 'error');
      return;
    }

    showToast(`"${eventTitle}" was deleted successfully.`, 'success');

    // Reset Day Viewer state
    state.selectedEventId = null;
    state.currentEventRoster = [];
    hideViewerRoster();

    // Reload event dropdown for current date
    const dateInput = document.getElementById('viewerDateInput');
    const dateVal = dateInput ? dateInput.value : '';
    if (dateVal) {
      await loadEventsForDate(dateVal);
    }

    // Refresh dashboard stats and recent events
    await loadDashboardData(false);

    // Refresh credits ledger if open
    if (!document.getElementById('tab-credits')?.classList.contains('hidden')) {
      await loadCreditsLedger(state.currentCreditsCategory, false);
    }

  } catch (err) {
    console.error('Delete event error:', err);
  }
}

async function confirmDeleteEventFromDashboard(eventId, eventName) {
  if (!confirm(`Are you sure you want to delete "${eventName}"?\n\nThis will permanently remove all attendance logs for this session.`)) {
    return;
  }

  try {
    const res = await apiFetch(`${API_BASE}/events/${eventId}`, {
      method: 'DELETE'
    });

    if (!res.ok) {
      showToast('Failed to delete event.', 'error');
      return;
    }

    showToast(`"${eventName}" deleted successfully.`, 'success');
    await loadDashboardData(false);

    // If currently selected in Day Viewer, reset it
    if (state.selectedEventId === eventId) {
      state.selectedEventId = null;
      hideViewerRoster();
      const dateInput = document.getElementById('viewerDateInput');
      if (dateInput?.value) {
        await loadEventsForDate(dateInput.value);
      }
    }

    // Refresh credits ledger if active
    if (!document.getElementById('tab-credits')?.classList.contains('hidden')) {
      await loadCreditsLedger(state.currentCreditsCategory, false);
    }
  } catch (err) {
    console.error('Delete event from dashboard error:', err);
  }
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

async function loadCreditsLedger(part = 'All Parts', showToastMsg = false) {
  const tbody = document.getElementById('creditsTableBody');
  const countBadge = document.getElementById('creditsRecordCount');
  const refreshBtn = document.getElementById('refreshCreditsBtn');
  const icon = refreshBtn?.querySelector('i');
  if (icon) icon.classList.add('animate-spin');

  if (tbody) tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-slate-400 italic">Calculating attendance hours & credits...</td></tr>';

  try {
    const url = part && part !== 'All Parts' ? `${API_BASE}/credits?part=${encodeURIComponent(part)}` : `${API_BASE}/credits`;
    const res = await apiFetch(url);
    if (!res.ok) throw new Error();
    const data = await res.json();

    state.allCreditsRows = data.students;
    if (countBadge) countBadge.textContent = `${data.total_records} Students`;

    renderCreditsTable(data.students);

    if (showToastMsg) {
      showToast('Credits ledger refreshed!', 'success');
    }
  } catch (err) {
    if (tbody) tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-6 text-center text-rose-500 font-semibold">Failed to load credits ledger.</td></tr>';
    if (showToastMsg) showToast('Failed to refresh credits ledger.', 'error');
  } finally {
    if (icon) setTimeout(() => icon.classList.remove('animate-spin'), 400);
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
  const baseUrl = part && part !== 'All Parts' 
    ? `${API_BASE}/reports/credits/csv?part=${encodeURIComponent(part)}` 
    : `${API_BASE}/reports/credits/csv`;
  const sep = baseUrl.includes('?') ? '&' : '?';
  const pinParam = state.adminPin ? `${sep}pin=${encodeURIComponent(state.adminPin)}` : '';
  window.location.href = `${baseUrl}${pinParam}`;
}

// ================= VIEW 5: MEMBERS DIRECTORY =================

async function loadMembersList(showToastMsg = false) {
  const tbody = document.getElementById('membersTableBody');
  const countBadge = document.getElementById('membersCountBadge');
  const refreshBtn = document.getElementById('refreshMembersBtn');
  const icon = refreshBtn?.querySelector('i');
  if (icon) icon.classList.add('animate-spin');

  try {
    const res = await apiFetch(`${API_BASE}/students`);
    if (!res.ok) throw new Error();
    const students = await res.json();
    state.allStudents = students;

    // Sync with attendanceMap so new members can immediately be marked
    students.forEach(s => {
      if (!(s.reg_no in state.attendanceMap)) {
        state.attendanceMap[s.reg_no] = false;
      }
    });

    if (countBadge) countBadge.textContent = `${students.length} Members`;
    renderMembersTable(students);

    if (showToastMsg) {
      showToast(`Members directory refreshed! ${students.length} members loaded.`, 'success');
    }
  } catch (err) {
    if (tbody) tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-6 text-center text-rose-500 font-semibold">Failed to load members list.</td></tr>';
    if (showToastMsg) showToast('Failed to refresh members list.', 'error');
  } finally {
    if (icon) setTimeout(() => icon.classList.remove('animate-spin'), 400);
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

  try {
    const res = await apiFetch(`${API_BASE}/students`, {
      method: 'POST',
      body: JSON.stringify({ student_name: name, reg_no: regNo, part: part })
    });

    if (res.status === 409) {
      showToast(`Registration ID '${regNo}' is already taken.`, 'error');
      return;
    }

    if (!res.ok) {
      const err = await res.json();
      showToast(err.detail || 'Failed to add student.', 'error');
      return;
    }

    showToast(`${name} added to ${part}! Directory & roster updated.`, 'success');
    document.getElementById('addStudentForm').reset();
    
    // Immediately reload directory and sync attendance roster!
    await loadMembersList(false);
    refreshMarkRoster(false);

  } catch (err) {
    console.error('Add member error:', err);
  }
}

async function confirmDeleteStudent(regNo, name) {
  if (!confirm(`Are you sure you want to remove ${name} (${regNo}) from the choir?`)) return;

  try {
    const res = await apiFetch(`${API_BASE}/students/${encodeURIComponent(regNo)}`, {
      method: 'DELETE'
    });

    if (!res.ok) {
      showToast('Failed to delete student.', 'error');
      return;
    }

    showToast(`${name} removed successfully.`);
    await loadMembersList(false);
    refreshMarkRoster(false);
  } catch (err) {
    console.error('Delete member error:', err);
  }
}

// Global Aliases
window.bulkSetAttendance = markFiltered;
window.submitAttendance = saveAttendance;
window.refreshMarkRoster = refreshMarkRoster;
window.setEventDuration = setEventDuration;
window.updateEventTimeSummary = updateEventTimeSummary;
window.confirmDeleteCurrentEvent = confirmDeleteCurrentEvent;
window.confirmDeleteEventFromDashboard = confirmDeleteEventFromDashboard;

