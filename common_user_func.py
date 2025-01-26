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

import asyncio
from db import subscriptions, add_subscription, shedule
from admin_func import admin_start


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        if context.args[0] == "2":
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="[тык](https://t.me/SuperManBossBot?start=2)",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
    if update.effective_user.id in id_admin:  # главное меню админа
        return await admin_start(update, context)
    else:  # главное меню пользователя
        keyboard = [
            [InlineKeyboardButton("Расписание", callback_data="schedule")],
            [InlineKeyboardButton("Мой абонемент", callback_data="my subscription")],
            [InlineKeyboardButton("Мои записи", callback_data="my appointments")],
        ]
        markup = InlineKeyboardMarkup(keyboard)

        query = update.callback_query
        if query:
            await query.answer()
            # Менять текст менюшки
            await query.edit_message_text(
                text="Главное Меню",
                reply_markup=markup,
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                reply_markup=markup,
                text="Привет, я бот для записи на уроки танцев, также я могу показать расписание, ваши записи и многое другое!",
            )
        return MAINMENU

async def reply_markup_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer() 
    if query.data == "schedule": #Расписание
        return await user_shedule(update,context)
    elif query.data == "my subscription":
        db_subscriptions = map(str, await subscriptions(context._user_id))
        text = "\n".join(db_subscriptions)
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Купить абонемент", callback_data="pay")],
                    [InlineKeyboardButton("Купить 3 абонемента", callback_data="pay3")],
                    [InlineKeyboardButton("Close", callback_data="close")],
                ]
            ),
        )
        return MY_SUBSCRIPTIONS
    elif query.data == "my appointments": #Мои записи
        print("my appointments")



async def user_shedule(update:Update, context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    db_shedule = await shedule()
    text = ""
    for lesson in db_shedule:
        text += f"\n[{lesson[5]}: {lesson[3]}](https://t.me/SuperManBossBot?start={lesson[0]})"
        print(lesson)
    print(text)
    await query.edit_message_text(
        text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("<", callback_data="<"),
                    InlineKeyboardButton(">", callback_data=">")
                ],
                [InlineKeyboardButton("Close", callback_data="close")],
            ]
        ),
    )
    return SCHEDULE



async def test():
    db_shedule = await shedule()
    text = ""
    for lesson in db_shedule:
        text += f"\n[{lesson[5]}: {lesson[3]}](https://t.me/SuperManBossBot?start={lesson[0]})"
        print(lesson)
    print(text)

if __name__ == "__main__":
    asyncio.run(test())

