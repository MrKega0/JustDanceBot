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
from datetime import datetime, timedelta
from telegram.helpers import escape_markdown


from sup_func import escape_text, get_day, day_to_date

import asyncio
from db import subscriptions, add_subscription, schedule, lesson, one_day_schedule, create_registration, add_user
from admin_func import admin_start


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await add_user(update.effective_user.id, update.effective_user.username, update.effective_user.full_name)
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
        return await user_subscription(update,context)
    elif query.data == "my appointments": #Мои записи
        print("my appointments")

async def user_subscription(update:Update,context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    db_subscriptions = await subscriptions(context._user_id) #subscription_id, user_id, remaining_classes, expiration_date
    if db_subscriptions:
        max_date = max([datetime.date(datetime.strptime(i,"%Y-%m-%d")) for _,_,_,i in db_subscriptions])
        now = datetime.date(datetime.now())
        time_until_end_subscription = (max_date - now)
        total_lessons = sum([i for _,_,i,_ in db_subscriptions])
        print(time_until_end_subscription,'--------------')
        text = f"У вас есть абонемент на {time_until_end_subscription.days} дней\nОсталось занятий: {total_lessons}"
    else:
        text = "У вас нет абонемента"
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

async def user_schedule(update:Update, context:ContextTypes.DEFAULT_TYPE):
    
    query = update.callback_query

    if query.data == "<":
        context.user_data['current_day'] -= 1
    elif query.data == ">":
        context.user_data['current_day'] += 1
    else:
        context.user_data['current_day'] = get_day()

    # datetime.date.weekday()
    current_date = day_to_date(context.user_data['current_day'])
    db_shedule = await one_day_schedule(current_date)
    print(current_date)
    print(db_shedule)

    if context.user_data['current_day']>=1 and context.user_data['current_day']<=7:
        text = f"`{days[context.user_data['current_day']-1]:^15}`"
    else:
        current_ru_date = datetime.strptime(current_date,"%Y-%m-%d").strftime("%d-%m-%Y")
        text = f"`{current_ru_date:^15}`"


    if db_shedule:
        for lesson in db_shedule:
            text += f"\n[{lesson[5]}: {lesson[3]}](https://t.me/SuperManBossBot?start=sign_up_{lesson[0]})"
            print(lesson)
    else:
        text += '\nНет записей'
        
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
    context.user_data['reg_lesson_id'] = lesson_id
    markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=escape_text(text),
                reply_markup=markup,
                parse_mode=ParseMode.MARKDOWN_V2
    )
    return SIGN_UP_LESSON

async def make_registration(update:Update,context:ContextTypes.DEFAULT_TYPE):
    lesson_id = context.user_data['reg_lesson_id']
    await create_registration(update.effective_user.id, lesson_id)

    query = update.callback_query
    await query.answer()
    
    


async def test():
    db_shedule = await schedule()
    text = ""
    for lesson in db_shedule:
        text += f"\n[{lesson[5]}: {lesson[3]}](https://t.me/SuperManBossBot?start={lesson[0]})"
        print(lesson)
    print(text)

if __name__ == "__main__":
    asyncio.run(test())

