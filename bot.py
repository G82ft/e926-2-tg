from datetime import datetime
from os import getenv

from pyrogram import Client
from pyrogram.raw.functions.messages import GetScheduledHistory

import config
from api import get_posts

bot = Client(
    "e926-2-tg",
    api_id=414121,
    api_hash='db09ccfc2a65e1b14a937be15bdb5d4b',
    bot_token=getenv("TOKEN")
)


# async
async def main():
    post: str = ""
    async with bot:
        scheduled: list = (await bot.invoke(GetScheduledHistory(
            peer=await bot.resolve_peer(config.get("peer")),
            hash=0
        ))).messages

        schedule = config.get_schedule(datetime.now())
        if len(scheduled) > 0:
            schedule = config.get_schedule(datetime.fromtimestamp(scheduled[0].date))

        for i, post in enumerate(get_posts(config.get("tags")), start=len(scheduled)):
            print(i, post)
            if i >= config.get("schedule_limit"):
                break
            await bot.send_photo(config.get("peer"), post, post, schedule_date=next(schedule))

    if config.get("use_last_id") and post:
        config.set_last_id(int(post.split("/")[-1]))
