from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Expense, User
from .blockchain import BlockchainVerifier

class AuditService:
    """Service to perform financial integrity and compliance audits"""

    def __init__(self, db: Session):
        self.db = db

    def perform_integrity_sweep(self, user_id: int) -> Dict:
        """Verify all transactions using BlockchainVerifier"""
        # We must verify in ascending order to reconstruct the chain correctly
        expenses = self.db.query(Expense).filter(Expense.user_id == user_id).order_by(Expense.id.asc()).all()
        tampered = []
        verified_count = 0
        current_prev_hash = None

        for exp in expenses:
            is_valid = BlockchainVerifier.verify_transaction(
                blockchain_hash=exp.blockchain_hash,
                transaction_id=exp.id,
                user_id=user_id,
                amount=exp.amount,
                description=exp.description or "",
                timestamp=exp.date,
                previous_hash=current_prev_hash
            )
            
            if not is_valid:
                tampered.append({
                    "id": exp.id,
                    "date": exp.date.isoformat(),
                    "amount": exp.amount,
                    "category": exp.category.value,
                    "description": exp.description,
                    "expected_hash": exp.blockchain_hash
                })
            else:
                verified_count += 1
            
            # Chain the hash for the next record
            current_prev_hash = exp.blockchain_hash

        return {
            "status": "Compromised" if tampered else "Stable",
            "total_count": len(expenses),
            "verified_count": verified_count,
            "tampered_records": tampered
        }

    def detect_anomalies(self, user_id: int) -> List[Dict]:
        """Detect duplicate transactions and spending outliers"""
        anomalies = []
        
        # 1. Duplicate Detection (Same amount, category, date, payee)
        # Using func.date to catch same-day duplicates regardless of exact time
        duplicates = self.db.query(
            Expense.amount, 
            Expense.category, 
            func.date(Expense.date).label('date_only'), 
            Expense.payee, 
            func.count('*').label('count')
        ).filter(Expense.user_id == user_id).group_by(
            Expense.amount, 
            Expense.category, 
            'date_only', 
            Expense.payee
        ).having(func.count('*') > 1).all()

        for d in duplicates:
            anomalies.append({
                "type": "Duplicate Entry",
                "severity": "Medium",
                "details": f"Potential double-posting: {d.count} records for ₹{d.amount:,.2f} found on {d.date_only}.",
                "recommendation": "Verify your ledger for manual entry errors."
            })

        # 2. Outlier Detection (> 300% of category average in last 90 days)
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        # 3. Category Shift Detection (Sudden 50% increase in total category spend)
        this_month_start = datetime.utcnow().replace(day=1)
        prev_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        
        categories = self.db.query(Expense.category).filter(Expense.user_id == user_id).distinct().all()

        for (cat,) in categories:
            # Outlier Logic
            avg_query = self.db.query(func.avg(Expense.amount)).filter(
                Expense.user_id == user_id,
                Expense.category == cat,
                Expense.date >= ninety_days_ago
            ).scalar() or 0

            if avg_query > 0:
                outliers = self.db.query(Expense).filter(
                    Expense.user_id == user_id,
                    Expense.category == cat,
                    Expense.amount > (avg_query * 3)
                ).all()

                for o in outliers:
                    anomalies.append({
                        "type": "Spending Outlier",
                        "severity": "High",
                        "details": f"Significant transaction: ₹{o.amount:,.2f} in {cat.value.capitalize()} (Average: ₹{avg_query:,.2f}).",
                        "recommendation": "Confirm this high-value procurement is authorized."
                    })
            
            # Category Shift Logic
            current_total = self.db.query(func.sum(Expense.amount)).filter(
                Expense.user_id == user_id,
                Expense.category == cat,
                Expense.date >= this_month_start
            ).scalar() or 0
            
            prev_total = self.db.query(func.sum(Expense.amount)).filter(
                Expense.user_id == user_id,
                Expense.category == cat,
                Expense.date >= prev_month_start,
                Expense.date < this_month_start
            ).scalar() or 0

            if prev_total > 5000 and current_total > prev_total * 1.5:
                anomalies.append({
                    "type": "Category Shift",
                    "severity": "Medium",
                    "details": f"Spending in {cat.value.capitalize()} has surged by {((current_total/prev_total)-1)*100:.0f}% vs last month.",
                    "recommendation": "Investigate surge in category-specific burn rate."
                })

        return anomalies

    def check_compliance(self, user_id: int) -> Dict:
        """Check for missing metadata and regulatory readiness"""
        expenses = self.db.query(Expense).filter(Expense.user_id == user_id).all()
        
        missing_payee = [e.id for e in expenses if not e.payee]
        missing_ref = [e.id for e in expenses if not e.reference_no]
        
        compliance_score = 100
        if expenses:
            deduction = (len(missing_payee) + len(missing_ref)) / (len(expenses) * 2) * 100
            compliance_score = max(0, 100 - int(deduction))

        return {
            "score": compliance_score,
            "missing_payee_count": len(missing_payee),
            "missing_reference_count": len(missing_ref),
            "tax_ready": compliance_score > 90
        }
