// --- Theme Manager ---
function toggleTheme() {
    const body = document.body;
    const icon = document.getElementById('theme-icon');
    if (body.getAttribute('data-theme') === 'light') {
        body.removeAttribute('data-theme'); // Dark mode
        icon.innerText = '☀️';
    } else {
        body.setAttribute('data-theme', 'light'); // Light mode
        icon.innerText = '🌙';
    }
}

// --- API Interaction ---
async function fetchLogs() {
    try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        renderTable(data);
    } catch (error) {
        console.error('Error fetching logs:', error);
    }
}

function renderTable(logs) {
    const tbody = document.getElementById('log-body');
    const emptyState = document.getElementById('empty-state');
    const countEl = document.getElementById('pending-count');
    
    tbody.innerHTML = '';
    
    // Filter only pending items (assuming all in log need review for now)
    // Or showcase all. For now, showcase all.
    
    if (logs.length === 0) {
        emptyState.style.display = 'block';
        countEl.innerText = '0';
        return;
    }

    emptyState.style.display = 'none';
    countEl.innerText = logs.length;

    logs.reverse().forEach(log => {
        const tr = document.createElement('tr');
        const confidence = parseFloat(log.final_prob).toFixed(2);
        
        tr.innerHTML = `
            <td style="color: var(--text-secondary);">${log.timestamp}</td>
            <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${log.url}">
                ${log.url}
            </td>
            <td>
                <span style="font-weight: bold; color: ${confidence > 0.8 ? 'var(--danger)' : 'var(--text-secondary)'}">
                    ${(confidence * 100).toFixed(1)}%
                </span>
            </td>
            <td>${log.is_phishing ? '🔴 Phishing' : '🟢 Safe'}</td>
            <td>
                <!-- Actions -->
                <button class="btn-action btn-approve" onclick="verifyLog('${log.id}', 'safe')">✅ Safe</button>
                <button class="btn-action btn-delete" onclick="verifyLog('${log.id}', 'remove')">🗑️ Remove</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function verifyLog(id, action) {
    if (!confirm(`Are you sure you want to mark this as ${action}?`)) return;

    try {
        const response = await fetch('/api/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, action })
        });
        
        if (response.ok) {
            fetchLogs(); // Reload
        } else {
            alert('Action failed');
        }
    } catch (error) {
        console.error(error);
        alert('Connection error');
    }
}

async function triggerRetrain() {
    const btn = document.getElementById('train-btn');
    const statusText = document.getElementById('status-text');
    const statusLight = document.getElementById('status-light');
    
    if (!confirm('Start training process? This may take 10-20 minutes.')) return;

    btn.disabled = true;
    btn.innerText = '⏳ Training Initiated...';
    
    // Simulate status update
    statusLight.className = 'status-badge status-training';
    statusText.innerText = 'Training in Progress...';
    statusText.style.color = 'var(--accent-color)';

    try {
        const period = document.getElementById('frequency-select').value;
        const response = await fetch('/api/retrain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ period })
        });

        const data = await response.json();
        alert(data.message);
        
        // Re-enable after 5 seconds just for UI feedback (actual training is async)
        setTimeout(() => {
            btn.disabled = false;
            btn.innerText = '🔥 Start Retraining';
        }, 5000);

    } catch (error) {
        alert('Failed to trigger training');
        btn.disabled = false;
        btn.innerText = '🔥 Start Retraining';
    }
}

// Init
document.addEventListener('DOMContentLoaded', fetchLogs);
