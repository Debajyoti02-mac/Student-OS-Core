/**
 * STUDENT OS AI - JAVASCRIPT CLIENT
 */

const API_BASE = '/api';

// DOM Elements
const studentIdInput = document.getElementById('studentIdInput');
const goalInput = document.getElementById('goalInput');
const goalForm = document.getElementById('goalForm');
const btnGeneratePlan = document.getElementById('btnGeneratePlan');
const dashboardContainer = document.getElementById('dashboardContainer');
const emptyState = document.getElementById('emptyState');

const currentTaskTitle = document.getElementById('currentTaskTitle');
const nextTaskLabel = document.getElementById('nextTaskLabel');
const btnMarkComplete = document.getElementById('btnMarkComplete');
const btnImStuck = document.getElementById('btnImStuck');
const tasksList = document.getElementById('tasksList');
const taskCountBadge = document.getElementById('taskCountBadge');

const progressPercentage = document.getElementById('progressPercentage');
const progressBarFill = document.getElementById('progressBarFill');
const statCompleted = document.getElementById('statCompleted');
const statRemaining = document.getElementById('statRemaining');
const statTotal = document.getElementById('statTotal');

const skillsContainer = document.getElementById('skillsContainer');
const roadmapContainer = document.getElementById('roadmapContainer');
const projectDescription = document.getElementById('projectDescription');

const historyModal = document.getElementById('historyModal');
const btnViewHistory = document.getElementById('btnViewHistory');
const btnCloseModal = document.getElementById('btnCloseModal');
const historyLogsContainer = document.getElementById('historyLogsContainer');
const toastContainer = document.getElementById('toastContainer');

// State
let currentStudentId = localStorage.getItem('student_os_id') || generateStudentId();
studentIdInput.value = currentStudentId;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  if (currentStudentId) {
    loadExistingStudentState(currentStudentId);
  }
});

function generateStudentId() {
  const rand = Math.random().toString(36).substring(2, 7);
  const id = `student_${rand}`;
  localStorage.setItem('student_os_id', id);
  return id;
}

function setupEventListeners() {
  // Goal Form Submission
  goalForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const studentId = studentIdInput.value.trim();
    const goal = goalInput.value.trim();

    if (!studentId || !goal) {
      showToast('Please provide both a Student ID and a Goal.', 'warning');
      return;
    }

    currentStudentId = studentId;
    localStorage.setItem('student_os_id', studentId);
    await initializeGoal(studentId, goal);
  });

  // Suggestion Chips
  document.querySelectorAll('.chip-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      goalInput.value = btn.dataset.goal;
      goalInput.focus();
    });
  });

  // Action: Mark Complete
  btnMarkComplete.addEventListener('click', async () => {
    await updateStudentStatus('progressing');
  });

  // Action: I'm Stuck
  btnImStuck.addEventListener('click', async () => {
    await updateStudentStatus('stuck');
  });

  // Modal actions
  btnViewHistory.addEventListener('click', loadHistoryLogs);
  btnCloseModal.addEventListener('click', () => historyModal.classList.remove('open'));
  historyModal.addEventListener('click', (e) => {
    if (e.target === historyModal) historyModal.classList.remove('open');
  });
}

/**
 * Initialize / Set Goal
 */
async function initializeGoal(studentId, goal) {
  setButtonLoading(btnGeneratePlan, true, 'Generating Plan...');
  try {
    const res = await fetch(`${API_BASE}/student/goal`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: studentId, goal: goal })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to initialize goal.');
    }

    const state = await res.json();
    renderStudentState(state);
    showToast('🎉 Learning roadmap and tasks generated successfully!', 'success');
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    setButtonLoading(btnGeneratePlan, false, '✨ Generate Learning OS');
  }
}

/**
 * Update Student Status (progressing or stuck)
 */
