from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
import uvicorn

# Import database initialization
from backend.database import init_db

# Import routers
from backend.routers import auth, expenses, budgets, advisor, bot

app = FastAPI(
    title="FinPilot",
    description="AI-Powered Personal Finance Manager",
    version="1.1.0"
)

# Initialize database
init_db()

# Mount static files
static_dir = Path(__file__).parent / "frontend" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include Routers
app.include_router(auth.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(budgets.router, prefix="/api")
app.include_router(advisor.router, prefix="/api")
app.include_router(bot.router, prefix="/api")

# ==================== HELPER FUNCTION ====================

def get_html_content():
    """Load and return HTML content"""
    template_path = Path(__file__).parent / "frontend" / "template" / "index.html"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<html><body><h1>FinPilot - Loading...</h1></body></html>"

# ==================== ROUTES: HOME ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main frontend page"""
    return get_html_content()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "FinPilot", "version": "1.1.0"}

# ==================== STARTUP ====================

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5500, reload=True)
