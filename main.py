import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
)
from dotenv import load_dotenv
import os
from common_user_func import start
from db import create_tables

from states import START, MAINMENU, ADMIN

load_dotenv()

from common_user_func import reply_markup_handler, reply_markup_admin_handler

import asyncio

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def main():
    TOKEN = os.getenv("TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()

    menu_conv_hand = ConversationHandler(
        entry_points=[CommandHandler("start", start, has_args=False)],
        states={
            START: [CommandHandler("start", start)],
            MAINMENU: [CallbackQueryHandler(reply_markup_handler)],
            ADMIN: [CallbackQueryHandler(reply_markup_admin_handler)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(menu_conv_hand)
    application.run_polling()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_tables())
    main()
