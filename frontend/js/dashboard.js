/**
 * Dashboard Page Logic
 * Loads stats and renders 6 interactive charts.
 */

const API_BASE_URL = "https://smart-study-analyzer-api.onrender.com";


// Store chart instances so we can destroy/recreate them
let charts = {
    daily: null,
    subject: null,
    distraction: null,
    focusTrend: null,
    weekly: null,
    breakFocus: null
};

// Current student being viewed
let currentStudent = null;


// ===========================================
// Initialization
// ===========================================
document.addEventListener('DOMContentLoaded', async () => {
    await loadStudents();
    
    // Auto-select first student if exists
    const select = document.getElementById('studentSelect');
    if (select.options.length > 1) {
        select.selectedIndex = 1; // First real student
        currentStudent = select.value;
        await loadDashboard(currentStudent);
    }
    
    // Listen for student changes
    select.addEventListener('change', async (e) => {
        currentStudent = e.target.value;
        if (currentStudent) {
            await loadDashboard(currentStudent);
        }
    });
});


// ===========================================
// Load list of students
// ===========================================
async function loadStudents() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/study/students`);
        const result = await response.json();
        
        const select = document.getElementById('studentSelect');
        select.innerHTML = '<option value="">-- Select Student --</option>';
        
        if (result.success && result.data.length > 0) {
            result.data.forEach(student => {
                const option = document.createElement('option');
                option.value = student.name;
                option.textContent = `${student.name} (${student.session_count} sessions)`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Failed to load students:', error);
    }
}


// ===========================================
// Load all dashboard data
// ===========================================
async function loadDashboard(studentName) {
    showLoading(true);
    hideEmptyState();
    
    try {
        // Load stats
        await loadStats(studentName);
        
        // Load all charts in parallel
        await Promise.all([
            loadDailyHours(studentName),
            loadSubjectDistribution(studentName),
            loadDistractionDistribution(studentName),
            loadFocusTrend(studentName),
            loadWeeklyHours(studentName),
            loadBreakFocus(studentName),
            loadCoachReport(studentName)
        ]);
        
        
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    } finally {
        showLoading(false);
    }
}


// ===========================================
// Load Stats Cards
// ===========================================
async function loadStats(studentName) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/stats?student_name=${encodeURIComponent(studentName)}`);
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            document.getElementById('statSessions').textContent = data.total_sessions;
            document.getElementById('statHours').textContent = data.total_hours;
            document.getElementById('statFocus').textContent = data.average_focus;
            document.getElementById('statSubject').textContent = data.most_studied_subject;
            document.getElementById('statLongest').textContent = data.longest_session;
            document.getElementById('statGoals').textContent = `${data.goal_completion_rate}%`;
            
            // Check if no data
            if (data.total_sessions === 0) {
                showEmptyState();
            }
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}


// ===========================================
// Chart 1: Daily Study Hours (Line Chart)
// ===========================================
async function loadDailyHours(studentName) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/daily-hours?student_name=${encodeURIComponent(studentName)}&days=30`);
        const result = await response.json();
        
        if (result.success) {
            renderLineChart(
                'dailyHoursChart',
                'daily',
                result.data.labels,
                [{
                    label: 'Study Hours',
                    data: result.data.hours,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            );
        }
    } catch (error) {
        console.error('Failed to load daily hours:', error);
    }
}


// ===========================================
// Chart 2: Subject Distribution (Bar Chart)
// ===========================================
async function loadSubjectDistribution(studentName) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/subject-distribution?student_name=${encodeURIComponent(studentName)}`);
        const result = await response.json();
        
        if (result.success) {
            renderBarChart(
                'subjectChart',
                'subject',
                result.data.labels,
                result.data.hours,
                '#10b981'
            );
        }
    } catch (error) {
        console.error('Failed to load subject distribution:', error);
    }
}


// ===========================================
// Chart 3: Distraction Distribution (Doughnut)
// ===========================================
async function loadDistractionDistribution(studentName) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/distraction-distribution?student_name=${encodeURIComponent(studentName)}`);
        const result = await response.json();
        
        if (result.success) {
            renderDoughnutChart(
                'distractionChart',
                'distraction',
                result.data.labels,
                result.data.counts
            );
        }
    } catch (error) {
        console.error('Failed to load distraction distribution:', error);
    }
}


// ===========================================
// Chart 4: Focus Trend (Line Chart)
// ===========================================
async function loadFocusTrend(studentName) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/focus-trend?student_name=${encodeURIComponent(studentName)}`);
        const result = await response.json();
        
        if (result.success) {
            renderLineChart(
                'focusTrendChart',
                'focusTrend',
                result.data.labels,
                [{
                    label: 'Focus Rating',
                    data: result.data.focus,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            );
        }
    } catch (error) {
        console.error('Failed to load focus trend:', error);
    }
}


