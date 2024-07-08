import os.path
from datetime import datetime, timedelta
from itertools import cycle, chain
from json import load, dump

from classes.anything import Anything

DEFAULT: dict[str: int | str | list[str | dict[str: str]]] = {
    "peer": "me",
    "tags": "order:score meme",
    "post": "preview",
    "no_sample": "skip",
    "use_last_id": False,
    "start_id": Anything(),
    "end_id": -1,
    "start_page": 1,
    "end_page": 1,
    "schedule_limit": 10,
    "blacklist": [
        "rating:e",
        "rating:q"
    ],
    "schedule": [
        "12:00:00"
    ],
    "time_tolerance": 60,
    "reversed": False
}

cached: dict[str: bool | int | str | list[str]] = {}


def get(key: str, *,
        config_path: str = "config.json") -> int | Anything | str | list[str | dict[str: str]]:
    if key == "config_path":
        return config_path
    if key not in DEFAULT:
        raise KeyError(key)
    elif key == "start_id":
        if get("use_last_id") and (last_id := get_last_id()) is not None:
            return last_id

    global cached
    if cached:
        return cached.get(key, DEFAULT[key])

    with open(config_path, "r", encoding="utf-8") as f:
        cached = load(f)
        return cached.get(key, DEFAULT[key])


def get_schedule(start_from: datetime):
    schedule: list = get("schedule").copy()
    schedule.sort()
    start_from = start_from.replace(microsecond=0)

    for i, time in enumerate(schedule):
        parsed = datetime.strptime(time, "%H:%M:%S")
        dt_time = timedelta(hours=start_from.hour, minutes=start_from.minute, seconds=start_from.second)
        pars_time = timedelta(hours=parsed.hour, minutes=parsed.minute, seconds=parsed.second)
        if pars_time - timedelta(seconds=get("time_tolerance")) > dt_time:
            break
    else:
        start_from = start_from + timedelta(days=1)
        i = 0

    start_from = start_from.replace(hour=0, minute=0, second=0)

    for time in chain(schedule[i:] + [''], cycle(schedule + [''])):
        if not time:
            start_from = start_from + timedelta(days=1)
            continue

        repl = replaced(start_from, time)
        yield repl


def replaced(dt: datetime, time: str) -> datetime:
    parsed = datetime.strptime(time, "%H:%M:%S")
    return dt.replace(hour=parsed.hour, minute=parsed.minute, second=parsed.second)


def get_last_id():
    if os.path.isfile("last_id.json"):
        with open("last_id.json", "r") as f:
            return load(f)["id"]

    return None


def set_last_id(last_id: int):
    with open("last_id.json", "w") as f:
        dump({"id": last_id}, f)
