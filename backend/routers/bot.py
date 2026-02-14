from fastapi import APIRouter, Depends, Form, Response
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.bot_service import WhatsAppBotService

router = APIRouter(prefix="/bot", tags=["bot"])

@router.post("/whatsapp")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Twilio Webhook for WhatsApp.
    Twilio sends data as Form parameters:
    - From: The sender's phone number (e.g., 'whatsapp:+1234567890')
    - Body: The message text
    """
    
    # Strip the 'whatsapp:' prefix if present
    phone_number = From.replace("whatsapp:", "").strip()
    
    # Process the message
    reply_text = await WhatsAppBotService.process_message(db, phone_number, Body)
    
    # Generate TwiML response
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply_text}</Message>
</Response>"""

    return Response(content=twiml_response, media_type="application/xml")
