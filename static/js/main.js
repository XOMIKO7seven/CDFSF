// Program monitoring and management functionality

let statusUpdateInterval;
let logUpdateIntervals = {};
let lastLogTimestamps = {};

function initializeProgramMonitoring() {
    // Load initial logs for all programs
    [1, 2, 3, 4].forEach(programId => {
        loadProgramLogs(programId);
        startLogPolling(programId);
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
                logsContainer.innerHTML = '<div class="text-muted">Нет доступных логов</div>';
            }
            
            // Store timestamp for future polling
            if (data.timestamp) {
                lastLogTimestamps[programId] = data.timestamp;
            }
        })
        .catch(error => {
            console.error(`Error loading logs for program ${programId}:`, error);
            const logsContainer = document.getElementById(`logs-${programId}`);
            logsContainer.innerHTML = '<div class="text-danger">Ошибка загрузки логов</div>';
        });
}

function startLogPolling(programId) {
    // Clear existing interval if any
    if (logUpdateIntervals[programId]) {
        clearInterval(logUpdateIntervals[programId]);
    }
    
    // Poll for new logs every 2 seconds
    logUpdateIntervals[programId] = setInterval(() => {
        pollForNewLogs(programId);
    }, 2000);
}

function pollForNewLogs(programId) {
    const sinceParam = lastLogTimestamps[programId] ? `?since=${encodeURIComponent(lastLogTimestamps[programId])}` : '';
    
    fetch(`/api/programs/${programId}/logs${sinceParam}`)
        .then(response => response.json())
        .then(data => {
            if (data.logs && data.logs.length > 0) {
                const logsContainer = document.getElementById(`logs-${programId}`);
                
                // If this is the first load or we have new logs
                if (!sinceParam || data.logs.length > 0) {
                    if (!sinceParam) {
                        // Full reload
                        logsContainer.innerHTML = data.logs.map(log => 
                            `<div class="log-line">${escapeHtml(log)}</div>`
                        ).join('');
                    } else {
                        // Append new logs
                        data.logs.forEach(log => {
                            const logDiv = document.createElement('div');
                            logDiv.className = 'log-line';
                            logDiv.textContent = log;
                            logsContainer.appendChild(logDiv);
                        });
                        
                        // Keep only last 500 lines for performance
                        const logLines = logsContainer.querySelectorAll('.log-line');
                        while (logLines.length > 500) {
                            logLines[0].remove();
                        }
                    }
                    
                    scrollToBottom(logsContainer);
                }
            }
            
            // Update timestamp for next poll
            if (data.timestamp) {
                lastLogTimestamps[programId] = data.timestamp;
            }
        })
        .catch(error => {
            console.error(`Error polling logs for program ${programId}:`, error);
        });
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
        if (program.status === 'запущен') {
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } else {
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
    }
}

function startProgram(programId) {
    showAlert('info', `Запуск программы ${programId}...`);
    
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
        showAlert('danger', `Ошибка запуска программы ${programId}`);
    });
}

function stopProgram(programId) {
    showAlert('info', `Остановка программы ${programId}...`);
    
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
        showAlert('danger', `Ошибка остановки программы ${programId}`);
    });
}

function clearLogs(programId) {
    if (confirm(`Вы уверены, что хотите очистить логи программы ${programId}?`)) {
        fetch(`/api/programs/${programId}/clear_logs`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const logsContainer = document.getElementById(`logs-${programId}`);
                logsContainer.innerHTML = '<div class="text-muted">Логи очищены</div>';
                showAlert('success', data.message);
            } else {
                showAlert('danger', data.message);
            }
        })
        .catch(error => {
            console.error(`Error clearing logs for program ${programId}:`, error);
            showAlert('danger', `Ошибка очистки логов программы ${programId}`);
        });
    }
}

function refreshAll() {
    showAlert('info', 'Обновление всех программ...');
    
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
            showAlert('success', 'Все программы обновлены');
        })
        .catch(error => {
            console.error('Error refreshing programs:', error);
            showAlert('danger', 'Ошибка обновления программ');
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
    // Clear all log polling intervals
    Object.values(logUpdateIntervals).forEach(interval => {
        clearInterval(interval);
    });
    
    // Clear status monitoring interval
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
    }
});
