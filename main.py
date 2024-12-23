import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler
)
from dotenv import load_dotenv
import os
from common_user_func import start
from db import create_tables

from states import *
load_dotenv()

from common_user_func import reply_markup_handler, reply_markup_admin_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)




if __name__ == "__main__":
    TOKEN = os.getenv("TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()

    menu_conv_hand = ConversationHandler(
        entry_points=[CommandHandler('start',start)],
        states={START:[CommandHandler('start', start)],
                MAINMENU:[CallbackQueryHandler(reply_markup_handler)],
                ADMIN:[CallbackQueryHandler(reply_markup_admin_handler)],
                },
        fallbacks=[CommandHandler('start',start)],
    )



    application.add_handler(menu_conv_hand)
    create_tables()
    application.run_polling()