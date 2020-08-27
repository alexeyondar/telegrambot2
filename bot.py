#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os
import azure.cosmos.cosmos_client as cosmos_client
import requests

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_ENDPOINT = 'http://backend/api/generate'


def init_db():
    endpoint = os.environ['COSMOS_HOST']
    key = os.environ['COSMOS_KEY']
    client = cosmos_client.CosmosClient(endpoint, {'masterKey': key})
    return client


def store_stats(user, url, url_short):
    client = init_db()
    database_name = 'telegram-bot'
    container_name = 'statistics'

    cosmos_data = {
        'id': user.name,
        'user_id': user.id,
        'user_name': user.full_name,
        'user_nick': user.name,
        'user_link': user.link,
        'url': url,
        'url_short': url_short
    }
    client.UpsertItem("dbs/" + database_name + "/colls/" + container_name, cosmos_data)


def call_backend(url):

    return requests.post(BACKEND_ENDPOINT, data={'url': url}).text

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hello! My name is Bot! Paste url to cut it')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help message')


def url(update, context):
    """Send a message when the command /url is issued."""
    update.message.reply_text('Working...')
    user = update.message.from_user
    url = update.message.text
    link = call_backend(url)

    store_stats(user, url, link)
    update.message.reply_text('Short link: {}'.format(link))


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    TOKEN = os.environ['TOKEN']

    updater = Updater(token=TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, url))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
