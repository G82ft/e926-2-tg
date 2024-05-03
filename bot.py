from datetime import datetime
from os import getenv

from pyrogram import Client
from pyrogram.raw.functions.messages import GetScheduledHistory

import config
from api import get_posts
from logs import get_logger

bot = Client(
    "e926-2-tg",
    api_id=414121,
    api_hash='db09ccfc2a65e1b14a937be15bdb5d4b',
    phone_number=getenv("PHONE")
)

logger = get_logger(__name__)


async def main():
    post: str = ""
    reached_end: bool = False

    async with bot:
        scheduled: list = (await bot.invoke(GetScheduledHistory(
            peer=await bot.resolve_peer(config.get("peer")),
            hash=0
        ))).messages

        schedule = config.get_schedule(datetime.now())
        if len(scheduled) > 0:
            schedule = config.get_schedule(datetime.fromtimestamp(scheduled[0].date))

        for i, post in enumerate(get_posts(config.get("tags")), start=len(scheduled)):
            if i >= config.get("schedule_limit"):
                logger.info(f'Schedule limit reached ({i})')
                break

            schedule_date = next(schedule)
            logger.info(f'Scheduling post "{post}" at {schedule_date}')
            await bot.send_photo(config.get("peer"), post, post, schedule_date=schedule_date)
        else:
            reached_end = True

    if config.get("use_last_id") and post:
        if reached_end:
            logger.warning('No more posts to schedule')
            value = None
        else:
            logger.debug(f'Last ID: {post}')
            value = int(post.split("/")[-1])

        config.set_last_id(value)
