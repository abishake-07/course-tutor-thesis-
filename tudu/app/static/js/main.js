// Main JavaScript for Tudu Dashboard
let authToken = localStorage.getItem('authToken');
let budgetChart, trendsChart;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (!authToken) {
        // Redirect to login if no token
        showLoginForm();
        return;
    }
    
    initializeDashboard();
});

async function initializeDashboard() {
    try {
        await Promise.all([
            loadTaskStats(),
            loadBudgetSummary(),
            loadRecentTasks(),
            loadBudgetChart(),
            loadTrendsChart(),
            loadAIInsights()
        ]);
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        if (error.response && error.response.status === 401) {
            showLoginForm();
        }
    }
}

// Task Management Functions
async function loadTaskStats() {
    try {
        const response = await axios.get('/api/tasks/stats', {
            headers: { Authorization: `Bearer ${authToken}` }
        });
        
        const stats = response.data;
        document.getElementById('totalTasks').textContent = stats.total_tasks;
        document.getElementById('completedTasks').textContent = stats.completed_tasks;
        
        // Update progress bar or other UI elements
        updateTaskProgress(stats);
    } catch (error) {
        console.error('Error loading task stats:', error);
    }
}

async function loadRecentTasks() {
    try {
        const response = await axios.get('/api/tasks/?limit=10', {
            headers: { Authorization: `Bearer ${authToken}` }
        });
        
        const tasks = response.data;
        renderTasks(tasks);
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

function renderTasks(tasks) {
    const tasksContainer = document.getElementById('tasksList');
    
    if (tasks.length === 0) {
        tasksContainer.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="fas fa-tasks fa-3x mb-3"></i>
                <p>No tasks yet. Create your first task!</p>
            </div>
        `;
        return;
    }
    
    tasksContainer.innerHTML = tasks.map(task => `
        <div class="task-item priority-${task.priority}">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <h6 class="mb-1">${task.title}</h6>
                    <p class="mb-2 text-muted small">${task.description || 'No description'}</p>
                    <div class="d-flex align-items-center gap-2">
                        <span class="task-status status-${task.status}">
                            ${task.status.replace('_', ' ').toUpperCase()}
                        </span>
                        <small class="text-muted">
                            <i class="fas fa-flag"></i> ${task.priority}
                        </small>
                        ${task.due_date ? `
                            <small class="text-muted">
                                <i class="fas fa-calendar"></i> ${new Date(task.due_date).toLocaleDateString()}
                            </small>
                        ` : ''}
                    </div>
                </div>
                <div class="dropdown">
                    <button class="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                        <i class="fas fa-ellipsis-v"></i>
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="#" onclick="editTask(${task.id})">
                            <i class="fas fa-edit"></i> Edit
                        </a></li>
                        <li><a class="dropdown-item" href="#" onclick="completeTask(${task.id})">
                            <i class="fas fa-check"></i> Complete
                        </a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item text-danger" href="#" onclick="deleteTask(${task.id})">
                            <i class="fas fa-trash"></i> Delete
                        </a></li>
                    </ul>
                </div>
            </div>
        </div>
    `).join('');
}

// Budget Management Functions
async function loadBudgetSummary() {
    try {
        const response = await axios.get('/api/budget/summary', {
            headers: { Authorization: `Bearer ${authToken}` }
        });
        
        const summary = response.data;
        document.getElementById('monthlyIncome').textContent = `$${summary.monthly_income.toFixed(2)}`;
        document.getElementById('monthlyExpenses').textContent = `$${summary.monthly_expenses.toFixed(2)}`;
        
        return summary;
    } catch (error) {
        console.error('Error loading budget summary:', error);
    }
}

async function loadBudgetChart() {
    try {
        const summary = await loadBudgetSummary();
        const ctx = document.getElementById('budgetChart').getContext('2d');
        
        budgetChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: summary.categories_summary.map(cat => cat.name),
                datasets: [{
                    data: summary.categories_summary.map(cat => cat.amount),
                    backgroundColor: summary.categories_summary.map(cat => cat.color),
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': $' + context.parsed.toFixed(2);
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading budget chart:', error);
    }
}

async function loadTrendsChart() {
    try {
        const response = await axios.get('/api/budget/analytics/monthly?months=6', {
            headers: { Authorization: `Bearer ${authToken}` }
        });
        
        const data = response.data;
        const ctx = document.getElementById('trendsChart').getContext('2d');
        
        trendsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.month),
                datasets: [
                    {
                        label: 'Income',
                        data: data.map(item => item.income),
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Expenses',
                        data: data.map(item => item.expenses),
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Net',
                        data: data.map(item => item.net),
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toFixed(0);
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': $' + context.parsed.y.toFixed(2);
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading trends chart:', error);
    }
}

// AI Functions
async function loadAIInsights() {
    try {
        const response = await axios.get('/api/ai/insights', {
            headers: { Authorization: `Bearer ${authToken}` }
        });
        
        const insights = response.data;
        renderAIInsights(insights);
    } catch (error) {
        console.error('Error loading AI insights:', error);
        // Show placeholder insights
        showPlaceholderInsights();
    }
}

function renderAIInsights(insights) {
    const container = document.getElementById('aiInsights');
    
    container.innerHTML = insights.map(insight => `
        <div class="col-md-4 mb-3">
            <div class="ai-insight-card">
                <div class="d-flex align-items-center mb-2">
                    <i class="${insight.icon} icon me-3"></i>
                    <h6 class="mb-0">${insight.title}</h6>
                </div>
                <p class="mb-0">${insight.message}</p>
            </div>
        </div>
    `).join('');
}

function showPlaceholderInsights() {
    const container = document.getElementById('aiInsights');
    container.innerHTML = `
        <div class="col-md-4 mb-3">
            <div class="ai-insight-card">
                <div class="d-flex align-items-center mb-2">
                    <i class="fas fa-lightbulb icon me-3"></i>
                    <h6 class="mb-0">Task Optimization</h6>
                </div>
                <p class="mb-0">You have 3 high-priority tasks due this week. Consider breaking them into smaller subtasks.</p>
            </div>
        </div>
        <div class="col-md-4 mb-3">
            <div class="ai-insight-card">
                <div class="d-flex align-items-center mb-2">
                    <i class="fas fa-chart-line icon me-3"></i>
                    <h6 class="mb-0">Budget Trend</h6>
                </div>
                <p class="mb-0">Your expenses have increased by 15% this month. Most spending is in the 'Food' category.</p>
            </div>
        </div>
        <div class="col-md-4 mb-3">
            <div class="ai-insight-card">
                <div class="d-flex align-items-center mb-2">
                    <i class="fas fa-target icon me-3"></i>
                    <h6 class="mb-0">Goal Achievement</h6>
                </div>
                <p class="mb-0">Great job! You're 80% on track with your monthly savings goal.</p>
            </div>
        </div>
    `;
}

// Modal Functions
function showAddTaskModal() {
    const modal = new bootstrap.Modal(document.getElementById('addTaskModal'));
    modal.show();
}

function showAddBudgetModal() {
    const modal = new bootstrap.Modal(document.getElementById('addBudgetModal'));
    modal.show();
}

async function addTask() {
    const taskData = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        priority: document.getElementById('taskPriority').value,
        due_date: document.getElementById('taskDueDate').value || null,
        estimated_duration: parseInt(document.getElementById('taskDuration').value) || null
    };
    
    try {
        await axios.post('/api/tasks/', taskData, {
            headers: { Authorization: `Bearer ${authToken}` }
        });
        
        // Close modal and refresh tasks
        bootstrap.Modal.getInstance(document.getElementById('addTaskModal')).hide();
        document.getElementById('addTaskForm').reset();
        await loadRecentTasks();
        await loadTaskStats();
        
        showNotification('Task added successfully!', 'success');
    } catch (error) {
        console.error('Error adding task:', error);
        showNotification('Error adding task', 'error');
    }
}

async function addBudgetItem() {
    const budgetData = {
        title: document.getElementById('budgetTitle').value,
        description: document.getElementById('budgetDescription').value,
        amount: parseFloat(document.getElementById('budgetAmount').value),
        transaction_type: document.getElementById('budgetType').value,
        transaction_date: document.getElementById('budgetDate').value || null
    };
    
    try {
        await axios.post('/api/budget/', budgetData, {
            headers: { Authorization: `Bearer ${authToken}` }
        });
        
        // Close modal and refresh data
        bootstrap.Modal.getInstance(document.getElementById('addBudgetModal')).hide();
        document.getElementById('addBudgetForm').reset();
        await loadBudgetSummary();
        await loadBudgetChart();
        await loadTrendsChart();
        
        showNotification('Transaction added successfully!', 'success');
    } catch (error) {
        console.error('Error adding budget item:', error);
        showNotification('Error adding transaction', 'error');
    }
}

// Voice Command Functions
async function startVoiceCommand() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        showNotification('Voice recognition not supported in this browser', 'error');
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    
    const voiceBtn = document.getElementById('voiceBtn');
    const originalText = voiceBtn.innerHTML;
    
    voiceBtn.innerHTML = '<i class="fas fa-microphone"></i> Listening...';
    voiceBtn.classList.add('listening');
    
    showVoiceStatus('Listening...', 'info');
    
    recognition.onresult = async function(event) {
        const command = event.results[0][0].transcript;
        showVoiceStatus(`Processing: "${command}"`, 'info');
        
        try {
            const response = await axios.post('/api/ai/voice-command', {
                command: command
            }, {
                headers: { Authorization: `Bearer ${authToken}` }
            });
            
            showVoiceStatus(response.data.message, 'success');
            
            // Refresh dashboard if needed
            if (response.data.action_performed) {
                await initializeDashboard();
            }
        } catch (error) {
            console.error('Error processing voice command:', error);
            showVoiceStatus('Sorry, I couldn\'t process that command', 'error');
        }
    };
    
    recognition.onerror = function(event) {
        console.error('Voice recognition error:', event.error);
        showVoiceStatus('Voice recognition error', 'error');
    };
    
    recognition.onend = function() {
        voiceBtn.innerHTML = originalText;
        voiceBtn.classList.remove('listening');
        
        setTimeout(() => {
            hideVoiceStatus();
        }, 3000);
    };
    
    recognition.start();
}

// Utility Functions
function showVoiceStatus(message, type) {
    const status = document.getElementById('voiceStatus');
    const colors = {
        info: 'bg-info',
        success: 'bg-success', 
        error: 'bg-danger',
        warning: 'bg-warning'
    };
    
    status.innerHTML = `
        <div class="voice-status show ${colors[type]} text-white">
            <i class="fas fa-microphone me-2"></i>
            ${message}
        </div>
    `;
}

function hideVoiceStatus() {
    document.getElementById('voiceStatus').innerHTML = '';
}

function showNotification(message, type) {
    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 1060; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

async function completeTask(taskId) {
    try {
        await axios.post(`/api/tasks/${taskId}/complete`, {}, {
            headers: { Authorization: `Bearer ${authToken}` }
        });
        
        await loadRecentTasks();
        await loadTaskStats();
        showNotification('Task completed!', 'success');
    } catch (error) {
        console.error('Error completing task:', error);
        showNotification('Error completing task', 'error');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }
    
    try {
        await axios.delete(`/api/tasks/${taskId}`, {
            headers: { Authorization: `Bearer ${authToken}` }
        });
        
        await loadRecentTasks();
        await loadTaskStats();
        showNotification('Task deleted!', 'success');
    } catch (error) {
        console.error('Error deleting task:', error);
        showNotification('Error deleting task', 'error');
    }
}

function updateTaskProgress(stats) {
    // You can add progress bars or other visual indicators here
    if (stats.total_tasks > 0) {
        const completionRate = (stats.completed_tasks / stats.total_tasks) * 100;
        // Update any progress indicators
    }
}

function showLoginForm() {
    // Simple login form (you can enhance this)
    document.body.innerHTML = `
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header text-center">
                            <h4><i class="fas fa-tasks me-2"></i>Tudu Login</h4>
                        </div>
                        <div class="card-body">
                            <form id="loginForm">
                                <div class="mb-3">
                                    <label for="username" class="form-label">Username</label>
                                    <input type="text" class="form-control" id="username" required>
                                </div>
                                <div class="mb-3">
                                    <label for="password" class="form-label">Password</label>
                                    <input type="password" class="form-control" id="password" required>
                                </div>
                                <button type="submit" class="btn btn-primary w-100">Login</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('loginForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        formData.append('username', document.getElementById('username').value);
        formData.append('password', document.getElementById('password').value);
        
        try {
            const response = await axios.post('/auth/login', formData);
            localStorage.setItem('authToken', response.data.access_token);
            location.reload();
        } catch (error) {
            alert('Login failed. Please check your credentials.');
        }
    });
}