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

from db import subscriptions, add_subscription
from common_user_func import start, user_subscription

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