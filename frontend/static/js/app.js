/* FinPilot Frontend Application Logic */

// Global state
let currentUser = null;
let currentUserId = null;

// API Configuration
const API_BASE_URL = '/api';

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    try {
        const savedUser = localStorage.getItem('finpilot_user');
        if (savedUser) {
            currentUser = JSON.parse(savedUser);
            if (currentUser && currentUser.user_id) {
                currentUserId = currentUser.user_id;
                showPage('dashboard-page');
                loadDashboard();
            } else {
                throw new Error("Invalid user data");
            }
        } else {
            showPage('auth-page');
        }
    } catch (e) {
        console.error("Initialization error:", e);
        localStorage.removeItem('finpilot_user');
        showPage('auth-page');
    }
});

/* ===== NAVIGATION ===== */
function navigate(page) {
    if (!currentUser) {
        showPage('auth-page');
        return;
    }
    showPage(`${page}-page`);
    
    // Load page-specific data
    if (page === 'dashboard') loadDashboard();
    if (page === 'expenses') loadExpenses();
    if (page === 'budgets') loadBudgets();
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

async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const submitBtn = event.target.querySelector('button[type="submit"]') || event.target;
    
    if (!username || !password) return;
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }
        
        const data = await response.json();
        
        currentUser = {
            user_id: data.user_id,
            username: data.username,
            email: data.email,
            full_name: data.username // Backend doesn't return full_name in login response yet, using username as fallback
        };
        currentUserId = data.user_id;
        
        localStorage.setItem('finpilot_user', JSON.stringify(currentUser));
        
        // Fetch full user details to get full name
        fetchUserDetails();
        
        showPage('dashboard-page');
        loadDashboard();
        
        // Clear form
        document.getElementById('login-username').value = '';
        document.getElementById('login-password').value = '';
        
    } catch (err) {
        alert(err.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
    }
}

