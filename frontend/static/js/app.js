/* FinPilot Frontend Application Logic */

// Global state
let currentUser = null;
let currentUserId = null;

// API Configuration
const API_BASE_URL = "/api";

// App Initialization
document.addEventListener("DOMContentLoaded", () => {
  // Check if user is already logged in (from local storage)
  try {
    const savedUser = localStorage.getItem("finpilot_user");
    if (savedUser) {
      currentUser = JSON.parse(savedUser);
      currentUserId = currentUser ? currentUser.user_id : null;
      
      if (currentUserId) {
        fetchUserDetails();
        navigate("dashboard");
      } else {
        localStorage.removeItem("finpilot_user");
        navigate("landing");
      }
    } else {
      navigate("landing");
    }
  } catch (e) {
    console.error("Session restoration failed:", e);
    localStorage.removeItem("finpilot_user");
    navigate("landing");
  }
});

/* ===== UI UTILITIES ===== */
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  
  const icons = {
    success: "✅",
    error: "❌",
    warning: "⚠️",
    info: "ℹ️"
  };

  toast.innerHTML = `
    <span>${icons[type] || icons.info}</span>
    <div class="toast-content">${message}</div>
  `;

  container.appendChild(toast);

  // Auto-remove after 4s
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

function setLoading(show) {
  const overlay = document.getElementById("loading-overlay");
  if (overlay) {
    overlay.style.display = show ? "flex" : "none";
  }
}

/**
 * Standardized Fetch Wrapper with Hardening
 */
async function apiFetch(endpoint, options = {}) {
  const url = endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    headers: {
      "Content-Type": "application/json",
    },
  };

  const mergedOptions = { ...defaultOptions, ...options };
  
  try {
    const response = await fetch(url, mergedOptions);
    
    // Handle 204 No Content
    if (response.status === 204) return null;

    const contentType = response.headers.get("content-type");
    let data = {};
    
    if (contentType && contentType.includes("application/json")) {
      data = await response.json();
    } else {
      data = { detail: await response.text() };
    }

    if (!response.ok) {
      throw new Error(data.detail || `Request failed with status ${response.status}`);
    }
    return data;
  } catch (err) {
    console.error(`API Error [${endpoint}]:`, err.message);
    throw err;
  }
}

/* ===== NAVIGATION ===== */
// Navigation
function navigate(pageId) {
  if (pageId === "login") {
    pageId = "login-page";
  } else if (pageId === "register") {
    pageId = "register-page";
  } else if (pageId === "landing") {
    pageId = "landing-page";
  } else if (!pageId.endsWith("-page")) {
    pageId = `${pageId}-page`;
  }

  // Protection: If not logged in, only allow landing, login, and register
  const publicPages = ["landing-page", "login-page", "register-page"];
  if (!currentUserId && !publicPages.includes(pageId)) {
    pageId = "landing-page";
  }

  const pages = document.querySelectorAll(".page");
  pages.forEach((p) => p.classList.remove("active"));

  const targetPage = document.getElementById(pageId);
  if (targetPage) {
    targetPage.classList.add("active");
    window.scrollTo(0, 0);
  }

  // Toggle Nav visibility
  if (publicPages.includes(pageId)) {
    document.querySelector(".nav-menu").style.display = "none";
  } else {
    document.querySelector(".nav-menu").style.display = "flex";
  }

  // Load page-specific data if applicable
  if (pageId === "dashboard-page") loadDashboard();
  if (pageId === "expenses-page") loadExpenses();
  if (pageId === "budgets-page") loadBudgets();
  if (pageId === "advisor-page") loadAdvisorData();
  if (pageId === "profile-page") loadProfile();
}

function scrollToFeatures() {
  const features = document.getElementById("features");
  if (features) {
    features.scrollIntoView({ behavior: "smooth" });
  }
}

/* ===== AUTHENTICATION ===== */
async function handleLogin(event) {
  event.preventDefault();

  const username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;
  const submitBtn = event.target.querySelector('button[type="submit"]') || event.target;

  if (!username || !password) return;

  submitBtn.disabled = true;
  submitBtn.textContent = "Logging in...";

  setLoading(true);
  try {
    const data = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });

    currentUser = {
      user_id: data.user_id,
      username: data.username,
      email: data.email,
      full_name: data.username,
    };
    currentUserId = data.user_id;

    localStorage.setItem("finpilot_user", JSON.stringify(currentUser));
    fetchUserDetails();

    navigate("dashboard");
    showToast("Welcome back!", "success");

    // Clear form
    document.getElementById("login-username").value = "";
    document.getElementById("login-password").value = "";
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Login";
    setLoading(false);
  }
}

