import re
from datetime import datetime

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from app.database import SessionLocal
from app.models import Rent

TOKEN = "8731949415:AAGAJilDUS941ScEayQ81gIpCBWd9ODsP3I"


#  DB Helper
def get_db():
    return SessionLocal()


#  Smart Parser (important)
def extract_location(text: str):
    text = text.lower()

    if "naya raipur" in text:
        return "NayaRaipur"

    return None


#  Main Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    #  Only process rent-related messages
    if "rent" in text and "paid" in text:

        location = extract_location(text)

        if not location:
            await update.message.reply_text("❌ Location not recognized")
            return

        db = get_db()

        #  Get latest pending rent
        rent = (
            db.query(Rent)
            .filter(Rent.location == location, Rent.status == "pending")
            .order_by(Rent.created_at.desc())
            .first()
        )

        if not rent:
            await update.message.reply_text("❌ No pending rent found")
            db.close()
            return

        #  Mark as confirmed
        rent.status = "confirmed"
        rent.confirmed_at = datetime.utcnow()

        db.commit()

        await update.message.reply_text(
            f" Rent Confirmed\n"
            f"Location: {location}\n"
            f"Amount: ₹{rent.amount}\n"
            f"Txn ID: {rent.txn_id}"
        )

        db.close()

    else:
        await update.message.reply_text(" Message not understood")


# Start Bot
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot running...")
app.run_polling()

# why outside app

# -m app.telegram_bot tells Python:
# treat app as a package
# resolve imports correctly