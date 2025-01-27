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
from constants import id_admin, days
from states import *
from telegram.constants import ParseMode
import datetime

from sup_func import escape_text, get_day

import asyncio
from db import subscriptions, add_subscription, schedule, lesson
from admin_func import admin_start


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if context.args:
        if 'sign_up' in context.args[0]:
            return await sign_up_lesson(update,context)
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
        return await user_schedule(update,context)
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



async def user_schedule(update:Update, context:ContextTypes.DEFAULT_TYPE):
    
    query = update.callback_query

    if query.data == "<":
        context.user_data['current_day'] -= 1
    elif query.data == ">":
        context.user_data['current_day'] += 1
    else:
        context.user_data['current_day'] = get_day()

    db_shedule = await schedule()
    text = f"`{days[context.user_data['current_day']-1]:^15}`"
    
    for lesson in db_shedule:
        text += f"\n[{lesson[5]}: {lesson[3]}](https://t.me/SuperManBossBot?start=sign_up_{lesson[0]})"
        print(lesson)
    
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

async def sign_up_lesson(update:Update,context:ContextTypes.DEFAULT_TYPE):
    lesson_id = int(context.args[0].split('_')[2])
    lesson_info = await lesson(lesson_id)
    text = f"*{lesson_info[1]}*\nЗанятие проводит: {lesson_info[5]}\nДата: {lesson_info[2]}\nВремя: {lesson_info[3]}\nВсего мест: {lesson_info[6]}\nСвободно: {lesson_info[6]-lesson_info[7]}"
    keyboard = [
            [InlineKeyboardButton("Записаться", callback_data="sign up")],
            [InlineKeyboardButton("Close", callback_data="close")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=escape_text(text),
                reply_markup=markup,
                parse_mode=ParseMode.MARKDOWN_V2
    )
    return SIGN_UP_LESSON

async def test():
    db_shedule = await schedule()
    text = ""
    for lesson in db_shedule:
        text += f"\n[{lesson[5]}: {lesson[3]}](https://t.me/SuperManBossBot?start={lesson[0]})"
        print(lesson)
    print(text)

if __name__ == "__main__":
    asyncio.run(test())