async function fetchUserDetails() {
  if (!currentUserId) return;
  try {
    const userData = await apiFetch(`/auth/me?user_id=${currentUserId}`);
    currentUser = userData;
    localStorage.setItem("finpilot_user", JSON.stringify(currentUser));
  } catch (e) {
    console.error("Failed to fetch user details", e);
  }
}

async function handleRegister(event) {
  event.preventDefault();

  const username = document.getElementById("register-username").value;
  const email = document.getElementById("register-email").value;
  const fullname = document.getElementById("register-fullname").value;
  const password = document.getElementById("register-password").value;
  const submitBtn = event.target.querySelector('button[type="submit"]') || event.target;

  if (!username || !email || !password) return;

  submitBtn.disabled = true;
  submitBtn.textContent = "Creating Account...";

  try {
    await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        username,
        email,
        password,
        full_name: fullname,
      }),
    });

    showToast("Registration successful! Please login.", "success");
    navigate("login");

    // Clear form
    document.getElementById("register-username").value = "";
    document.getElementById("register-email").value = "";
    document.getElementById("register-fullname").value = "";
    document.getElementById("register-password").value = "";
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Register";
    setLoading(false);
  }
}

function handleLogout() {
  currentUser = null;
  currentUserId = null;
  localStorage.removeItem("finpilot_user");
  navigate("landing");
}

