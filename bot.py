from datetime import datetime
from os import getenv

from pyrogram import Client
from pyrogram.raw.functions.messages import GetScheduledHistory
from pyrogram.errors import WebpageMediaEmpty

import config
from api import get_posts
from logs import get_logger, get_skipped_logger

bot = Client(
    "e621-2-tg",
    api_id=414121,
    api_hash='db09ccfc2a65e1b14a937be15bdb5d4b',
    phone_number=getenv("PHONE")
)

logger = get_logger(__name__)
skipped = get_skipped_logger()


async def main():
    post: str = ""
    reached_end: bool = False

    async with bot:
        scheduled: list = (await bot.invoke(GetScheduledHistory(
            peer=await bot.resolve_peer(config.get("peer")),
            hash=0
        ))).messages

        schedule = config.get_schedule(datetime.now())
        if (i := len(scheduled)) > 0:
            schedule = config.get_schedule(datetime.fromtimestamp(scheduled[0].date))

        schedule_date: datetime = next(schedule)

        posts = get_posts(config.get("tags"))
        if config.get("reversed"):
            posts = reversed(tuple(posts))

        for post in posts:
            if i >= config.get("schedule_limit"):
                logger.info(f'Schedule limit reached ({i})')
                break

            if res := await send_post(post, schedule_date):
                i += 1
                schedule_date = next(schedule)

            logger.debug(f'Success: {res}')
        else:
            reached_end = True

    if config.get("use_last_id") and post:
        if reached_end:
            logger.warning('No more posts to schedule')
            value = -1
        else:
            logger.debug(f'Last ID: {post}')
            value = int(post.split("/")[-1])

        config.set_last_id(value)


async def send_post(post: str, schedule_date: datetime) -> bool:
    logger.debug(f'Scheduling post "{post}" at {schedule_date}')

    if config.get("post") == 'sample':
        return await send_sample(post, schedule_date)

    return await send_link(post, schedule_date, config.get("post") != 'link')


async def send_sample(post: str, schedule_date: datetime) -> bool:
    try:
        await bot.send_photo(config.get("peer"), post, post, schedule_date=schedule_date)
    except WebpageMediaEmpty:
        skipped.critical(post)
        logger.error(f'No sample for "{post}"')
        match config.get("no_sample"):
            case 'preview' | 'link':
                return await send_link(post, schedule_date, config.get("no_sample") == 'preview')
            case _:
                logger.debug(f'Skipping "{post}"')
                return False

    return True


async def send_link(post: str, schedule_date: datetime, preview: bool) -> bool:
    await bot.send_message(
        config.get("peer"), post,
        disable_web_page_preview=not preview,
        schedule_date=schedule_date
    )
    return True
