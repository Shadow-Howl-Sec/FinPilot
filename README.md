# 💰 FinPilot - AI-Powered Financial Suite

FinPilot is a professional-grade personal finance management platform. It combines traditional accounting principles with modern AI-driven insights and blockchain-backed transaction integrity.

## 📋 Core Capabilities

- **Treasury Management** – Dual-layer budgeting with Global Monthly Caps and granular Category Allocations.
- **Institutional Ledger** – Professional accounting interface for tracking expenses with automated variance analysis.
- **Blockchain Integrity** – Every transaction is hashed using SHA-256 and linked to prevent tampering and ensure auditability.
- **Compliance Audit & Advisor** – Intelligent analysis of spending patterns, daily/weekly/monthly threshold warnings, and category shift detection.
- **Net Savings Tracker** – Automated tracking based on global budget utilization.

## 🏗️ Project Architecture

```
FinPilot/
├── main.py              # FastAPI Application (API Layer, Routing & AI Logic)
├── backend/
│   ├── database.py      # SQLAlchemy Configuration & Session Management
│   ├── models.py        # Database Schema & Blockchain Logic
│   └── routers/         # API Modular Controllers
├── frontend/
│   ├── static/          # Client-side Assets
│   │   ├── css/         # Professional & Responsive Stylesheets
│   │   └── js/          # Core Application Logic (app.js)
│   └── template/
│       └── index.html   # Main Single-Page Application Template
├── .env                 # Environment Configuration (Database Path)
├── requirements.txt     # Python Dependencies
└── README.md            # Project Documentation
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

# 2. Configure Environment
# Ensure .env points to your database (e.g. V:/Projects/Money_management/finpilot.db)

# 3. Initialize Database & Run Server
python main.py
```

The application runs by default at `http://localhost:5500`.

## 🔗 Key API Endpoints

### User & Global Budget

- `GET /api/auth/me` – Current profile data
- `PUT /api/auth/profile` – Update User profile and phone number

### Expenses & Ledger

- `POST /api/expenses/` – Record transaction (triggers Blockchain hashing)
- `GET /api/expenses/` – List ledger entries
- `DELETE /api/expenses/{id}` – Removal with audit deletion

### Treasury (Budgets)

- `POST /api/budgets/` – Create category allocation
- `GET /api/budgets/` – Portfolio variance report (Allocated vs. Actual)
- `DELETE /api/budgets/{id}` – De-allocate funds

### Compliance & Analytics

- `GET /api/advisor/dashboard` – Consolidated fiscal health report
- `GET /api/advisor/audit` – Blockchain integrity & anomaly detection

## 🔐 Compliance & Security

FinPilot treats financial data with high integrity:

1. **Password Security**: Uses PBKDF2 for robust protection.
2. **Blockchain Verification**: Transactions are hashed; any unauthorized database modification will invalidate the signature.
3. **Budget Variance**: Implements real-time tracking of utilization to prevent over-spending.

## 📝 License

Licensed under the MIT License. **FinPilot** – Mastering your money through intelligence.
