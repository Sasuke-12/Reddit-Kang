import os
from telethon import TelegramClient

api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
agent = os.environ.get('AGENT')
subreddit = os.environ.get('SUBREDDIT')
channel_id = os.environ.get('APPROVAL_CHANNEL_ID')
main_channel_id = os.environ.get('MAIN_CHANNEL_ID')

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
