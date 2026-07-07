/**
 * Log Session Page - Form Logic + Recent Sessions
 * Handles form submission, validation, API calls, and session management.
 */

const API_BASE_URL = "https://smart-study-analyzer-api.onrender.com";


let deleteTargetId = null;


// ===========================================
// Initialization
// ===========================================
document.addEventListener('DOMContentLoaded', () => {
    // Set today's date as default
    const dateInput = document.getElementById('study_date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
        dateInput.max = today;
    }
    
    setupRatingButtons();
    setupFormSubmit();
    setupRecentSessions();
});


// ===========================================
// Rating Button Logic
// ===========================================
function setupRatingButtons() {
    const groups = document.querySelectorAll('.rating-group');
    
    groups.forEach(group => {
        const buttons = group.querySelectorAll('.rating-btn');
        const fieldName = group.dataset.name;
        const hiddenInput = document.getElementById(fieldName);
        
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                buttons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                hiddenInput.value = btn.dataset.value;
            });
        });
    });
}


// ===========================================
// Form Submit Handler
// ===========================================
function setupFormSubmit() {
    const form = document.getElementById('studyForm');
    const submitBtn = document.getElementById('submitBtn');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const focusRating = document.getElementById('focus_rating').value;
        const distractionLevel = document.getElementById('distraction_level').value;
        
        if (!focusRating) {
            showMessage('Please select a focus rating', 'error');
            return;
        }
        
        if (!distractionLevel) {
            showMessage('Please select a distraction level', 'error');
            return;
        }
        
        const formData = new FormData(form);
        const data = {
            student_name: formData.get('student_name'),
            study_date: formData.get('study_date'),
            study_time: formData.get('study_time') || null,
            subject: formData.get('subject'),
            study_hours: parseFloat(formData.get('study_hours')),
            break_minutes: parseInt(formData.get('break_minutes') || 0),
            focus_rating: parseInt(focusRating),
            distraction_level: parseInt(distractionLevel),
            study_location: formData.get('study_location') || null,
            study_method: formData.get('study_method') || null,
            mood_before: formData.get('mood_before') || null,
            mood_after: formData.get('mood_after') || null,
            goal_completed: formData.has('goal_completed'),
            notes: formData.get('notes') || null
        };
        
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Saving...';
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/study/sessions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                showMessage(`✅ Session saved! ID: #${result.data.id}`, 'success');
                
                setTimeout(() => {
                    form.reset();
                    document.querySelectorAll('.rating-btn.active').forEach(b => b.classList.remove('active'));
                    document.getElementById('study_date').value = new Date().toISOString().split('T')[0];
                    submitBtn.disabled = false;
                    submitBtn.textContent = '💾 Save Study Session';
                    loadRecentSessions();
                }, 2000);
                
            } else {
                showMessage(`❌ Error: ${result.error}`, 'error');
                submitBtn.disabled = false;
                submitBtn.textContent = '💾 Save Study Session';
            }
            
        } catch (error) {
            showMessage(`❌ Network error: ${error.message}. Make sure the backend is running.`, 'error');
            submitBtn.disabled = false;
            submitBtn.textContent = '💾 Save Study Session';
        }
    });
}


// ===========================================
// Show Message
// ===========================================
function showMessage(message, type) {
    const messageBox = document.getElementById('messageBox');
    messageBox.textContent = message;
    messageBox.className = `message-box ${type}`;
    messageBox.classList.remove('hidden');
    
    if (type === 'error') {
        setTimeout(() => messageBox.classList.add('hidden'), 5000);
    }
    
    messageBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
}


// ===========================================
// Recent Sessions
// ===========================================
function setupRecentSessions() {
    const refreshBtn = document.getElementById('refreshBtn');
    const cancelBtn = document.getElementById('cancelDelete');
    const confirmBtn = document.getElementById('confirmDelete');
    
    if (refreshBtn) refreshBtn.addEventListener('click', loadRecentSessions);
    if (cancelBtn) cancelBtn.addEventListener('click', closeDeleteModal);
    if (confirmBtn) confirmBtn.addEventListener('click', confirmDelete);
    
    // Auto-load if name field already has value
    const nameField = document.getElementById('student_name');
    if (nameField && nameField.value.trim()) {
        loadRecentSessions();
    }
    
    // Listen for name changes
    if (nameField) {
        nameField.addEventListener('blur', () => {
            if (nameField.value.trim()) {
                loadRecentSessions();
            }
        });
    }
}


async function loadRecentSessions() {
    const list = document.getElementById('sessionsList');
    if (!list) return;
    
    const studentName = document.getElementById('student_name').value.trim();
    
    if (!studentName) {
        list.innerHTML = '<p class="no-sessions">💡 Enter your name above to see your sessions here.</p>';
        return;
    }
    
    list.innerHTML = '<p class="no-sessions">⏳ Loading your sessions...</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/study/sessions?student_name=${encodeURIComponent(studentName)}&limit=20`);
        const result = await response.json();
        
        if (result.success && result.data.length > 0) {
            list.innerHTML = result.data.map(session => `
                <div class="session-item">
                    <div class="session-info">
                        <div class="session-subject">
                            📚 ${session.subject}
                            <span class="session-date">${formatDate(session.study_date)}</span>
                        </div>
                        <div class="session-meta">
                            <span>⏱️ ${session.study_hours}h</span>
                            <span>☕ ${session.break_minutes || 0}m</span>
                            <span>📍 ${session.study_location || 'N/A'}</span>
                            <div class="session-badges">
                                <span class="badge badge-focus">Focus: ${session.focus_rating}/5</span>
                                ${session.goal_completed ? '<span class="badge badge-goal">✅ Goal</span>' : ''}
                            </div>
                        </div>
                    </div>
                    <button type="button" class="btn-delete" onclick="showDeleteModal(${session.id})">
                        🗑️ Delete
                    </button>
                </div>
            `).join('');
        } else {
            list.innerHTML = '<p class="no-sessions">📭 No sessions yet. Log your first one above!</p>';
        }
    } catch (error) {
        list.innerHTML = `<p class="no-sessions">❌ Error: ${error.message}</p>`;
    }
}


function formatDate(dateStr) {
    if (!dateStr) return '';
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
        return dateStr;
    }
}


// ===========================================
// Delete Functions
// ===========================================
function showDeleteModal(sessionId) {
    deleteTargetId = sessionId;
    document.getElementById('deleteModal').classList.remove('hidden');
}

function closeDeleteModal() {
    deleteTargetId = null;
    document.getElementById('deleteModal').classList.add('hidden');
}

async function confirmDelete() {
    if (!deleteTargetId) return;
    
    const confirmBtn = document.getElementById('confirmDelete');
    confirmBtn.disabled = true;
    confirmBtn.textContent = '⏳ Deleting...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/study/sessions/${deleteTargetId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            closeDeleteModal();
            await loadRecentSessions();
            showMessage('✅ Session deleted successfully!', 'success');
        } else {
            showMessage(`❌ Error: ${result.error}`, 'error');
        }
    } catch (error) {
        showMessage(`❌ Network error: ${error.message}`, 'error');
    } finally {
        confirmBtn.disabled = false;
        confirmBtn.textContent = 'Delete';
    }
}
