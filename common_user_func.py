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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        return ADMIN
    else:
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
        print("my subscription")
    elif query.data == 'sign up lesson':
        print('sign up lesson')

async def reply_markup_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()
    if query.data == 'schedule':
        print('schedule')
    elif query.data == 'subscriptions':
        print("subscriptions")