// ===========================================
// Chart 5: Weekly Hours (Bar Chart)
// ===========================================
async function loadWeeklyHours(studentName) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard/weekly-hours?student_name=${encodeURIComponent(studentName)}`);
        const result = await response.json();
        
        if (result.success) {
            renderBarChart(
                'weeklyChart',
                'weekly',
                result.data.labels,
                result.data.hours,
                '#8b5cf6'
            );
        }
    } catch (error) {
        console.error('Failed to load weekly hours:', error);
    }
}


// ===========================================
// Chart 6: Break vs Focus (Scatter)
// ===========================================
// ===========================================
// Chart 6: Break vs Focus (Scatter)
// ===========================================
async function loadBreakFocus(studentName) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/study/sessions?student_name=${encodeURIComponent(studentName)}&limit=100`);
        const result = await response.json();
        
        if (result.success && result.data.length > 0) {
            const scatterData = result.data.map(s => ({
                x: s.break_minutes || 0,
                y: s.focus_rating
            }));
            
            // Check if there's actual variation in break minutes
            const breakValues = scatterData.map(d => d.x);
            const hasVariation = Math.max(...breakValues) - Math.min(...breakValues) > 0;
            
            if (!hasVariation) {
                // Add slight variation for visualization
                scatterData.forEach((d, i) => {
                    d.x = d.x + (i * 0.5);  // tiny spread
                });
            }
            
            renderScatterChart(
                'breakFocusChart',
                'breakFocus',
                scatterData
            );
        } else {
            // Show empty placeholder
            renderEmptyChart('breakFocusChart', 'No break data yet');
        }
    } catch (error) {
        console.error('Failed to load break vs focus:', error);
    }
}


// ===========================================
// Chart Renderers
// ===========================================
function renderLineChart(canvasId, chartKey, labels, datasets) {
    if (charts[chartKey]) charts[chartKey].destroy();
    
    const ctx = document.getElementById(canvasId).getContext('2d');
    charts[chartKey] = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true, position: 'top' }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}


function renderBarChart(canvasId, chartKey, labels, data, color) {
    if (charts[chartKey]) charts[chartKey].destroy();
    
    const ctx = document.getElementById(canvasId).getContext('2d');
    charts[chartKey] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Hours',
                data,
                backgroundColor: color,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}


function renderDoughnutChart(canvasId, chartKey, labels, data) {
    if (charts[chartKey]) charts[chartKey].destroy();
    
    const colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'];
    
    const ctx = document.getElementById(canvasId).getContext('2d');
    charts[chartKey] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right' }
            }
        }
    });
}


function renderScatterChart(canvasId, chartKey, data) {
    if (charts[chartKey]) charts[chartKey].destroy();
    
    const ctx = document.getElementById(canvasId).getContext('2d');
    charts[chartKey] = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Sessions',
                data,
                backgroundColor: '#ec4899',
                borderColor: '#ec4899',
                pointRadius: 8,
                pointHoverRadius: 12
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `Break: ${ctx.parsed.x} min, Focus: ${ctx.parsed.y}/5`
                    }
                }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Break Minutes' },
                    beginAtZero: true
                },
                y: {
                    title: { display: true, text: 'Focus Rating' },
                    min: 0,
                    max: 5
                }
            }
        }
    });
}
// ===========================================
// AI Study Coach
// ===========================================
async function loadCoachReport(studentName) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/coach/report?student_name=${encodeURIComponent(studentName)}`);
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            
            // Productivity Score
            document.getElementById('productivityScore').textContent = data.productivity.score;
            document.getElementById('productivityGrade').textContent = `Grade: ${data.productivity.grade}`;
            document.getElementById('productivityLevel').textContent = data.productivity.level;
            
            // Personality
            document.getElementById('personalityIcon').textContent = data.personality.icon;
            document.getElementById('personalityName').textContent = data.personality.name;
            document.getElementById('personalityDescription').textContent = data.personality.description;
            
            // Recommendations
            const recList = document.getElementById('recommendationsList');
            if (data.recommendations && data.recommendations.length > 0) {
                recList.innerHTML = data.recommendations.map(rec => `
                    <div class="recommendation-item ${rec.type}">
                        <div class="recommendation-icon">${rec.icon}</div>
                        <div class="recommendation-content">
                            <h4>${rec.title}</h4>
                            <p>${rec.message}</p>
                        </div>
                    </div>
                `).join('');
            }
            
            // Achievements
            const achList = document.getElementById('achievementsList');
            if (data.achievements && data.achievements.length > 0) {
                achList.innerHTML = data.achievements.map(ach => `
                    <div class="achievement-badge">
                        <div class="achievement-icon">${ach.icon}</div>
                        <div class="achievement-name">${ach.name}</div>
                        <div class="achievement-desc">${ach.description}</div>
                    </div>
                `).join('');
            } else {
                achList.innerHTML = `
                    <div class="no-achievements">
                        <p>🏆 No achievements unlocked yet. Keep studying to earn badges!</p>
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Failed to load coach report:', error);
    }
}


// ===========================================
// UI Helpers
// ===========================================
function showLoading(show) {
    document.getElementById('loadingState').classList.toggle('hidden', !show);
}

function showEmptyState() {
    document.getElementById('emptyState').classList.remove('hidden');
}

function hideEmptyState() {
    document.getElementById('emptyState').classList.add('hidden');
}
function renderEmptyChart(canvasId, message) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = '16px Inter, sans-serif';
    ctx.fillStyle = '#94a3b8';
    ctx.textAlign = 'center';
    ctx.fillText(message, canvas.width / 2, canvas.height / 2);
}