async function fetchUserDetails() {
    if (!currentUserId) return;
    try {
        const res = await fetch(`${API_BASE_URL}/auth/me?user_id=${currentUserId}`);
        if (res.ok) {
            const userData = await res.json();
            currentUser = userData;
            localStorage.setItem('finpilot_user', JSON.stringify(currentUser));
        }
    } catch (e) {
        console.error("Failed to fetch user details", e);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const fullname = document.getElementById('register-fullname').value;
    const password = document.getElementById('register-password').value;
    const submitBtn = event.target.querySelector('button[type="submit"]') || event.target;
    
    if (!username || !email || !password) return;

    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating Account...';

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                username, 
                email, 
                password,
                full_name: fullname
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }
        
        const newUser = await response.json();
        
        alert('Registration successful! Please login.');
        switchAuthTab('login');
        
        // Clear form
        document.getElementById('register-username').value = '';
        document.getElementById('register-email').value = '';
        document.getElementById('register-fullname').value = '';
        document.getElementById('register-password').value = '';
        
    } catch (err) {
        alert(err.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register';
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
async function loadDashboard() {
    if (!currentUserId) return;
    
    try {
        // Fetch Dashboard Summary (Spending & Advisor)
        const dashboardRes = await fetch(`${API_BASE_URL}/advisor/dashboard?user_id=${currentUserId}`);
        if (dashboardRes.ok) {
            const data = await dashboardRes.json();
            
            // Update Welcome Message
            const welcomeMsg = document.getElementById('welcome-message');
            welcomeMsg.textContent = `Welcome back, ${data.user_name}!`;
            
            // Update Spending Cards
            const summary = data.financial_summary;
            
            document.getElementById('monthly-spending').textContent = `₹${(summary.total_spent_month || 0).toFixed(2)}`;
            
            // New Global Budget Metrics & History
            // summary already declared above
            
            document.getElementById('overall-savings').textContent = `₹${(summary.overall_savings || 0).toFixed(2)}`;
            document.getElementById('overall-savings').style.color = (summary.overall_savings || 0) >= 0 ? 'var(--secondary-color)' : '#EF4444';
            
            // Render History
            const historyList = document.getElementById('savings-history-list');
            if (summary.savings_history && summary.savings_history.length > 0) {
                historyList.innerHTML = summary.savings_history.map(m => `
                    <div class="history-item" style="display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding: 0.5rem 0; font-size: 0.9em;">
                        <span>${m.month}</span>
                        <span style="color: ${m.savings >= 0 ? 'green' : 'red'}; font-weight: 500;">
                            ₹${m.savings.toFixed(2)}
                        </span>
                    </div>
                `).join('');
            } else {
                historyList.innerHTML = '<p class="text-muted">No history available yet.</p>';
            }
            
            // Reconcile Net Savings
            const netSavingsEl = document.getElementById('net-savings');
            if (netSavingsEl) {
                netSavingsEl.textContent = `₹${(summary.net_savings || 0).toFixed(2)}`;
                netSavingsEl.style.color = (summary.net_savings || 0) >= 0 ? 'var(--success-color)' : 'var(--danger-color)';
            }

            const globalLimitDisplay = document.getElementById('global-limit-display');
            if (globalLimitDisplay) {
                globalLimitDisplay.textContent = `Target: ₹${(summary.global_budget_limit || 0).toFixed(2)}`;
            }
            
            // Calculate avg daily for display info only if needed, or stick to backend report
            document.getElementById('daily-spending').textContent = `₹${(data.analysis.average_daily_spend || 0).toFixed(2)}`;
            const list = document.getElementById('recommendations-list');
            if (data.recommendations && data.recommendations.length > 0) {
                list.innerHTML = data.recommendations.map(rec => 
                    `<div class="recommendation-item">${rec}</div>`
                ).join('');
            } else {
                list.innerHTML = '<p class="text-muted">No recommendations yet. Start tracking expenses!</p>';
            }
        }
        
    } catch (error) {
        console.error("Error loading dashboard:", error);
    }
}

// loadRecommendations is now handled inside loadDashboard or Advisor
function loadRecommendations() {
    // Deprecated, handled in loadDashboard
}

/* ===== EXPENSES ===== */
function showExpenseForm() {
    const form = document.getElementById('expense-form');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

async function addExpense(event) {
    event.preventDefault();
    
    if (!currentUserId) return;
    
    const amount = parseFloat(document.getElementById('expense-amount').value);
    const category = document.getElementById('expense-category').value;
    const description = document.getElementById('expense-description').value;
    
    // Professional Fields
    const date = document.getElementById('expense-date').value;
    const payee = document.getElementById('expense-payee').value;
    const method = document.getElementById('expense-method').value;
    const ref = document.getElementById('expense-ref').value;
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    
    if (!amount || !category || !date) {
        alert("Please fill in Date, Amount, and Category.");
        return;
    }
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Posting...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/expenses/?user_id=${currentUserId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                amount: amount,
                category: category,
                description: description || null,
                date: new Date(date).toISOString(),
                payment_method: method,
                payee: payee || null,
                reference_no: ref || null,
                status: "Cleared" // Default for now, could add UI selector
            })
        });
        
        if (response.ok) {
            const newExp = await response.json();
            
            // Check for Smart Alerts
            if (newExp.alerts && newExp.alerts.length > 0) {
                alert(`Entry Posted.\n\n⚠️ COMPLIANCE WARNING:\n${newExp.alerts.join('\n')}`);
            }

            document.getElementById('expense-form').reset();
            // document.getElementById('category-limit-info').style.display = 'none'; // Element might not exist in new UI
            loadExpenses();
            loadDashboard(); // Update dashboard stats
            // loadAdvisorData(); // Update advisor
            showExpenseForm(); // Hide form
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to post entry');
        }
    } catch (e) {
        console.error("Error adding expense:", e);
        alert("Failed to post entry");
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Post Entry';
    }
}

