/* FinPilot Frontend Application Logic */

// Global state
let currentUser = null;
let currentUserId = null;

// API Configuration
const API_BASE_URL = '/api';

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    const savedUser = localStorage.getItem('finpilot_user');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        currentUserId = currentUser.user_id;
        showPage('dashboard');
        loadDashboard();
    } else {
        showPage('auth');
    }
});

/* ===== NAVIGATION ===== */
function navigate(page) {
    if (!currentUser) {
        showPage('auth');
        return;
    }
    showPage(`${page}-page`);
    
    // Load page-specific data
    if (page === 'dashboard') loadDashboard();
    if (page === 'expenses') loadExpenses();
    if (page === 'budgets') loadBudgets();
    if (page === 'savings') loadSavingsGoals();
    if (page === 'advisor') loadAdvisorData();
    if (page === 'profile') loadProfile();
}

function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    const page = document.getElementById(pageId);
    if (page) {
        page.classList.add('active');
    }
}

/* ===== AUTHENTICATION ===== */
function switchAuthTab(tab) {
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    
    document.getElementById(`${tab}-form`).classList.add('active');
    event.target.classList.add('active');
}

function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    // Simulate login (in production, call actual API)
    if (username && password) {
        currentUser = {
            user_id: 1,
            username: username,
            email: `${username}@finpilot.com`,
            full_name: username
        };
        currentUserId = 1;
        
        localStorage.setItem('finpilot_user', JSON.stringify(currentUser));
        showPage('dashboard-page');
        loadDashboard();
        
        // Clear form
        document.getElementById('login-username').value = '';
        document.getElementById('login-password').value = '';
    }
}

function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const fullname = document.getElementById('register-fullname').value;
    const password = document.getElementById('register-password').value;
    
    if (username && email && password) {
        currentUser = {
            user_id: 1,
            username: username,
            email: email,
            full_name: fullname
        };
        currentUserId = 1;
        
        localStorage.setItem('finpilot_user', JSON.stringify(currentUser));
        showPage('dashboard-page');
        loadDashboard();
        
        // Clear form
        document.getElementById('register-username').value = '';
        document.getElementById('register-email').value = '';
        document.getElementById('register-fullname').value = '';
        document.getElementById('register-password').value = '';
    }
}

function handleLogout() {
    currentUser = null;
    currentUserId = null;
    localStorage.removeItem('finpilot_user');
    showPage('auth-page');
    resetAuthForms();
}

function resetAuthForms() {
    document.getElementById('login-form').classList.add('active');
    document.getElementById('register-form').classList.remove('active');
    document.querySelectorAll('.tab-btn')[0].classList.add('active');
    document.querySelectorAll('.tab-btn')[1].classList.remove('active');
}

/* ===== DASHBOARD ===== */
function loadDashboard() {
    const welcomeMsg = document.getElementById('welcome-message');
    welcomeMsg.textContent = `Welcome back, ${currentUser.full_name || currentUser.username}!`;
    
    // Load spending data (mock data for demo)
    document.getElementById('monthly-spending').textContent = '$2,450.50';
    document.getElementById('daily-spending').textContent = '$81.68';
    document.getElementById('savings-progress').textContent = '65%';
    document.getElementById('budget-status').textContent = 'On Track';
    
    loadRecommendations();
}

function loadRecommendations() {
    const recommendations = [
        '💡 You\'re spending 20% more on entertainment than last month. Consider cutting back.',
        '✅ Great job! You\'re under budget for groceries this month.',
        '⚠️ Your transport costs are approaching 80% of your monthly budget.',
        '💰 You\'ve saved $500 this month. Keep up the great work!',
        '📊 Increase your savings goal by $100/month to reach your vacation fund by July.'
    ];
    
    const list = document.getElementById('recommendations-list');
    list.innerHTML = recommendations.map(rec => 
        `<div class="recommendation-item">${rec}</div>`
    ).join('');
}

