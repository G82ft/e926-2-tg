from argparse import ArgumentParser
from datetime import datetime
from os.path import abspath

from api import get_posts, s, ORIGIN
from config import get, DEFAULT, get_last_id
from logs import get_logger

parser: ArgumentParser = ArgumentParser(
    description="Script for verifying config for e926-2-tg.",
    epilog="https://github.com/G82ft/e926-2-tg",
)

parser.add_argument(
    "config",
    nargs="?",
    default="config.json"
)
VALIDATION: tuple[tuple[str, tuple | dict, any], ...]
ITEM: str = "item"

logger = get_logger(__name__)


def validate_config(file: str = "config.json") -> None:
    invalid: bool = False

    logger.info(f'Validating "{abspath(file)}"...')
    for name, args, validate_arg in VALIDATION:
        if is_default(name, config_file=file):
            logger.info(f'{name}: DEFAULT')
            continue
        if check := validate_arg(get(name, config_file=file), name, *args):
            logger.error(f"{name}: {check}")
            invalid = True
            continue

        logger.info(f'{name}: OK')

    logger.info(f'CONFIG: OK')
    if invalid:
        logger.critical(f'CONFIG: FAILED')
        exit(1)


def check_type(value: any, name: str, type_: type | tuple[type, ...]) -> str:
    return not isinstance(value, type_) and f'{name} must be {type_.__name__}. ("{value}" is {type(value).__name__}).'


def check_range(value: any, name: str, min_: int, max_: int) -> str:
    return (
            check_type(value, name, int)
            or (
                    value not in range(min_, max_ + 1)
                    and f'{name} must be in range {min_}...{max_}.'
            )
    )


def check_options(value: any, name: str, options: list) -> str:
    return (
                check_type(value, name, type(options[0]))
                or (
                        value not in options
                        and f'{name} must be in {options}.'
                )
        )


def check_tags(tags: str, name: str = "tags") -> str:
    if check := check_type(tags, name, str):
        return check

    try:
        next(get_posts(tags, validate=True))
    except StopIteration:
        return f'{name} "{tags}" doesn\'t match any posts.'


def check_post_id(post_id: int, name: str = "post_id") -> str:
    if name == "start_id" and get("use_last_id"):
        return ''

    if check := check_type(post_id, name, int):
        return check

    if post_id != -1 and "post" not in s.get(f"{ORIGIN}/posts/{post_id}.json").json():
        return f"Post with ID: {post_id} doesn't exist."


def check_blacklist(blacklist: list, name: str = "blacklist") -> str:
    if check := check_type(blacklist, name, list):
        return check

    for entry in blacklist:
        if check := check_type(entry, f'{name}:{ITEM} "{entry}"', str):
            return check

        if check := check_tags(entry, f'{name}:{ITEM}'):
            return check


def check_schedule(schedule: list, name: str = "schedule") -> str:
    if check := check_type(schedule, name, list):
        return check

    for time in schedule:
        if check := check_type(time, f'{name}:{ITEM} "{time}"', str):
            return check

        try:
            datetime.strptime(time, '%H:%M:%S')
        except ValueError:
            return f'{name}:{ITEM} "{time}" must be in HH:MM:SS format.'


def is_default(name: str, *, config_file: str) -> bool:
    if name == "start_id" and get("use_last_id") and get_last_id() is not None:
        return True
    return get(name, config_file=config_file) == DEFAULT[name]


VALIDATION = (
    ("peer", (str,), check_type),
    ("tags", (), check_tags),
    ("post", (('sample', 'preview', 'link'),), check_options),
    ("no_sample", (('skip', 'preview', 'link'),), check_options),
    ("use_last_id", (bool,), check_type),
    ("start_id", (), check_post_id),
    ("end_id", (), check_post_id),
    ("start_page", (1, 750), check_range),
    ("end_page", (1, 750), check_range),
    ("schedule_limit", (1, 100), check_range),
    ("blacklist", (), check_blacklist),
    ("schedule", (), check_schedule),
    ("time_tolerance", (int,), check_type),
)

if __name__ == "__main__":
    validate_config(parser.parse_args().config)
