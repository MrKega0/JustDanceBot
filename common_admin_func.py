import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
)


async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton('Расписание', callback_data='schedule') 
        ],
        [
            InlineKeyboardButton('Абонементы', callback_data='subscriptions')
        ],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id= update.effective_chat.id,
        text="Меню администратора",
        reply_markup=markup,
    )


async def reply_markup_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()
    if query.data == 'schedule':
        pass
    elif query.data == 'subscriptions':
        pass
    