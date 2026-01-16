# FinPilot - AI-Powered Personal Finance Manager

A lightweight personal finance management platform with expense tracking, budgeting, AI-powered recommendations, and blockchain transaction verification.

## 📋 Features

- **Budget Management** – Create and monitor budgets
- **Expense Tracking** – Categorized expense logging with blockchain verification
- **AI Advisor** – Personalized financial insights and recommendations
- **Savings Goals** – Track progress toward financial goals
- **Spending Analysis** – Pattern analysis and monthly forecasting
- **Responsive UI** – Mobile-friendly dashboard

## 🏗️ Project Structure

```
FinPilot/
├── main.py              # FastAPI app with all routes
├── backend/
│   ├── models.py        # Database models and business logic
│   └── database.py      # Database configuration
├── frontend/
│   ├── template/
│   │   └── index.html   # Single-page application
│   └── static/
│       ├── css/         # Styling
│       └── js/          # Frontend logic
└── requirements.txt     # Dependencies
```

## 🔧 Tech Stack

- **Backend**: FastAPI 0.128.0, SQLAlchemy 2.0.45
- **Database**: SQLite / PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Security**: PBKDF2 password hashing, SHA256 blockchain verification

## 📦 Quick Start

### Install & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run application
python main.py

# 3. Open http://localhost:8000
```

## 🔗 API Endpoints

### Authentication
- `POST /api/auth/register` – Create account
- `POST /api/auth/login` – Login user
- `GET /api/auth/me` – Get user info

### Expenses
- `POST /api/expenses/` – Create expense
- `GET /api/expenses/` – List expenses
- `PUT /api/expenses/{id}` – Update expense
- `DELETE /api/expenses/{id}` – Delete expense

### Budgets
- `POST /api/budgets/` – Create budget
- `GET /api/budgets/` – List budgets
- `PUT /api/budgets/{id}` – Update budget
- `DELETE /api/budgets/{id}` – Delete budget

### Savings Goals
- `POST /api/savings/` – Create goal
- `GET /api/savings/` – List goals
- `PUT /api/savings/{id}` – Update goal
- `DELETE /api/savings/{id}` – Delete goal

### AI Advisor
- `GET /api/advisor/recommendations` – Get personalized recommendations
- `GET /api/advisor/analysis` – Analyze spending patterns
- `GET /api/advisor/forecast` – Predict monthly spending
- `GET /api/advisor/dashboard` – Complete dashboard summary

## 📊 Database Models

- **User** – Accounts and authentication
- **Expense** – Categorized spending with blockchain hash
- **Budget** – Monthly/quarterly/yearly limits
- **SavingsGoal** – Financial targets with progress tracking
- **Transaction** – Audit trail with blockchain verification

## 🔐 Security

- PBKDF2 password hashing (100,000 iterations)
- SHA256 blockchain hashing for transaction integrity
- SQL injection protection via SQLAlchemy ORM
- Relationship constraints and foreign keys

## 📝 License

Open source - feel free to use and modify

### 4. Run the application
```bash
python main.py
```

The application will be available at `http://localhost:8000`

## 🚀 API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

### Authentication Endpoints
- `POST /api/auth/register` – Create new user account
- `POST /api/auth/login` – User login
- `GET /api/auth/me` – Get current user info

### Expense Management
- `POST /api/expenses/` – Create new expense
- `GET /api/expenses/` – Get all expenses
- `GET /api/expenses/{id}` – Get specific expense
- `PUT /api/expenses/{id}` – Update expense
- `DELETE /api/expenses/{id}` – Delete expense

### Budget Management
- `POST /api/budgets/` – Create budget
- `GET /api/budgets/` – Get all budgets
- `GET /api/budgets/{id}` – Get specific budget
- `PUT /api/budgets/{id}` – Update budget
- `DELETE /api/budgets/{id}` – Delete budget

### Savings Goals
- `POST /api/savings/` – Create savings goal
- `GET /api/savings/` – Get all goals
- `GET /api/savings/{id}` – Get specific goal
- `PUT /api/savings/{id}` – Update goal
- `DELETE /api/savings/{id}` – Delete goal

### AI Advisor
- `GET /api/advisor/recommendations` – Get financial recommendations
- `GET /api/advisor/analysis` – Analyze spending patterns
- `GET /api/advisor/forecast` – Get monthly spending forecast
- `GET /api/advisor/dashboard` – Get complete dashboard summary

## 🔐 Security Features

### Password Security
- Bcrypt-based password hashing with salt
- PBKDF2 key derivation
- Secure password verification

### Blockchain Verification
- SHA256 hashing of transactions
- Immutable audit trail
- Chain-linked transactions for tamper detection
- Transaction verification endpoints

## 🤖 AI Advisor Features

The AI engine provides:
- **Spending Analysis** – Categorized spending breakdown
- **Pattern Recognition** – Identify spending trends
- **Budget Recommendations** – Smart budget optimization
- **Monthly Forecasting** – Predict end-of-month spending
- **Personalized Insights** – Category-specific recommendations
- **Goal Tracking** – Monitor savings progress

## 📊 Database Models

### User
- id, username, email, password_hash, full_name
- created_at, updated_at, is_active

### Expense
- id, user_id, amount, category, description, date
- blockchain_hash for verification

### Budget
- id, user_id, name, category, limit, period
- start_date, end_date

### Savings Goal
- id, user_id, name, target_amount, current_amount
- deadline, description

### Transaction
- id, user_id, expense_id, type, amount
- blockchain_hash, previous_hash, verified status

## 🧪 Testing

Run tests with:
```bash
pytest
```

## 📈 Future Enhancements

- [ ] Multi-currency support
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Bill reminders and notifications
- [ ] Integration with banking APIs
- [ ] Advanced portfolio tracking
- [ ] Machine learning price predictions
- [ ] Two-factor authentication
- [ ] Data export functionality
- [ ] Dark mode UI

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Create a feature branch
2. Make your changes
3. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For issues, questions, or suggestions, please open an issue on the repository.

---

**FinPilot** – Make better money decisions with AI-powered insights! 💰🤖