/* ===== EXPENSES ===== */
function showExpenseForm() {
    const form = document.getElementById('expense-form');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

function addExpense(event) {
    event.preventDefault();
    
    const amount = parseFloat(document.getElementById('expense-amount').value);
    const category = document.getElementById('expense-category').value;
    const description = document.getElementById('expense-description').value;
    
    if (amount > 0 && category) {
        const expense = {
            id: Math.random(),
            date: new Date().toLocaleDateString(),
            category: category,
            description: description || 'No description',
            amount: amount.toFixed(2)
        };
        
        // Save to localStorage (in production, send to API)
        let expenses = JSON.parse(localStorage.getItem('finpilot_expenses') || '[]');
        expenses.push(expense);
        localStorage.setItem('finpilot_expenses', JSON.stringify(expenses));
        
        // Clear form
        document.getElementById('expense-form').reset();
        loadExpenses();
    }
}

function loadExpenses() {
    const expenses = JSON.parse(localStorage.getItem('finpilot_expenses') || '[]');
    const tbody = document.getElementById('expenses-list');
    
    if (expenses.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-muted">No expenses yet. Add one to get started!</td></tr>';
        return;
    }
    
    const categoryEmojis = {
        'food': '🍔',
        'transport': '🚗',
        'utilities': '💡',
        'entertainment': '🎬',
        'health': '🏥',
        'shopping': '🛍️',
        'education': '📚',
        'other': '📌'
    };
    
    tbody.innerHTML = expenses.map((exp, idx) => `
        <tr>
            <td>${exp.date}</td>
            <td>${categoryEmojis[exp.category]} ${exp.category}</td>
            <td>${exp.description}</td>
            <td>$${exp.amount}</td>
            <td>
                <button class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" 
                    onclick="deleteExpense(${idx})">Delete</button>
            </td>
        </tr>
    `).join('');
}

function deleteExpense(index) {
    let expenses = JSON.parse(localStorage.getItem('finpilot_expenses') || '[]');
    expenses.splice(index, 1);
    localStorage.setItem('finpilot_expenses', JSON.stringify(expenses));
    loadExpenses();
}

/* ===== BUDGETS ===== */
function showBudgetForm() {
    const form = document.getElementById('budget-form');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

function addBudget(event) {
    event.preventDefault();
    
    const name = document.getElementById('budget-name').value;
    const category = document.getElementById('budget-category').value;
    const limit = parseFloat(document.getElementById('budget-limit').value);
    const period = document.getElementById('budget-period').value;
    
    if (name && category && limit > 0) {
        const budget = {
            id: Math.random(),
            name: name,
            category: category,
            limit: limit.toFixed(2),
            period: period,
            spent: (Math.random() * limit).toFixed(2)
        };
        
        let budgets = JSON.parse(localStorage.getItem('finpilot_budgets') || '[]');
        budgets.push(budget);
        localStorage.setItem('finpilot_budgets', JSON.stringify(budgets));
        
        document.getElementById('budget-form').reset();
        loadBudgets();
    }
}

function loadBudgets() {
    const budgets = JSON.parse(localStorage.getItem('finpilot_budgets') || '[]');
    const container = document.getElementById('budgets-list');
    
    if (budgets.length === 0) {
        container.innerHTML = '<p class="text-muted">No budgets created yet. Create one to track your spending!</p>';
        return;
    }
    
    container.innerHTML = budgets.map((budget, idx) => {
        const percentage = (budget.spent / budget.limit) * 100;
        const color = percentage > 80 ? '#EF4444' : percentage > 50 ? '#F59E0B' : '#10B981';
        
        return `
            <div class="budget-card">
                <h4>${budget.name}</h4>
                <p class="text-muted">${budget.category}</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${Math.min(100, percentage)}%; background-color: ${color};"></div>
                </div>
                <p>$${budget.spent} / $${budget.limit}</p>
                <button class="btn btn-danger" style="font-size: 0.8rem;" onclick="deleteBudget(${idx})">Delete</button>
            </div>
        `;
    }).join('');
}

function deleteBudget(index) {
    let budgets = JSON.parse(localStorage.getItem('finpilot_budgets') || '[]');
    budgets.splice(index, 1);
    localStorage.setItem('finpilot_budgets', JSON.stringify(budgets));
    loadBudgets();
}

/* ===== SAVINGS GOALS ===== */
function showSavingsForm() {
    const form = document.getElementById('savings-form');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

function addSavingsGoal(event) {
    event.preventDefault();
    
    const name = document.getElementById('savings-name').value;
    const target = parseFloat(document.getElementById('savings-target').value);
    const deadline = document.getElementById('savings-deadline').value;
    const description = document.getElementById('savings-description').value;
    
    if (name && target > 0) {
        const goal = {
            id: Math.random(),
            name: name,
            target: target.toFixed(2),
            current: (Math.random() * target).toFixed(2),
            deadline: deadline,
            description: description || 'No description'
        };
        
        let goals = JSON.parse(localStorage.getItem('finpilot_savings') || '[]');
        goals.push(goal);
        localStorage.setItem('finpilot_savings', JSON.stringify(goals));
        
        document.getElementById('savings-form').reset();
        loadSavingsGoals();
    }
}

function loadSavingsGoals() {
    const goals = JSON.parse(localStorage.getItem('finpilot_savings') || '[]');
    const container = document.getElementById('savings-list');
    
    if (goals.length === 0) {
        container.innerHTML = '<p class="text-muted">No savings goals yet. Create one to start saving!</p>';
        return;
    }
    
    container.innerHTML = goals.map((goal, idx) => {
        const percentage = (goal.current / goal.target) * 100;
        
        return `
            <div class="savings-card">
                <h4>${goal.name}</h4>
                <p class="text-muted">${goal.description}</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${Math.min(100, percentage)}%;"></div>
                </div>
                <p>$${goal.current} / $${goal.target} (${percentage.toFixed(0)}%)</p>
                ${goal.deadline ? `<p class="text-muted">Deadline: ${goal.deadline}</p>` : ''}
                <button class="btn btn-danger" style="font-size: 0.8rem;" onclick="deleteSavingsGoal(${idx})">Delete</button>
            </div>
        `;
    }).join('');
}

function deleteSavingsGoal(index) {
    let goals = JSON.parse(localStorage.getItem('finpilot_savings') || '[]');
    goals.splice(index, 1);
    localStorage.setItem('finpilot_savings', JSON.stringify(goals));
    loadSavingsGoals();
}

/* ===== AI ADVISOR ===== */
function loadAdvisorData() {
    // Spending Analysis
    const analysisHtml = `
        <p><strong>Last 30 Days Analysis:</strong></p>
        <ul style="margin-left: 1rem;">
            <li>Total Spent: $2,450.50</li>
            <li>Average Daily: $81.68</li>
            <li>Highest Category: Entertainment ($680)</li>
            <li>Lowest Category: Education ($45)</li>
        </ul>
    `;
    document.getElementById('spending-analysis').innerHTML = analysisHtml;
    
    // Spending Forecast
    const forecastHtml = `
        <p><strong>Month Projection:</strong></p>
        <ul style="margin-left: 1rem;">
            <li>Spent so far: $2,450.50</li>
            <li>Days elapsed: 15</li>
            <li>Projected monthly: $4,901.00</li>
            <li>Days remaining: 15</li>
        </ul>
    `;
    document.getElementById('spending-forecast').innerHTML = forecastHtml;
    
    // Recommendations
    const recommendations = [
        '💡 Entertainment spending is $200 over budget. Consider streaming service alternatives.',
        '✅ Food budget is on track - maintain current habits.',
        '📊 Transport spending increased 15% last month. Check for carpool opportunities.',
        '⚠️ Utility bills trending up. Review heating/cooling usage.',
        '💰 Save $50/week to reach your vacation fund goal by July 2026.'
    ];
    
    const recHtml = recommendations.map(rec => 
        `<div class="recommendation-item">${rec}</div>`
    ).join('');
    document.getElementById('ai-recommendations').innerHTML = recHtml;
}

/* ===== PROFILE ===== */
function loadProfile() {
    document.getElementById('profile-username').textContent = currentUser.username;
    document.getElementById('profile-email').textContent = currentUser.email;
    document.getElementById('profile-fullname').textContent = currentUser.full_name || 'Not set';
    document.getElementById('profile-joined').textContent = new Date().toLocaleDateString();
}

/* ===== FORM SUBMISSIONS ===== */
document.getElementById('login-form')?.addEventListener('submit', handleLogin);
document.getElementById('register-form')?.addEventListener('submit', handleRegister);
