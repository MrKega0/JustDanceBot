import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    PicklePersistence,
    filters,
)
from dotenv import load_dotenv
import os
from common_user_func import start
from db import create_tables

from states import START, MAINMENU, ADMIN, MY_SUBSCRIPTIONS, SCHEDULE, SIGN_UP_LESSON

load_dotenv()

from common_user_func import (
    reply_markup_handler,
    user_schedule
)

from payment_for_subscription import (
    start_without_shipping_callback,
    precheckout_callback,
    successful_payment_callback
)
from admin_func import reply_markup_admin_handler


import asyncio

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# logging.getLogger("httpx").setLevel(logging.WARNING)

def main():
    TOKEN = os.getenv("TOKEN")
    persistence = PicklePersistence(filepath="bot_cache")
    application = ApplicationBuilder().token(TOKEN).persistence(persistence).build()

    menu_conv_hand = ConversationHandler(
        entry_points=[CommandHandler("start", start, has_args=False)],
        states={
            MAINMENU: [CallbackQueryHandler(reply_markup_handler)],
            ADMIN: [CallbackQueryHandler(reply_markup_admin_handler)],
            MY_SUBSCRIPTIONS: [
                CallbackQueryHandler(start, pattern="^close$"),
                CallbackQueryHandler(
                    start_without_shipping_callback, pattern="^(pay|pay3)$"
                ),
                MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)
            ],
            SCHEDULE: [CallbackQueryHandler(start, pattern="^close$"), CallbackQueryHandler(user_schedule, pattern="^(<|>)$")], #Доделать
            SIGN_UP_LESSON: [CallbackQueryHandler(user_schedule, pattern="^close$")]
        },
        fallbacks=[CommandHandler("start", start)],
        name='menu_conv_hand',
        persistent=True
    )

    application.add_handler(menu_conv_hand)
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    # application.add_handler(
    #     MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)
    # )
    application.run_polling()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_tables())
    main()
