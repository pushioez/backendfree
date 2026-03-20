import os

from dotenv import load_dotenv
import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes


load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MINIAPP_URL = os.getenv("MINIAPP_URL")
if not MINIAPP_URL:
    # Render commonly provides the public URL via `RENDER_EXTERNAL_URL`.
    # Fallback to localhost for local development.
    MINIAPP_URL = os.getenv("RENDER_EXTERNAL_URL") or os.getenv(
        "WEBAPP_URL", "http://127.0.0.1:8000/"
    )
if not MINIAPP_URL.endswith("/"):
    MINIAPP_URL += "/"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat:
        return

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Open Mini App",
                    web_app=WebAppInfo(url=MINIAPP_URL),
                )
            ]
        ]
    )

    await update.effective_chat.send_message(
        "Welcome! Tap the button below to open the Mini App and book an appointment.",
        reply_markup=keyboard,
    )

def create_application() -> Application:
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    return app


def run_polling_blocking() -> None:
    """
    Runs the bot in the current thread.
    When called from a background thread, we disable signal handling.
    """
    print(
        f"[telegram bot] run_polling_blocking() token_configured={bool(BOT_TOKEN)} miniapp_url={MINIAPP_URL}"
    )
    # If webhook was set previously, polling won't receive updates.
    # Clear webhook mode so polling works reliably on Render.
    if BOT_TOKEN:
        try:
            with httpx.Client(timeout=8.0) as client:
                client.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook",
                    data={"drop_pending_updates": "true"},
                )
        except Exception:
            pass

    app = create_application()
    print("[telegram bot] polling started")
    app.run_polling(stop_signals=None)


def main() -> None:
    run_polling_blocking()


if __name__ == "__main__":
    main()

