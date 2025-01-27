import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    InlineQueryHandler,
)
import os
from constants import id_admin
from states import *
from telegram.constants import ParseMode
import datetime
from db import schedule


async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Расписание", callback_data="schedule")],
        [InlineKeyboardButton("Абонементы", callback_data="subscriptions")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Меню администратора",
        reply_markup=markup,
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="[тык](https://t.me/SuperManBossBot?start=2)",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    return ADMIN

async def reply_markup_admin_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    await query.answer()
    if query.data == "schedule":
        db_shedule = map(str, await schedule())
        text = "\n".join(db_shedule)
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Close", callback_data="close")]]
            ),
        )
    elif query.data == "subscriptions":
        print("subscriptions")
    elif query.data == "close":
        await query.delete_message()
        return await admin_start(update, context)