async function loadExpenses() {
    if (!currentUserId) return;
    
    const tbody = document.getElementById('expenses-list');
    tbody.innerHTML = '<tr><td colspan="9" class="text-center">Loading records...</td></tr>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/expenses/?user_id=${currentUserId}&limit=50`); // Fetch last 50
        if (!response.ok) throw new Error("Failed to fetch expenses");
        
        let expenses = await response.json();
        
        if (expenses.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">No journal entries found.</td></tr>';
            document.getElementById('ledger-total').textContent = '₹0.00';
            return;
        }
        
        // Sort by date desc
        expenses.sort((a, b) => new Date(b.date) - new Date(a.date));
        
        const categoryMap = {
            'food': 'Meals & Ent.',
            'transport': 'Transportation',
            'utilities': 'Utilities',
            'entertainment': 'Recreation',
            'health': 'Medical',
            'shopping': 'Supplies',
            'education': 'Prof. Dev.',
            'other': 'Misc.'
        };

        let totalDebit = 0;
        
        tbody.innerHTML = expenses.map(exp => {
            const date = new Date(exp.date).toLocaleDateString();
            totalDebit += exp.amount;
            
            const statusClass = exp.status === 'Pending' ? 'status-pending' : 'status-cleared';
            
            return `
            <tr>
                <td>${date}</td>
                <td>${exp.reference_no || '-'}</td>
                <td>${exp.payee || '-'}</td>
                <td>${categoryMap[exp.category] || exp.category}</td>
                <td>${exp.description || '-'}</td>
                <td>${exp.payment_method || 'Cash'}</td>
                <td><span class="status-badge ${statusClass}">${exp.status || 'Cleared'}</span></td>
                <td class="text-right font-mono">₹${exp.amount.toFixed(2)}</td>
                <td class="text-center">
                    <button class="btn btn-danger" onclick="deleteExpense(${exp.id})">×</button>
                </td>
            </tr>
            `;
        }).join('');
        
        document.getElementById('ledger-total').textContent = `₹${totalDebit.toFixed(2)}`;
        
    } catch (e) {
        console.error("Error loading expenses:", e);
        tbody.innerHTML = '<tr><td colspan="9" class="text-danger">Failed to load ledger</td></tr>';
    }
}

async function deleteExpense(expenseId) {
    if (!currentUserId || !confirm("Are you sure you want to delete this expense?")) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/expenses/${expenseId}?user_id=${currentUserId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadExpenses();
            loadDashboard();
        } else {
            alert("Failed to delete expense");
        }
    } catch (e) {
        console.error("Error deleting expense:", e);
    }
}

/* ===== BUDGETS ===== */
function showBudgetForm() {
    const form = document.getElementById('budget-form');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

async function addBudget(event) {
    event.preventDefault();
    
    if (!currentUserId) return;
    
    const name = document.getElementById('budget-name').value;
    const category = document.getElementById('budget-category').value;
    const limit = parseFloat(document.getElementById('budget-limit').value);
    const period = document.getElementById('budget-period').value;
    const rolloverEl = document.getElementById('budget-rollover');
    const rollover = rolloverEl ? rolloverEl.checked : false;
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    
    if (!name || !category || !limit) return;
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Allocating...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/budgets/?user_id=${currentUserId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                category: category,
                amount: limit,
                period: period,
                is_rollover: rollover
            })
        });
        
        if (response.ok) {
            document.getElementById('budget-form').reset();
            loadBudgets();
            loadDashboard();
            showBudgetForm();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to allocate budget');
        }
    } catch (e) {
        console.error("Error adding budget:", e);
        alert("Failed to allocate budget");
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Allocation';
    }
}