/* ===== DASHBOARD ===== */
async function loadDashboard() {
  if (!currentUserId) return;

  // Optional: Add a subtle loading state to cards
  const summaryCards = document.querySelectorAll('.dashboard-grid .card .amount');
  summaryCards.forEach(card => card.classList.add('loading-pulse'));

  try {
    const data = await apiFetch(`/advisor/dashboard?user_id=${currentUserId}`);
    
    // Update Welcome Message
    const welcomeMsg = document.getElementById("welcome-message");
    welcomeMsg.textContent = `Welcome back, ${data.user_name}!`;

    // Update Spending Cards
    const summary = data.financial_summary;
    
    const monthlySpendingEl = document.getElementById("monthly-spending");
    if (monthlySpendingEl) {
      monthlySpendingEl.textContent = `₹${(summary.total_spent_month || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
    }

    const overallSavingsEl = document.getElementById("overall-savings");
    if (overallSavingsEl) {
      overallSavingsEl.textContent = `₹${(summary.overall_savings || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
      overallSavingsEl.style.color = (summary.overall_savings || 0) >= 0 ? "var(--success)" : "var(--danger)";
    }

    // Render History
    const historyList = document.getElementById("savings-history-list");
    if (summary.savings_history && summary.savings_history.length > 0) {
      historyList.innerHTML = summary.savings_history
        .map(m => `
          <div class="history-item" style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(0,0,0,0.05); padding: 0.75rem 0; font-size: 0.95rem;">
              <span class="text-muted">${m.month}</span>
              <span class="font-mono" style="color: ${m.savings >= 0 ? "var(--success)" : "var(--danger)"}; font-weight: 600;">
                  ₹${m.savings.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </span>
          </div>
        `).join("");
    } else {
      historyList.innerHTML = '<p class="text-muted">No fiscal history available yet.</p>';
    }

    // Reconcile Net Savings
    const netSavingsEl = document.getElementById("net-savings");
    if (netSavingsEl) {
      const netVal = summary.net_savings || 0;
      netSavingsEl.textContent = `₹${netVal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
      netSavingsEl.style.color = netVal >= 0 ? "var(--success)" : "var(--danger)";
    }

    const globalLimitDisplay = document.getElementById("global-limit-display");
    if (globalLimitDisplay) {
      globalLimitDisplay.textContent = `Target: ₹${(summary.global_budget_limit || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
    }

    const dailySpendingEl = document.getElementById("daily-spending");
    if (dailySpendingEl) {
      dailySpendingEl.textContent = `₹${(data.analysis.average_daily_spend || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
    }

    const list = document.getElementById("recommendations-list");
    if (data.recommendations && data.recommendations.length > 0) {
      list.innerHTML = data.recommendations
        .map(rec => `<div class="recommendation-item animate-in" style="padding: 12px; border-left: 3px solid var(--primary); background: var(--primary-soft); margin-bottom: 8px; border-radius: 4px;">${rec}</div>`)
        .join("");
    } else {
      list.innerHTML = '<p class="text-muted">AI is analyzing your patterns... Add more data for insights.</p>';
    }
  } catch (err) {
    console.error("Error loading dashboard:", err);
    showToast("Precision analytics temporarily unavailable", "error");
  } finally {
    summaryCards.forEach(card => card.classList.remove('loading-pulse'));
  }
}

/* ===== EXPENSES ===== */
function showExpenseForm() {
  const form = document.getElementById("expense-form");
  form.style.display = form.style.display === "none" ? "block" : "none";
}

async function addExpense(event) {
  event.preventDefault();
  if (!currentUserId) return;

  const amount = parseFloat(document.getElementById("expense-amount").value);
  const category = document.getElementById("expense-category").value;
  const description = document.getElementById("expense-description").value;
  const dateStr = document.getElementById("expense-date").value || new Date().toISOString().split("T")[0];
  const payee = document.getElementById("expense-payee").value || null;
  const method = document.getElementById("expense-method").value || "Cash";
  const ref = document.getElementById("expense-ref").value || null;

  const submitBtn = event.target.querySelector('button[type="submit"]');

  if (!amount || !category) {
    showToast("Please fill in Amount and Category.", "warning");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = "Posting...";

  setLoading(true);
  try {
    const newExp = await apiFetch(`/expenses/?user_id=${currentUserId}`, {
      method: "POST",
      body: JSON.stringify({
        amount,
        category,
        description: description || null,
        date: new Date(dateStr).toISOString(),
        payment_method: method,
        payee,
        reference_no: ref,
        status: "Cleared",
      }),
    });

    showToast("Transaction Posted Successfully", "success");
    if (newExp.alerts && newExp.alerts.length > 0) {
      newExp.alerts.forEach(alert => showToast(alert, "warning"));
    }

    document.getElementById("expense-form").reset();
    loadExpenses();
    loadDashboard();
    showExpenseForm();
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Post Entry";
    setLoading(false);
  }
}

async function loadExpenses() {
  if (!currentUserId) return;

  const tbody = document.getElementById("expenses-list");
  tbody.innerHTML = '<tr><td colspan="9" class="text-center">Loading Ledger...</td></tr>';

  try {
    const expenses = await apiFetch(`/expenses/?user_id=${currentUserId}&limit=50`);

    if (expenses.length === 0) {
      tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">No journal entries found.</td></tr>';
      document.getElementById("ledger-total").textContent = "₹0.00";
      return;
    }

    expenses.sort((a, b) => new Date(b.date) - new Date(a.date));

    const categoryMap = {
      food: "Meals & Ent.",
      transport: "Transportation",
      utilities: "Utilities",
      entertainment: "Recreation",
      health: "Medical",
      shopping: "Supplies",
      education: "Prof. Dev.",
      other: "Misc.",
    };

    let totalDebit = 0;
    tbody.innerHTML = expenses.map(exp => {
      const date = new Date(exp.date).toLocaleDateString();
      totalDebit += exp.amount;
      const statusClass = exp.status === "Pending" ? "status-pending" : "status-cleared";

      return `
        <tr>
            <td>${date}</td>
            <td>${exp.reference_no || "-"}</td>
            <td>${exp.payee || "-"}</td>
            <td>${categoryMap[exp.category] || exp.category}</td>
            <td>${exp.description || "-"}</td>
            <td>${exp.payment_method || "Cash"}</td>
            <td><span class="status-badge ${statusClass}">${exp.status || "Cleared"}</span></td>
            <td class="text-right font-mono">₹${exp.amount.toFixed(2)}</td>
            <td class="text-center">
                <button class="btn btn-danger" onclick="deleteExpense(${exp.id})">×</button>
            </td>
        </tr>
      `;
    }).join("");

    document.getElementById("ledger-total").textContent = `₹${totalDebit.toFixed(2)}`;
  } catch (err) {
    showToast("Failed to load ledger", "error");
    tbody.innerHTML = '<tr><td colspan="9" class="text-danger">Failed to load ledger</td></tr>';
  }
}

async function deleteExpense(expenseId) {
  if (!currentUserId || !confirm("Are you sure you want to delete this expense?")) return;

  setLoading(true);
  try {
    await apiFetch(`/expenses/${expenseId}?user_id=${currentUserId}`, {
      method: "DELETE",
    });

    showToast("Entry Deleted", "success");
    loadExpenses();
    loadDashboard();
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    setLoading(false);
  }
}

/* ===== BUDGETS ===== */
function showBudgetForm() {
  const form = document.getElementById("budget-form");
  form.style.display = form.style.display === "none" ? "block" : "none";
}

async function addBudget(event) {
  event.preventDefault();
  if (!currentUserId) return;

  const name = document.getElementById("budget-name").value;
  const category = document.getElementById("budget-category").value;
  const limit = parseFloat(document.getElementById("budget-limit").value);
  const period = document.getElementById("budget-period").value;
  const rollover = document.getElementById("budget-rollover")?.checked || false;

  const submitBtn = event.target.querySelector('button[type="submit"]');

  if (!name || !category || !limit) return;

  submitBtn.disabled = true;
  submitBtn.textContent = "Allocating...";

  setLoading(true);
  try {
    await apiFetch(`/budgets/?user_id=${currentUserId}`, {
      method: "POST",
      body: JSON.stringify({
        name,
        category,
        amount: limit,
        period,
        is_rollover: rollover,
      }),
    });

    showToast("Budget Allocated", "success");
    document.getElementById("budget-form").reset();
    loadBudgets();
    loadDashboard();
    showBudgetForm();
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Create Allocation";
    setLoading(false);
  }
}

async function loadBudgets() {
  if (!currentUserId) return;

  const container = document.getElementById("budgets-list");
  container.innerHTML = '<tr><td colspan="8" class="text-center">Calculating variance...</td></tr>';

  try {
    const budgets = await apiFetch(`/budgets/?user_id=${currentUserId}`);

    if (budgets.length === 0) {
      container.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No active budget allocations.</td></tr>';
      return;
    }

    let totalAlloc = 0;
    let totalActual = 0;
    let totalVariance = 0;

    const categoryMap = {
      food: "Meals & Ent.",
      transport: "Transportation",
      utilities: "Utilities",
      entertainment: "Recreation",
      health: "Medical",
      shopping: "Supplies",
      education: "Prof. Dev.",
      other: "Misc.",
    };

    container.innerHTML = budgets.map(budget => {
      const limit = budget.amount;
      const spent = budget.spent || 0;
      const variance = limit - spent;
      const variancePct = limit > 0 ? (spent / limit) * 100 : 0;

      totalAlloc += limit;
      totalActual += spent;
      totalVariance += variance;

      let statusBadge = "";
      if (variance < 0) statusBadge = '<span class="status-badge status-over">Over Budget</span>';
      else if (variancePct > 90) statusBadge = '<span class="status-badge status-pending">Critical</span>';
      else statusBadge = '<span class="status-badge status-under">Under Budget</span>';

      return `
        <tr>
            <td style="font-weight: 500;">${budget.name} <span class="text-muted" style="font-size: 0.8em;">(${categoryMap[budget.category] || budget.category})</span></td>
            <td>${budget.period}</td>
            <td class="text-right font-mono">₹${limit.toFixed(2)}</td>
            <td class="text-right font-mono">₹${spent.toFixed(2)}</td>
            <td class="text-right font-mono ${variance < 0 ? "negative-val" : "positive-val"}">₹${variance.toFixed(2)}</td>
            <td class="text-center font-mono">${variancePct.toFixed(1)}%</td>
            <td class="text-center">${statusBadge}</td>
            <td class="text-center">
                <button class="btn btn-danger" onclick="deleteBudget(${budget.id})">×</button>
            </td>
        </tr>
      `;
    }).join("");

    document.getElementById("total-allocated").textContent = `₹${totalAlloc.toFixed(2)}`;
    document.getElementById("total-actual").textContent = `₹${totalActual.toFixed(2)}`;
    document.getElementById("total-variance").textContent = `₹${totalVariance.toFixed(2)}`;
    document.getElementById("total-variance").className = `text-right font-mono ${totalVariance < 0 ? "negative-val" : "positive-val"}`;
  } catch (err) {
    showToast("Failed to load budget report", "error");
  }
}

async function updateGlobalBudget() {
  if (!currentUserId) return;

  const limit = parseFloat(document.getElementById("global-budget-input").value);
  if (isNaN(limit) || limit < 0) {
    showToast("Please enter a valid amount", "warning");
    return;
  }

  setLoading(true);
  try {
    await apiFetch(`/budgets/users/${currentUserId}/global`, {
      method: "PUT",
      body: JSON.stringify({ limit }),
    });

    showToast("Global budget updated!", "success");
    loadDashboard();
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    setLoading(false);
  }
}

async function deleteBudget(budgetId) {
  if (!currentUserId || !confirm("Delete this budget?")) return;

  setLoading(true);
  try {
    await apiFetch(`/budgets/${budgetId}?user_id=${currentUserId}`, {
      method: "DELETE",
    });

    showToast("Allocation Removed", "success");
    loadBudgets();
    loadDashboard();
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    setLoading(false);
  }
}

/* ===== AI ADVISOR ===== */
async function loadAdvisorData() {
  if (!currentUserId) return;

  try {
    const data = await apiFetch(`/advisor/dashboard?user_id=${currentUserId}`);
    const analysis = data.analysis;
    const forecast = data.forecast;

    let highest = { name: "None", amount: 0 };
    let lowest = { name: "None", amount: Infinity };
    const breakdown = analysis.category_breakdown || analysis.spending_by_category;

    if (breakdown) {
      for (const [cat, data] of Object.entries(breakdown)) {
        const amt = typeof data === 'object' ? data.total : data;
        if (amt > highest.amount) highest = { name: cat, amount: amt };
        if (amt < lowest.amount) lowest = { name: cat, amount: amt };
      }
    }
    if (lowest.amount === Infinity) lowest.amount = 0;

    const analysisHtml = `
      <p><strong>Last 30 Days Analysis:</strong></p>
      <ul style="margin-left: 1rem;">
          <li>Total Spent: ₹${(analysis.total_spent || 0).toFixed(2)}</li>
          <li>Average Daily: ₹${(analysis.average_daily_spend || 0).toFixed(2)}</li>
          <li>Highest Category: ${highest.name} (₹${highest.amount.toFixed(2)})</li>
          <li>Lowest Category: ${lowest.name} (₹${lowest.amount.toFixed(2)})</li>
      </ul>
    `;
    document.getElementById("spending-analysis").innerHTML = analysisHtml;

    const forecastHtml = `
      <p><strong>Month Projection:</strong></p>
      <ul style="margin-left: 1rem;">
          <li>Projected Total: ₹${(forecast.predicted_monthly_spending || 0).toFixed(2)}</li>
          <li>Likely to exceed budget: ${forecast.is_likely_to_exceed_budget ? "Yes ⚠️" : "No ✅"}</li>
      </ul>
    `;
    document.getElementById("spending-forecast").innerHTML = forecastHtml;

    const list = document.getElementById("ai-recommendations");
    if (data.recommendations && data.recommendations.length > 0) {
      list.innerHTML = data.recommendations
        .map(rec => `<div class="recommendation-item">${rec}</div>`)
        .join("");
    } else {
      list.innerHTML = '<p class="text-muted">No recommendations generated yet.</p>';
    }
  } catch (err) {
    showToast("Failed to load advisor data", "error");
    document.getElementById("spending-analysis").innerHTML = '<p class="text-danger">Failed to load analysis</p>';
  }
}

/* ===== PROFILE ===== */
function loadProfile() {
  if (!currentUser) return;
  document.getElementById("profile-username").textContent = currentUser.username;
  document.getElementById("profile-email").textContent = currentUser.email;
  document.getElementById("profile-fullname").textContent = currentUser.full_name || "Not set";
  document.getElementById("profile-joined").textContent = new Date().toLocaleDateString();
}

/* ===== EVENT LISTENERS ===== */
document.addEventListener("DOMContentLoaded", () => {
  const forms = {
    "login-form": handleLogin,
    "register-form": handleRegister,
    "expense-form": addExpense,
    "budget-form": addBudget,
  };

  for (const [id, handler] of Object.entries(forms)) {
    const form = document.getElementById(id);
    if (form) form.addEventListener("submit", handler);
  }

  // Category Limit Intelligence
  const catSelect = document.getElementById("expense-category");
  if (catSelect) {
    catSelect.addEventListener("change", async (e) => {
      const category = e.target.value;
      const infoBox = document.getElementById("category-limit-info");
      if (!category || !currentUserId || !infoBox) return;

      try {
        const budgets = await apiFetch(`/budgets/?user_id=${currentUserId}`);
        const budget = budgets.find(b => b.category.toLowerCase() === category.toLowerCase());

        if (budget) {
          const limitMonthly = budget.amount;
          document.getElementById("limit-category-name").textContent = category;
          document.getElementById("limit-monthly").textContent = `₹${limitMonthly.toFixed(2)}`;
          document.getElementById("limit-weekly").textContent = `₹${(limitMonthly / 4).toFixed(2)}`;
          document.getElementById("limit-daily").textContent = `₹${(limitMonthly / 30).toFixed(2)}`;
          infoBox.style.display = "block";
        } else {
          infoBox.style.display = "none";
        }
      } catch (err) {
        console.error("Error fetching category budget", err);
      }
    });
  }
});
