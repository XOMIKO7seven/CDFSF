// Program monitoring and management functionality

let eventSources = {};
let statusUpdateInterval;

function initializeProgramMonitoring() {
    // Load initial logs for all programs
    [1, 2, 3, 4].forEach(programId => {
        loadProgramLogs(programId);
        startLogStreaming(programId);
    });
    
    // Start status monitoring
    startStatusMonitoring();
}

function loadProgramLogs(programId) {
    fetch(`/api/programs/${programId}/logs`)
        .then(response => response.json())
        .then(data => {
            const logsContainer = document.getElementById(`logs-${programId}`);
            if (data.logs && data.logs.length > 0) {
                logsContainer.innerHTML = data.logs.map(log => 
                    `<div class="log-line">${escapeHtml(log)}</div>`
                ).join('');
                scrollToBottom(logsContainer);
            } else {
                logsContainer.innerHTML = '<div class="text-muted">No logs available</div>';
            }
        })
        .catch(error => {
            console.error(`Error loading logs for program ${programId}:`, error);
            const logsContainer = document.getElementById(`logs-${programId}`);
            logsContainer.innerHTML = '<div class="text-danger">Error loading logs</div>';
        });
}

function startLogStreaming(programId) {
    // Close existing connection if any
    if (eventSources[programId]) {
        eventSources[programId].close();
    }
    
    const eventSource = new EventSource(`/api/programs/${programId}/logs/stream`);
    eventSources[programId] = eventSource;
    
    let initialLogsLoaded = false;
    
    eventSource.onmessage = function(event) {
        const logsContainer = document.getElementById(`logs-${programId}`);
        
        if (!initialLogsLoaded) {
            // Clear loading message
            logsContainer.innerHTML = '';
            initialLogsLoaded = true;
        }
        
        // Add new log line
        const logDiv = document.createElement('div');
        logDiv.className = 'log-line';
        logDiv.textContent = event.data;
        logsContainer.appendChild(logDiv);
        
        // Keep only last 500 lines for performance
        const logLines = logsContainer.querySelectorAll('.log-line');
        if (logLines.length > 500) {
            logLines[0].remove();
        }
        
        scrollToBottom(logsContainer);
    };
    
    eventSource.onerror = function(event) {
        console.error(`Error in log stream for program ${programId}:`, event);
        eventSource.close();
        
        // Attempt to reconnect after 5 seconds
        setTimeout(() => {
            startLogStreaming(programId);
        }, 5000);
    };
}

function startStatusMonitoring() {
    function updateStatus() {
        fetch('/api/programs/status')
            .then(response => response.json())
            .then(data => {
                Object.keys(data).forEach(programId => {
                    const program = data[programId];
                    updateProgramStatus(programId, program);
                });
            })
            .catch(error => {
                console.error('Error updating program status:', error);
            });
    }
    
    // Update immediately and then every 3 seconds
    updateStatus();
    statusUpdateInterval = setInterval(updateStatus, 3000);
}

function updateProgramStatus(programId, program) {
    const statusIndicator = document.getElementById(`status-${programId}`);
    const statusText = document.getElementById(`status-text-${programId}`);
    const pidElement = document.getElementById(`pid-${programId}`);
    const startBtn = document.getElementById(`start-btn-${programId}`);
    const stopBtn = document.getElementById(`stop-btn-${programId}`);
    
    if (statusIndicator) {
        statusIndicator.className = `status-indicator status-${program.status}`;
    }
    
    if (statusText) {
        statusText.textContent = program.status.charAt(0).toUpperCase() + program.status.slice(1);
    }
    
    if (pidElement) {
        pidElement.textContent = program.pid || 'N/A';
    }
    
    // Update button states
    if (startBtn && stopBtn) {
        if (program.status === 'running') {
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } else {
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
    }
}

function startProgram(programId) {
    showAlert('info', `Starting program ${programId}...`);
    
    fetch(`/api/programs/${programId}/start`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showAlert('success', data.message);
        } else {
            showAlert('danger', data.message);
        }
    })
    .catch(error => {
        console.error(`Error starting program ${programId}:`, error);
        showAlert('danger', `Error starting program ${programId}`);
    });
}

function stopProgram(programId) {
    showAlert('info', `Stopping program ${programId}...`);
    
    fetch(`/api/programs/${programId}/stop`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showAlert('success', data.message);
        } else {
            showAlert('danger', data.message);
        }
    })
    .catch(error => {
        console.error(`Error stopping program ${programId}:`, error);
        showAlert('danger', `Error stopping program ${programId}`);
    });
}

function clearLogs(programId) {
    if (confirm(`Are you sure you want to clear logs for program ${programId}?`)) {
        fetch(`/api/programs/${programId}/clear_logs`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const logsContainer = document.getElementById(`logs-${programId}`);
                logsContainer.innerHTML = '<div class="text-muted">Logs cleared</div>';
                showAlert('success', data.message);
            } else {
                showAlert('danger', data.message);
            }
        })
        .catch(error => {
            console.error(`Error clearing logs for program ${programId}:`, error);
            showAlert('danger', `Error clearing logs for program ${programId}`);
        });
    }
}

function refreshAll() {
    showAlert('info', 'Refreshing all programs...');
    
    // Reload logs for all programs
    [1, 2, 3, 4].forEach(programId => {
        loadProgramLogs(programId);
    });
    
    // Force status update
    fetch('/api/programs/status')
        .then(response => response.json())
        .then(data => {
            Object.keys(data).forEach(programId => {
                const program = data[programId];
                updateProgramStatus(programId, program);
            });
            showAlert('success', 'All programs refreshed');
        })
        .catch(error => {
            console.error('Error refreshing programs:', error);
            showAlert('danger', 'Error refreshing programs');
        });
}

function showAlert(type, message) {
    const alertContainer = document.getElementById('alert-container');
    const alertId = 'alert-' + Date.now();
    
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert" id="${alertId}">
            <i class="fas fa-${getAlertIcon(type)} me-2"></i>
            ${escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alertElement = document.getElementById(alertId);
        if (alertElement) {
            const alert = new bootstrap.Alert(alertElement);
            alert.close();
        }
    }, 5000);
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function scrollToBottom(element) {
    element.scrollTop = element.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    // Close all event sources
    Object.values(eventSources).forEach(eventSource => {
        eventSource.close();
    });
    
    // Clear status monitoring interval
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
    }
});
