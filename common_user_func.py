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

from db import shedule, subscriptions, add_subscription


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        if context.args[0] == "2":
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="[тык](https://t.me/SuperManBossBot?start=2)",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
    if update.effective_user.id in id_admin:  # главное меню админа
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
    else:  # главное меню пользователя
        keyboard = [
            [InlineKeyboardButton("Расписание", callback_data="schedule")],
            [InlineKeyboardButton("Мой абонемент", callback_data="my subscription")],
            [InlineKeyboardButton("Записаться", callback_data="sign up lesson")],
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


async def start_without_shipping_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Sends an invoice without requiring shipping details."""
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    title = "Payment Example"
    description = "Example of a payment process using the python-telegram-bot library."
    # Unique payload to identify this payment request as being from your bot
    payload = query.data
    currency = "RUB"
    # Price in dollars
    if query.data == 'pay':
        price = 100
    elif query.data == 'pay3':
        price = 300
    # Convert price to cents from dollars.
    prices = [LabeledPrice("Абонемент", price * 100)]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    await context.bot.send_invoice(
        chat_id, title, description, payload, os.getenv('PAYMENT_PROVIDER_TOKEN'), currency, prices
    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responds to the PreCheckoutQuery as the final confirmation for checkout."""
    query = update.pre_checkout_query
    # Verify if the payload matches, ensure it's from your bot
    if query.invoice_payload not in ["pay",'pay3']:
        # If not, respond with an error
        await query.answer(ok=False, error_message="Something went wrong...")
    else:
        await query.answer(ok=True)


async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Acknowledges successful payment and thanks the user."""
    payload = update.effective_message.successful_payment.invoice_payload
    now = datetime.datetime.now()
    expire_date = now + datetime.timedelta(days=30)
    expire_date3 = now + datetime.timedelta(days=90)
    expire_date3_st = expire_date3.strftime('%Y-%m-%d')
    expire_date_st = expire_date.strftime('%Y-%m-%d')

    if payload == 'pay':
        await add_subscription(update.effective_user.id,'ind',10,expire_date_st)
    elif payload == 'pay3':
        await add_subscription(update.effective_user.id,'ind',30,expire_date3_st)
    return await start(update, context)

async def reply_markup_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()
    if query.data == "schedule":
        print("schedule")
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
    elif query.data == "sign up lesson":
        print("sign up lesson")
    


async def reply_markup_admin_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    await query.answer()
    if query.data == "schedule":
        db_shedule = map(str, await shedule())
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
        await start(update, context)