async function loadBudgets() {
    if (!currentUserId) return;
    
    const container = document.getElementById('budgets-list');
    container.innerHTML = '<tr><td colspan="8" class="text-center">Calculating variance...</td></tr>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/budgets/?user_id=${currentUserId}`);
        if (!response.ok) throw new Error("Failed to fetch budgets");
        
        const budgets = await response.json();
        
        if (budgets.length === 0) {
            container.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No active budget allocations.</td></tr>';
            return;
        }
        
        let totalAlloc = 0;
        let totalActual = 0;
        let totalVariance = 0;

        container.innerHTML = budgets.map(budget => {
            const limit = budget.amount; 
            const spent = budget.spent || 0;
            const variance = limit - spent;
            const variancePct = limit > 0 ? (spent / limit) * 100 : 0;
            
            totalAlloc += limit;
            totalActual += spent;
            totalVariance += variance;
            
            let statusBadge = '';
            if (variance < 0) statusBadge = '<span class="status-badge status-over">Over Budget</span>';
            else if (variancePct > 90) statusBadge = '<span class="status-badge status-pending">Critical</span>';
            else statusBadge = '<span class="status-badge status-under">Under Budget</span>';

            const categoryMap = {
                'food': 'Meals & Ent.',
                'transport': 'Transportation',
                'utilities': 'Utilities',
                'entertainment': 'Recreation',
                'health': 'Medical',
                'shopping': 'Supplies',
                'education': 'Prof. Dev.',
                'other': 'Misc.'
            };

            return `
            <tr>
                <td style="font-weight: 500;">${budget.name} <span class="text-muted" style="font-size: 0.8em;">(${categoryMap[budget.category] || budget.category})</span></td>
                <td>${budget.period}</td>
                <td class="text-right font-mono">₹${limit.toFixed(2)}</td>
                <td class="text-right font-mono">₹${spent.toFixed(2)}</td>
                <td class="text-right font-mono ${variance < 0 ? 'negative-val' : 'positive-val'}">₹${variance.toFixed(2)}</td>
                <td class="text-center font-mono">${variancePct.toFixed(1)}%</td>
                <td class="text-center">${statusBadge}</td>
                <td class="text-center">
                    <button class="btn btn-danger" onclick="deleteBudget(${budget.id})">×</button>
                </td>
            </tr>
            `;
        }).join('');
        
        // Update Totals Footer
        document.getElementById('total-allocated').textContent = `₹${totalAlloc.toFixed(2)}`;
        document.getElementById('total-actual').textContent = `₹${totalActual.toFixed(2)}`;
        document.getElementById('total-variance').textContent = `₹${totalVariance.toFixed(2)}`;
        document.getElementById('total-variance').className = `text-right font-mono ${totalVariance < 0 ? 'negative-val' : 'positive-val'}`;
        
    } catch (e) {
        console.error("Error loading budgets:", e);
        container.innerHTML = '<tr><td colspan="8" class="text-danger">Failed to load variance report</td></tr>';
    }
}