async function updateStudentStatus(status) {
  const btn = status === 'progressing' ? btnMarkComplete : btnImStuck;
  const originalText = status === 'progressing' ? '✅ Mark as Complete & Advance' : "🧩 I'm Stuck (Break Down Task)";
  const loadingText = status === 'progressing' ? 'Advancing...' : 'Adapting Tasks...';

  setButtonLoading(btn, true, loadingText);
  btnMarkComplete.disabled = true;
  btnImStuck.disabled = true;

  try {
    const res = await fetch(`${API_BASE}/student/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: currentStudentId, status: status })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to update status.');
    }

    const state = await res.json();
    renderStudentState(state);

    if (status === 'progressing') {
      showToast('🌟 Great job! Task marked complete and next milestone set.', 'success');
    } else {
      showToast('🧠 Agent adaptively simplified the task into smaller steps!', 'warning');
    }
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    setButtonLoading(btn, false, originalText);
    btnMarkComplete.disabled = false;
    btnImStuck.disabled = false;
  }
}

/**
 * Load existing state for a returning student
 */
async function loadExistingStudentState(studentId) {
  try {
    const res = await fetch(`${API_BASE}/student/state/${encodeURIComponent(studentId)}`);
    if (res.ok) {
      const state = await res.json();
      if (state.goal) {
        goalInput.value = state.goal;
        renderStudentState(state);
      }
    }
  } catch (e) {
    // Session not found or fresh state, keep empty state
  }
}

/**
 * Render State into DOM
 */
function renderStudentState(state) {
  emptyState.style.display = 'none';
  dashboardContainer.style.display = 'grid';

  // Active Task
  currentTaskTitle.textContent = state.current_task || 'All tasks completed 🎉';
  nextTaskLabel.textContent = state.next_task || 'None left';

  // Progress Bar & Stats
  const totalTasks = (state.priority_tasks || []).length;
  const completedTasks = (state.completed_tasks || []).length;
  const remaining = Math.max(0, totalTasks - completedTasks);
  const pct = Math.min(100, Math.max(0, state.progress || (totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0)));

  progressPercentage.textContent = `${pct}%`;
  progressBarFill.style.width = `${pct}%`;
  statCompleted.textContent = completedTasks;
  statRemaining.textContent = remaining;
  statTotal.textContent = totalTasks;

  // Render Priority Tasks Queue
  taskCountBadge.textContent = `${totalTasks} Tasks`;
  tasksList.innerHTML = '';
  (state.priority_tasks || []).forEach((task, idx) => {
    const isCompleted = (state.completed_tasks || []).includes(task);
    const isActive = task === state.current_task;

    const item = document.createElement('div');
    item.className = `task-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`;
    item.innerHTML = `
      <div class="task-bullet">${isCompleted ? '✓' : idx + 1}</div>
      <div class="task-text">${escapeHtml(task)}</div>
    `;
    tasksList.appendChild(item);
  });

  // Render Skills
  skillsContainer.innerHTML = '';
  (state.skills || []).forEach(skill => {
    const badge = document.createElement('span');
    badge.className = 'skill-badge';
    badge.textContent = skill;
    skillsContainer.appendChild(badge);
  });

  // Render Project
  projectDescription.textContent = state.first_project || 'No project assigned yet.';

  // Render Roadmap Timeline
  roadmapContainer.innerHTML = '';
  (state.roadmap || []).forEach((step, idx) => {
    const div = document.createElement('div');
    div.className = 'roadmap-step';
    div.innerHTML = `
      <div class="step-num">${idx + 1}</div>
      <div>${escapeHtml(step)}</div>
    `;
    roadmapContainer.appendChild(div);
  });
}

/**
 * Load History / Agent Reasoning Logs
 */
async function loadHistoryLogs() {
  historyModal.classList.add('open');
  historyLogsContainer.innerHTML = '<div style="text-align:center; padding:20px;"><span class="spinner"></span> Loading logs...</div>';

  try {
    const res = await fetch(`${API_BASE}/student/history/${encodeURIComponent(currentStudentId)}`);
    if (!res.ok) throw new Error('No logs found for this session.');

    const logs = await res.json();
    if (!logs || logs.length === 0) {
      historyLogsContainer.innerHTML = '<p style="color:var(--text-muted); text-align:center; padding:20px;">No logs recorded yet.</p>';
      return;
    }

    historyLogsContainer.innerHTML = '';
    logs.forEach((log) => {
      const card = document.createElement('div');
      card.style.background = 'rgba(15, 23, 42, 0.6)';
      card.style.border = '1px solid var(--border-subtle)';
      card.style.borderRadius = 'var(--radius-md)';
      card.style.padding = '14px';
      card.style.marginBottom = '12px';

      const roleBadge = document.createElement('span');
      roleBadge.className = 'card-tag';
      roleBadge.textContent = log.role.toUpperCase();
      
      const content = document.createElement('div');
      content.style.fontSize = '13px';
      content.style.color = 'var(--text-primary)';
      content.style.whiteSpace = 'pre-wrap';
      content.style.marginTop = '6px';
      content.textContent = log.content;

      card.appendChild(roleBadge);
      card.appendChild(content);
      historyLogsContainer.appendChild(card);
    });
  } catch (err) {
    historyLogsContainer.innerHTML = `<p style="color:var(--danger); text-align:center; padding:20px;">${escapeHtml(err.message)}</p>`;
  }
}

/**
 * Helpers
 */
function setButtonLoading(btn, isLoading, text) {
  if (isLoading) {
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> <span>${escapeHtml(text)}</span>`;
  } else {
    btn.disabled = false;
    btn.innerHTML = `<span>${text}</span>`;
  }
}

function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${type === 'success' ? '✅' : type === 'warning' ? '⚠️' : '❌'}</span> <span>${escapeHtml(message)}</span>`;

  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
