# 🚀 FinPilot - Getting Started

## ✅ Setup Complete!

Your FinPilot installation is ready to use. Here's what was set up:

### Installed Components
- ✓ Python backend (FastAPI)
- ✓ Database (SQLite)
- ✓ Frontend (HTML/CSS/JavaScript)
- ✓ AI Engine
- ✓ Blockchain verification

### Database Status
- ✓ SQLite database created: `finpilot.db`
- ✓ All tables initialized
- ✓ Ready for data entry

---

## 🎯 Quick Start

### Option 1: Run with Auto-Reload (for Development)
```bash
cd FinPilot
python main.py
```

### Option 2: Run with Uvicorn
```bash
cd FinPilot
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Run in Background (PowerShell)
```powershell
Start-Process python -ArgumentList "main.py" -WindowStyle Hidden
```

---

## 🌐 Access the Application

Once the server is running (you'll see `Uvicorn running on http://0.0.0.0:8000`):

| Resource | URL |
|----------|-----|
| **Main App** | http://localhost:8000 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **Alternative Docs (ReDoc)** | http://localhost:8000/redoc |
| **Health Check** | http://localhost:8000/health |

---

## 👤 First Login

The app uses localStorage for demo purposes:

1. **Open** http://localhost:8000
2. **Click "Register"** tab
3. **Fill in details**:
   - Username: `testuser`
   - Email: `test@example.com`
   - Full Name: `Test User`
   - Password: `password123`
4. **Click "Register"**
5. You'll be logged in and see the dashboard!

---

## 🎨 Features to Try

### 1. **Add Expenses** (Expenses tab)
- Amount: $50.00
- Category: Food
- Description: Lunch

### 2. **Create Budgets** (Budgets tab)
- Budget Name: Monthly Groceries
- Category: Food
- Limit: $300.00

### 3. **Set Savings Goals** (Savings tab)
- Goal Name: Vacation Fund
- Target: $2000.00
- Deadline: 2026-06-30

### 4. **Get AI Advice** (AI Advisor tab)
- View spending analysis
- Get personalized recommendations
- See monthly forecasts

---

## 📊 API Examples

### Using curl or Postman

#### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure123",
    "full_name": "John Doe"
  }'
```

#### Add Expense
```bash
curl -X POST http://localhost:8000/api/expenses/ \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 45.50,
    "category": "food",
    "description": "Dinner at restaurant"
  }' \
  -H "user_id: 1"
```

#### Get Recommendations
```bash
curl http://localhost:8000/api/advisor/recommendations?user_id=1
```

**Full API documentation available at**: http://localhost:8000/docs

---

## 🗂️ Project Structure Quick Reference

```
FinPilot/
├── backend/
│   ├── models/           # Database models
│   ├── routes/           # API endpoints
│   ├── blockchain/       # Transaction verification
│   ├── ai_engine/        # AI advisor logic
│   └── database.py       # Database setup
├── frontend/
│   ├── template/
│   │   └── index.html    # Main UI
│   └── static/
│       ├── css/          # Styles
│       └── js/           # App logic
├── config/               # Settings
├── main.py              # FastAPI app
├── requirements.txt     # Dependencies
└── README.md            # Full documentation
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```env
DATABASE_URL=sqlite:///./finpilot.db
DEBUG=True
SECRET_KEY=your-secret-key
LOG_LEVEL=INFO
```

### Switch Database (Optional)

For production, use PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@localhost/finpilot
```

Then install PostgreSQL driver:
```bash
python -m pip install psycopg2-binary
```

---

## 🧪 Testing the Application

### Test All Features
1. **Register** with the Register button
2. **Add Expenses** - Create 5-10 expenses in different categories
3. **Create Budgets** - Set monthly limits for categories
4. **Add Savings Goals** - Set vacation/emergency fund goals
5. **View Dashboard** - See your overview with AI recommendations
6. **Check AI Advisor** - View spending patterns and forecasts

### Clear All Data
```bash
# Delete the database file
del finpilot.db

# Re-initialize
python -c "from backend.database import init_db; init_db()"
```

---

## 📱 Mobile Access

Open your browser on your phone and navigate to:
```
http://<YOUR_COMPUTER_IP>:8000
```

Replace `<YOUR_COMPUTER_IP>` with your computer's IP address (get it with `ipconfig` on Windows).

---

## 🐛 Troubleshooting

### Port 8000 Already In Use
```bash
# Use a different port
python -m uvicorn main:app --port 8001
```

### ModuleNotFoundError
```bash
# Reinstall dependencies
python -m pip install -r requirements.txt --upgrade
```

### Database Issues
```bash
# Reset database
del finpilot.db
python -c "from backend.database import init_db; init_db()"
```

### Application Won't Start
1. Check Python version: `python --version` (should be 3.8+)
2. Verify dependencies: `python -m pip list | grep -E "fastapi|sqlalchemy|pydantic"`
3. Check port: `netstat -ano | findstr :8000` (Windows)

---

## 📚 API Documentation

Swagger UI provides interactive API testing at http://localhost:8000/docs

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get profile

#### Expenses
- `POST /api/expenses/` - Add expense
- `GET /api/expenses/` - List expenses
- `PUT /api/expenses/{id}` - Update expense
- `DELETE /api/expenses/{id}` - Delete expense

#### Budgets
- `POST /api/budgets/` - Create budget
- `GET /api/budgets/` - List budgets
- `PUT /api/budgets/{id}` - Update budget
- `DELETE /api/budgets/{id}` - Delete budget

#### Savings
- `POST /api/savings/` - Create goal
- `GET /api/savings/` - List goals
- `PUT /api/savings/{id}` - Update goal
- `DELETE /api/savings/{id}` - Delete goal

#### AI Advisor
- `GET /api/advisor/recommendations` - Get advice
- `GET /api/advisor/analysis` - Spending analysis
- `GET /api/advisor/forecast` - Monthly forecast
- `GET /api/advisor/dashboard` - Complete summary

---

## 🚀 Next Steps

1. **Explore the frontend** - Get familiar with the UI
2. **Test the APIs** - Use Swagger UI at `/docs`
3. **Add real data** - Enter your own expenses and budgets
4. **Customize** - Modify the code to fit your needs
5. **Deploy** - Follow deployment guide for production

---

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Guide](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Server](https://www.uvicorn.org/)

---

## 💬 Support

If you encounter issues:
1. Check the **Troubleshooting** section above
2. Review **SETUP_GUIDE.md** for detailed setup help
3. Check **README.md** for full documentation
4. Review error messages carefully

---

## 🎉 You're All Set!

Your FinPilot personal finance manager is ready to use. Start tracking your expenses and getting AI-powered insights!

**Happy financial tracking!** 💰🤖

---

**Last Updated**: January 15, 2026  
**FinPilot Version**: 1.0.0
