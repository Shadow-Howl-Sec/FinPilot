import re
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import User, Expense, ExpenseCategory, PaymentMethod, ExpenseStatus
from ..routers.expenses import create_expense
from ..schemas import ExpenseCreate

class WhatsAppBotService:
    """Service to handle WhatsApp message parsing and transaction processing"""

    @staticmethod
    def parse_message(text: str) -> Dict:
        """
        Parse natural language message to extract amount, category, and description.
        Formats supported: 
        - "Spent 500 on food"
        - "₹250 for transport"
        - "transport 100"
        """
        text = text.lower().strip()
        
        # 1. Extract Amount
        # Matches numbers like 500, 500.50, ₹100, RS 100
        amount_match = re.search(r'(?:₹|rs\s*|)\s*(\d+(?:\.\d{1,2})?)', text)
        amount = float(amount_match.group(1)) if amount_match else 0.0

        # 2. Extract Category
        category = ExpenseCategory.OTHER
        categories = {cat.value: cat for cat in ExpenseCategory}
        
        # Find if any category keyword is in the text
        for cat_name, cat_enum in categories.items():
            if cat_name in text:
                category = cat_enum
                break
        
        # 3. Clean Description
        description = text
        if amount_match:
            description = description.replace(amount_match.group(0), "").strip()
        
        # Remove category from description if it exists
        description = description.replace(category.value, "").strip()
        
        # Clean up common fillers
        fillers = ["spent", "on", "for", "paid", "to"]
        for filler in fillers:
            description = re.sub(rf'\b{filler}\b', '', description).strip()
            
        return {
            "amount": amount,
            "category": category,
            "description": description.capitalize() or f"WhatsApp Entry: {category.value.capitalize()}"
        }

    @staticmethod
    def detect_intent(text: str) -> str:
        """Detect if the user wants to record an expense or query status"""
        text = text.lower().strip()
        query_keywords = ["balance", "status", "how much", "summary", "spent", "limit", "budget"]
        
        # If the text has a number and a category but no query keywords, it's likely a record
        has_number = bool(re.search(r'\d+', text))
        
        # Check for explicit query keywords
        if any(keyword in text for keyword in query_keywords) and not (has_number and "spent" in text and len(text.split()) < 5):
             return "query"
             
        return "record"

    @staticmethod
    async def handle_query(db: Session, user: User) -> str:
        """Handle financial status queries"""
        from ..services.advisor_service import FinancialAdvisor
        advisor = FinancialAdvisor(db)
        
        # Get dashboard data
        # We can repurpose advisor logic here
        today = datetime.utcnow()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        month_expenses = db.query(Expense).filter(
            Expense.user_id == user.id,
            Expense.date >= start_of_month
        ).all()
        
        total_spent = sum(e.amount for e in month_expenses)
        global_limit = user.monthly_budget_limit or 0
        net_savings = global_limit - total_spent
        
        forecast = advisor.predict_monthly_spending(user.id)
        
        response = f"📊 *Financial Status Update*\n\n"
        response += f"💰 *Spent this month*: ₹{total_spent:,.2f}\n"
        response += f"🎯 *Global Budget*: ₹{global_limit:,.2f}\n"
        response += f"🏦 *Net Savings*: ₹{net_savings:,.2f}\n\n"
        
        if forecast.get("predicted_monthly_spending"):
            response += f"📈 *Forecasted Spend*: ₹{forecast['predicted_monthly_spending']:,.2f}\n"
            
        # Add high-level alert if over budget
        if net_savings < 0:
            response += f"\n⚠️ *Warning*: You are ₹{abs(net_savings):,.2f} over your monthly limit!"
            
        return response

    @staticmethod
    async def process_message(db: Session, from_number: str, message_body: str) -> str:
        """Identify user, parse message, and create expense OR answer query"""
        user = db.query(User).filter(User.phone_number.contains(from_number[-10:])).first()
        
        if not user:
            return "❌ Phone number not recognized. Please update your phone number in FinPilot settings."

        if not message_body:
            return "❓ I didn't catch that. Try 'Spent 500 on Food' or 'What is my balance?'."

        intent = WhatsAppBotService.detect_intent(message_body)
        
        if intent == "query":
            return await WhatsAppBotService.handle_query(db, user)

        # Handle Record Intent
        data = WhatsAppBotService.parse_message(message_body)
        
        if data["amount"] <= 0:
            return "⚠️ I couldn't identify the amount. Please use a format like '100 for shopping' or ask 'How much have I spent?'."

        try:
            expense_in = ExpenseCreate(
                amount=data["amount"],
                category=data["category"],
                description=data["description"],
                date=datetime.utcnow(),
                payment_method=PaymentMethod.UPI,
                status=ExpenseStatus.CLEARED
            )
            
            new_expense = await create_expense(expense_in, user.id, db)
            
            summary = f"✅ *Record Created*\n"
            summary += f"💰 Amount: ₹{data['amount']:,.2f}\n"
            summary += f"📁 Category: {data['category'].value.capitalize()}\n"
            summary += f"📝 Narration: {data['description']}"
            
            if hasattr(new_expense, 'alerts') and new_expense.alerts:
                 summary += "\n\n🔔 *Alerts:*\n" + "\n".join([f"- {a}" for a in new_expense.alerts])
                 
            return summary
            
        except Exception as e:
            return f"❌ Error processing transaction: {str(e)}"
    @staticmethod
    async def send_welcome_message(db: Session, phone_number: str, full_name: str) -> bool:
        """Send a welcome message to a newly registered user"""
        welcome_text = f"🌟 *Welcome to FinPilot, {full_name or 'Navigator'}!* 🌟\n\n"
        welcome_text += "I am your AI Financial Assistant. You can now record expenses or query your budget right here.\n\n"
        welcome_text += "Try saying: *'Spent 500 on Food'* or *'How is my budget?'*"
        
        # In a real scenario, this would call the Twilio API
        # For now, we log the intent and return success
        try:
            print(f"DEBUG: Sending WhatsApp Welcome to {phone_number}: {welcome_text}")
        except UnicodeEncodeError:
            print(f"DEBUG: Sending WhatsApp Welcome to {phone_number}: [Content contains emojis, suppressed for terminal]")
        return True
