"""Laptop Dashboard UI for Hotel Lounge Smart-Glasses POC.

Served directly from lounge-control. Allows staff to:
- Select a guest from hotel records or manually edit guest_ref
- Submit entry and exit taps via the shared /v1/lounge/taps path
- View live active roster displaying display_name and admitted_at only
- Automatically refetch roster on SSE roster_change events
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hotel Lounge Staff Dashboard</title>
  <style>
    :root {
      --bg-color: #0f172a;
      --card-bg: #1e293b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-hover: #0284c7;
      --success: #22c55e;
      --success-hover: #16a34a;
      --danger: #ef4444;
      --danger-hover: #dc2626;
      --border: #334155;
    }
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    body {
      background-color: var(--bg-color);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    header {
      background: var(--card-bg);
      border-bottom: 1px solid var(--border);
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    h1 {
      font-size: 1.25rem;
      font-weight: 600;
      letter-spacing: -0.025em;
    }
    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.85rem;
      color: var(--text-muted);
      background: rgba(255, 255, 255, 0.05);
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      border: 1px solid var(--border);
    }
    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #eab308;
    }
    .status-dot.connected {
      background: var(--success);
      box-shadow: 0 0 8px rgba(34, 197, 94, 0.6);
    }
    main {
      flex: 1;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2rem;
      padding: 2rem;
      max-width: 1400px;
      margin: 0 auto;
      width: 100%;
    }
    @media (max-width: 860px) {
      main {
        grid-template-columns: 1fr;
      }
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 0.75rem;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }
    h2 {
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--accent);
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .form-group {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }
    label {
      font-size: 0.85rem;
      color: var(--text-muted);
      font-weight: 500;
    }
    select, input[type="text"] {
      background: #0f172a;
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 0.6rem 0.75rem;
      border-radius: 0.375rem;
      font-size: 0.95rem;
      outline: none;
      transition: border-color 0.15s;
    }
    select:focus, input[type="text"]:focus {
      border-color: var(--accent);
    }
    .btn-row {
      display: flex;
      gap: 1rem;
      margin-top: 0.5rem;
    }
    button {
      flex: 1;
      padding: 0.75rem 1rem;
      border-radius: 0.375rem;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      border: none;
      transition: background-color 0.15s, opacity 0.15s;
    }
    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    .btn-entry {
      background: var(--success);
      color: white;
    }
    .btn-entry:hover:not(:disabled) {
      background: var(--success-hover);
    }
    .btn-exit {
      background: var(--danger);
      color: white;
    }
    .btn-exit:hover:not(:disabled) {
      background: var(--danger-hover);
    }
    .btn-register {
      background: var(--accent);
      color: #082f49;
    }
    .btn-register:hover:not(:disabled) {
      background: var(--accent-hover);
      color: white;
    }
    .btn-refresh {
      background: transparent;
      border: 1px solid var(--border);
      color: var(--text-muted);
      font-size: 0.8rem;
      padding: 0.25rem 0.5rem;
      border-radius: 0.25rem;
      cursor: pointer;
    }
    .btn-refresh:hover {
      color: var(--text-main);
      border-color: var(--text-muted);
    }
    .feedback {
      padding: 0.75rem 1rem;
      border-radius: 0.375rem;
      font-size: 0.875rem;
      display: none;
    }
    .feedback.info {
      display: block;
      background: rgba(56, 189, 248, 0.15);
      border: 1px solid var(--accent);
      color: var(--accent);
    }
    .feedback.error {
      display: block;
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid var(--danger);
      color: #fca5a5;
    }
    .feedback.success {
      display: block;
      background: rgba(34, 197, 94, 0.15);
      border: 1px solid var(--success);
      color: #86efac;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
    }
    th {
      text-align: left;
      padding: 0.6rem 0.75rem;
      border-bottom: 1px solid var(--border);
      color: var(--text-muted);
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    td {
      padding: 0.75rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    tr:last-child td {
      border-bottom: none;
    }
    .empty-state {
      text-align: center;
      padding: 2.5rem 1rem;
      color: var(--text-muted);
      font-style: italic;
      font-size: 0.9rem;
    }
    .counter {
      background: rgba(56, 189, 248, 0.2);
      color: var(--accent);
      padding: 0.1rem 0.45rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      margin-left: 0.5rem;
    }
    .privacy-notice {
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-top: auto;
      padding-top: 1rem;
      border-top: 1px dashed var(--border);
    }
  </style>
</head>
<body>
  <header>
    <h1>🏨 Hotel Lounge — Laptop Control & Roster</h1>
    <div class="status-badge" id="sse-status">
      <span class="status-dot" id="sse-dot"></span>
      <span id="sse-text">Connecting SSE...</span>
    </div>
  </header>

  <main>
    <!-- Tap Control Card -->
    <div class="card">
      <h2>Guest Tap Ingress</h2>

      <div class="form-group">
        <label for="guest-dropdown">Select Registered Hotel Guest</label>
        <select id="guest-dropdown">
          <option value="">-- Choose guest or type reference below --</option>
        </select>
      </div>

      <div class="form-group">
        <label for="guest-ref">Guest Reference (editable)</label>
        <input type="text" id="guest-ref" placeholder="e.g. guest-alex-101" spellcheck="false" autocomplete="off" />
      </div>

      <div class="btn-row">
        <button type="button" class="btn-entry" id="btn-entry" onclick="submitTap('entry')">
          🟢 Admit (Entry Tap)
        </button>
        <button type="button" class="btn-exit" id="btn-exit" onclick="submitTap('exit')">
          🔴 Depart (Exit Tap)
        </button>
      </div>

      <div id="tap-feedback" class="feedback"></div>

      <div class="privacy-notice">
        Submits taps to <code>POST /v1/lounge/taps</code>. Enforces at most one active presence per guest reference.
      </div>
    </div>

    <!-- Mock Hotel Guest Registration Card -->
    <div class="card">
      <h2>Register Mock Hotel Guest</h2>
      <form id="guest-registration-form">
        <div class="form-group">
          <label for="guest-name">Guest name</label>
          <input type="text" id="guest-name" maxlength="100" required autocomplete="off" />
        </div>
        <div class="form-group">
          <label for="guest-room">Room number (optional)</label>
          <input type="text" id="guest-room" autocomplete="off" />
        </div>
        <div class="form-group">
          <label for="guest-allergies">Allergies (optional, comma-separated)</label>
          <input type="text" id="guest-allergies" placeholder="e.g. peanuts, shellfish" />
        </div>
        <div class="form-group">
          <label for="guest-preferences">Preferences (optional, comma-separated)</label>
          <input type="text" id="guest-preferences" placeholder="e.g. still water, quiet table" />
        </div>
        <button type="submit" class="btn-register" id="btn-register-guest">Register guest</button>
      </form>
      <div id="registration-feedback" class="feedback" role="status" aria-live="polite"></div>
      <div class="privacy-notice">
        Creates a mock guest in the hotel list with a generated reference and synthetic photo.
      </div>
    </div>

    <!-- Active Roster Card -->
    <div class="card">
      <h2>
        <span>Active Lounge Roster <span class="counter" id="roster-count">0</span></span>
        <button type="button" class="btn-refresh" onclick="fetchRoster()">Refresh</button>
      </h2>

      <div id="roster-container">
        <table>
          <thead>
            <tr>
              <th>Guest Name</th>
              <th>Admitted At</th>
            </tr>
          </thead>
          <tbody id="roster-tbody">
            <!-- Dynamic entries -->
          </tbody>
        </table>
        <div id="roster-empty" class="empty-state">No guests currently admitted in lounge.</div>
      </div>

      <div class="privacy-notice">
        Displaying guest display_name and admitted_at only. No personal preferences, allergies, or identifiers shown.
      </div>
    </div>
  </main>

  <script>
    const guestDropdown = document.getElementById('guest-dropdown');
    const guestRefInput = document.getElementById('guest-ref');
    const rosterTbody = document.getElementById('roster-tbody');
    const rosterEmpty = document.getElementById('roster-empty');
    const rosterCount = document.getElementById('roster-count');
    const tapFeedback = document.getElementById('tap-feedback');
    const registrationForm = document.getElementById('guest-registration-form');
    const registrationFeedback = document.getElementById('registration-feedback');
    const sseDot = document.getElementById('sse-dot');
    const sseText = document.getElementById('sse-text');

    function showFeedback(message, type) {
      tapFeedback.textContent = message;
      tapFeedback.className = 'feedback ' + type;
    }

    // Populate guest dropdown
    async function loadHotelGuests(selectedGuestRef = null) {
      try {
        const resp = await fetch('/v1/dashboard/guests');
        if (resp.ok) {
          const guests = await resp.json();
          guestDropdown.innerHTML = '<option value="">-- Choose guest or type reference below --</option>';
          guests.forEach(g => {
            const opt = document.createElement('option');
            opt.value = g.guest_ref;
            opt.textContent = `${g.display_name} (${g.guest_ref})`;
            guestDropdown.appendChild(opt);
          });
          const selectedRef = selectedGuestRef || guests[0]?.guest_ref || '';
          guestDropdown.value = selectedRef;
          if (selectedGuestRef || !guestRefInput.value) {
            guestRefInput.value = selectedRef;
          }
        }
      } catch (e) {
        console.warn('Failed to load hotel guests:', e);
      }
    }

    function showRegistrationFeedback(message, type) {
      registrationFeedback.textContent = message;
      registrationFeedback.className = 'feedback ' + type;
    }

    function commaSeparatedValues(value) {
      return value.split(',').map(item => item.trim()).filter(Boolean);
    }

    async function registerGuest(event) {
      event.preventDefault();
      const displayName = document.getElementById('guest-name').value.trim();
      if (!displayName) {
        showRegistrationFeedback('Enter a guest name.', 'error');
        return;
      }

      const payload = {
        display_name: displayName,
        room_number: document.getElementById('guest-room').value.trim() || null,
        allergies: commaSeparatedValues(document.getElementById('guest-allergies').value),
        preferences: commaSeparatedValues(document.getElementById('guest-preferences').value)
      };
      const button = document.getElementById('btn-register-guest');
      button.disabled = true;
      try {
        const resp = await fetch('/v1/dashboard/guests', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || resp.statusText);
        registrationForm.reset();
        await loadHotelGuests(data.guest_ref);
        showRegistrationFeedback(
          `Registered ${data.display_name}. Guest reference: ${data.guest_ref}`,
          'success'
        );
      } catch (err) {
        showRegistrationFeedback(`Could not register guest: ${err.message}`, 'error');
      } finally {
        button.disabled = false;
      }
    }

    registrationForm.addEventListener('submit', registerGuest);

    guestDropdown.addEventListener('change', (e) => {
      if (e.target.value) {
        guestRefInput.value = e.target.value;
      }
    });

    // Fetch and render active roster
    async function fetchRoster() {
      try {
        const resp = await fetch('/v1/lounge/roster');
        if (!resp.ok) throw new Error('Status ' + resp.status);
        const roster = await resp.json();
        renderRoster(roster);
      } catch (e) {
        console.error('Failed to fetch roster:', e);
      }
    }

    function renderRoster(roster) {
      rosterTbody.innerHTML = '';
      rosterCount.textContent = roster.length;
      if (!roster || roster.length === 0) {
        rosterEmpty.style.display = 'block';
        return;
      }
      rosterEmpty.style.display = 'none';
      roster.forEach(entry => {
        const row = document.createElement('tr');
        const nameCell = document.createElement('td');
        nameCell.textContent = entry.display_name;
        nameCell.style.fontWeight = '500';

        const admittedCell = document.createElement('td');
        let formattedTime = entry.admitted_at;
        try {
          const d = new Date(entry.admitted_at);
          formattedTime = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        } catch (_) {}
        admittedCell.textContent = formattedTime;
        admittedCell.style.color = 'var(--text-muted)';

        row.appendChild(nameCell);
        row.appendChild(admittedCell);
        rosterTbody.appendChild(row);
      });
    }

    // Submit tap event
    async function submitTap(eventType) {
      const guestRef = guestRefInput.value.trim();
      if (!guestRef) {
        showFeedback('Please select or enter a guest reference.', 'error');
        return;
      }

      const eventId = 'evt-dash-' + Math.random().toString(36).substring(2, 10);
      const payload = {
        event_id: eventId,
        reader_id: 'lounge-laptop-dashboard',
        guest_ref: guestRef,
        event_type: eventType,
        occurred_at: new Date().toISOString()
      };

      try {
        const resp = await fetch('/v1/lounge/taps', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await resp.json();
        if (resp.ok) {
          if (data.action === 'already_admitted') {
            showFeedback(`Guest '${guestRef}' is already admitted. Single presence preserved.`, 'info');
          } else if (data.action === 'admitted') {
            showFeedback(`Guest '${guestRef}' admitted successfully.`, 'success');
          } else if (data.action === 'departed') {
            const count = (data.removed_candidates || []).length;
            showFeedback(`Guest '${guestRef}' departed (${count} presence removed).`, 'success');
          } else {
            showFeedback(`Tap recorded: ${JSON.stringify(data)}`, 'success');
          }
          fetchRoster();
        } else {
          showFeedback(`Tap error: ${data.detail || resp.statusText}`, 'error');
        }
      } catch (err) {
        showFeedback(`Network error submitting tap: ${err.message}`, 'error');
      }
    }

    // Connect to Server-Sent Events (SSE)
    function connectSSE() {
      const evtSource = new EventSource('/v1/lounge/events');

      evtSource.addEventListener('connected', () => {
        sseDot.className = 'status-dot connected';
        sseText.textContent = 'SSE Live';
      });

      evtSource.addEventListener('roster_change', (e) => {
        fetchRoster();
      });

      evtSource.onopen = () => {
        sseDot.className = 'status-dot connected';
        sseText.textContent = 'SSE Live';
        fetchRoster();
      };

      evtSource.onerror = () => {
        sseDot.className = 'status-dot';
        sseText.textContent = 'SSE Reconnecting...';
      };
    }

    // Initialize
    loadHotelGuests();
    fetchRoster();
    connectSSE();
  </script>
</body>
</html>
"""
