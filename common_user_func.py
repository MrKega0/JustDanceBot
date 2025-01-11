import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    InlineQueryHandler,
)
from dotenv import load_dotenv
import os
from constants import id_admin
from states import *
from telegram.constants import ParseMode

from db import shedule, subscriptions


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(context.args)
    if context.args:
        if context.args[0] == '2':
            await context.bot.send_message(
            chat_id= update.effective_chat.id,
            text="[тык](https://t.me/SuperManBossBot?start=2)",
            parse_mode=ParseMode.MARKDOWN_V2
        )
    if update.effective_user.id in id_admin: # главное меню админа
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
        await context.bot.send_message(
            chat_id= update.effective_chat.id,
            text="[тык](https://t.me/SuperManBossBot?start=2)",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return ADMIN
    else:   # главное меню пользователя
        keyboard = [
            [
                InlineKeyboardButton('Расписание', callback_data='schedule') 
            ],
            [
                InlineKeyboardButton('Мой абонемент', callback_data='my subscription')
            ],
            [
                InlineKeyboardButton('Записаться', callback_data='sign up lesson')
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_markup=markup,
            text="Привет, я бот для записи на уроки танцев, также я могу показать расписание, ваши записи и многое другое!"
        )
        return MAINMENU


async def reply_markup_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()
    if query.data == 'schedule':
        print('schedule')
    elif query.data == 'my subscription':
        db_subscriptions = map(str, await subscriptions(context._user_id))
        text = '\n'.join(db_subscriptions)
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('Купить абонемент',callback_data='close')],
            [InlineKeyboardButton('Купить 3 абонемента',callback_data='close')],
            [InlineKeyboardButton('Close',callback_data='close')]
            ]))
    elif query.data == 'sign up lesson':
        print('sign up lesson')
    elif query.data == 'close':
        await query.delete_message()
        await start(update,context)

async def reply_markup_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    await query.answer()
    if query.data == 'schedule':
        db_shedule = map(str, await shedule())
        text = '\n'.join(db_shedule)
        await query.edit_message_text(text,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Close',callback_data='close')]]))
    elif query.data == 'subscriptions':
        print("subscriptions")
    elif query.data == 'close':
        await query.delete_message()
        await start(update,context)
    