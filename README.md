# 💰 FinPilot - AI-Powered Financial Suite

FinPilot is a professional-grade personal finance management platform. It combines traditional accounting principles with modern AI-driven insights and blockchain-backed transaction integrity.

## 📋 Core Capabilities

- **Fiscal Budgeting** – Dual-layer budgeting with Global Monthly Caps and granular Category Allocations.
- **Transaction Ledger** – Professional accounting interface for tracking expenses with automated variance analysis.
- **Blockchain Integrity** – Every transaction is hashed using SHA-256 and linked to prevent tampering and ensure auditability.
- **AI Audit & Advisor** – Intelligent analysis of spending patterns, daily/weekly/monthly limit warnings, and fiscal year compliance.
- **Wealth Builder** – Automated net savings tracking based on global budget utilization.

## 🏗️ Project Architecture

```
FinPilot/
├── main.py              # FastAPI Application (API Layer, Routing & AI Logic)
├── backend/
│   ├── database.py      # SQLAlchemy Configuration & Session Management
│   └── models.py        # Database Schema (Users, Expenses, Budgets)
├── frontend/
│   ├── static/          # Client-side Assets
│   │   ├── css/         # Professional & Responsive Stylesheets
│   │   └── js/          # Core Application Logic (app.js)
│   └── template/
│       └── index.html   # Main Single-Page Application Template
├── finpilot.db          # SQLite Database (Default)
├── main.py              # FastAPI Application (API Layer, Routing & AI Logic)
├── requirements.txt     # Python Dependencies
├── .env.example         # Environment Config Template
└── GETTING_STARTED.md   # In-depth Setup & Deployment Guide
```

## 🔧 Technical Specification

- **Backend**: FastAPI (Python 3.10+), SQLAlchemy Core/ORM
- **Database**: SQLite (default) / PostgreSQL compatible
- **Security**: PBKDF2 Password Hashing, SHA-256 Blockchain hashes
- **Frontend**: Vanilla JS (ES6+), CSS3 with CSS Variables, HTML5 Semantic Tags

## 📦 Getting Started

### Installation

```bash
# 1. Clone repository and install dependencies
pip install -r requirements.txt

# 2. Initialize Database & Run Server
python main.py
```

The application runs by default at `http://localhost:5500`.

## 🔗 Key API Endpoints

### User & Global Budget

- `GET /api/auth/me` – Current profile data
- `PUT /api/users/{user_id}/budget` – Update **Global Monthly Limit**

### Expenses & Ledger

- `POST /api/expenses/` – Record transaction (triggers Blockchain hashing)
- `GET /api/expenses/` – List ledger entries
- `DELETE /api/expenses/{id}` – Removal with audit deletion

### Proactive Budgeting

- `POST /api/budgets/` – Create category allocation
- `GET /api/budgets/` – Portfolio variance report (Allocated vs. Actual)
- `DELETE /api/budgets/{id}` – De-allocate funds

### Intelligent Audit

- `GET /api/advisor/dashboard` – Consolidated fiscal health report
- `GET /api/advisor/recommendations` – Smart AI insights

## 🔐 Compliance & Security

FinPilot treats financial data with high integrity:

1. **Password Security**: Uses PBKDF2 with 100,000 iterations for robust protection.
2. **Blockchain Verification**: Transactions are immutable; any change to amount or description in the database will invalidate the blockchain hash.
3. **Budget Variance**: Implements real-time tracking of utilization percentages to prevent over-spending.

## 📝 License

Licensed under the MIT License. **FinPilot** – Mastering your money through intelligence.