async function updateGlobalBudget() {
    if (!currentUserId) return;
    
    const limit = parseFloat(document.getElementById('global-budget-input').value);
    if (isNaN(limit) || limit < 0) {
        alert("Please enter a valid amount");
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users/${currentUserId}/budget`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ limit })
        });

        if (response.ok) {
            alert("Global budget updated!");
            loadDashboard();
        } else {
            alert("Failed to update global budget");
        }
    } catch (e) {
        console.error("Error updating global budget:", e);
        alert("Failed to update global budget");
    }
}

async function deleteBudget(budgetId) {
    if (!currentUserId || !confirm("Delete this budget?")) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/budgets/${budgetId}?user_id=${currentUserId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadBudgets();
            loadDashboard();
        } else {
            alert("Failed to delete budget");
        }
    } catch (e) {
        console.error("Error deleting budget:", e);
    }
}

/* ===== SAVINGS GOALS REMOVED ===== */

/* ===== AI ADVISOR ===== */
async function loadAdvisorData() {
    if (!currentUserId) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/advisor/dashboard?user_id=${currentUserId}`);
        if (!response.ok) throw new Error("Failed to fetch advisor data");
        
        const data = await response.json();
        const analysis = data.analysis;
        const forecast = data.forecast;
        
        // Find highest/lowest category
        let highest = { name: 'None', amount: 0 };
        let lowest = { name: 'None', amount: Infinity };
        
        if (analysis.spending_by_category) {
            for (const [cat, amt] of Object.entries(analysis.spending_by_category)) {
                if (amt > highest.amount) highest = { name: cat, amount: amt };
                if (amt < lowest.amount) lowest = { name: cat, amount: amt };
            }
        }
        if (lowest.amount === Infinity) lowest.amount = 0;
        
        // Spending Analysis
        const analysisHtml = `
            <p><strong>Last 30 Days Analysis:</strong></p>
            <ul style="margin-left: 1rem;">
                <li>Total Spent: ₹${(analysis.total_spent || 0).toFixed(2)}</li>
                <li>Average Daily: ₹${(analysis.average_daily_spend || 0).toFixed(2)}</li>
                <li>Highest Category: ${highest.name} (₹${highest.amount.toFixed(2)})</li>
                <li>Lowest Category: ${lowest.name} (₹${lowest.amount.toFixed(2)})</li>
            </ul>
        `;
        document.getElementById('spending-analysis').innerHTML = analysisHtml;
        
        // Spending Forecast
        const forecastHtml = `
            <p><strong>Month Projection:</strong></p>
            <ul style="margin-left: 1rem;">
                <li>Projected Total: ₹${(forecast.predicted_monthly_spending || 0).toFixed(2)}</li>
                <li>Likely to exceed budget: ${forecast.is_likely_to_exceed_budget ? 'Yes ⚠️' : 'No ✅'}</li>
            </ul>
        `;
        document.getElementById('spending-forecast').innerHTML = forecastHtml;
        
        // Recommendations
        const list = document.getElementById('ai-recommendations');
        if (data.recommendations && data.recommendations.length > 0) {
            list.innerHTML = data.recommendations.map(rec => 
                `<div class="recommendation-item">${rec}</div>`
            ).join('');
        } else {
            list.innerHTML = '<p class="text-muted">No recommendations generated yet.</p>';
        }
        
    } catch (e) {
        console.error("Error loading advisor data:", e);
        document.getElementById('spending-analysis').innerHTML = '<p class="text-danger">Failed to load analysis</p>';
    }
}

/* ===== PROFILE ===== */
function loadProfile() {
    document.getElementById('profile-username').textContent = currentUser.username;
    document.getElementById('profile-email').textContent = currentUser.email;
    document.getElementById('profile-fullname').textContent = currentUser.full_name || 'Not set';
    document.getElementById('profile-joined').textContent = new Date().toLocaleDateString();
}

/* ===== FORM SUBMISSIONS ===== */
// Use event delegation or check existence to avoid null errors on partial pages
document.addEventListener('DOMContentLoaded', () => {
    const forms = {
        'login-form': handleLogin,
        'register-form': handleRegister,
        'expense-form': addExpense,
        'budget-form': addBudget
    };

// Logic for Limit Display
document.getElementById('expense-category').addEventListener('change', async (e) => {
    const category = e.target.value;
    const infoBox = document.getElementById('category-limit-info');
    
    if (!category || !currentUserId) {
        infoBox.style.display = 'none';
        return;
    }
    
    // Fetch budget for this category 
    // Optimization: In real app, cache this. For now, fetch.
    try {
        const response = await fetch(`${API_BASE_URL}/budgets/?user_id=${currentUserId}`);
        if (response.ok) {
            const budgets = await response.json();
            const budget = budgets.find(b => b.category === category || b.category.toLowerCase() === category.toLowerCase());
            
            if (budget) {
                const limitMonthly = budget.amount; // Monthly Limit
                const limitDaily = limitMonthly / 30;
                const limitWeekly = limitMonthly / 4;
                
                document.getElementById('limit-category-name').textContent = category;
                document.getElementById('limit-monthly').textContent = `₹${limitMonthly.toFixed(2)}`;
                document.getElementById('limit-weekly').textContent = `₹${limitWeekly.toFixed(2)}`;
                document.getElementById('limit-daily').textContent = `₹${limitDaily.toFixed(2)}`;
                
                infoBox.style.display = 'block';
            } else {
                infoBox.style.display = 'none'; // No budget, no intelligence
            }
        }
    } catch(err) {
        console.error("Error fetching budget for limits", err);
    }
});
    
    for (const [id, handler] of Object.entries(forms)) {
        const form = document.getElementById(id);
        if (form) {
            form.addEventListener('submit', handler);
        }
    }
});
