import os.path
from datetime import datetime, timedelta
from itertools import cycle
from json import load, dump

from classes.anything import Anything
from classes.next import Next

DEFAULT: dict[str: int | str | list[str | dict[str: str]]] = {
    "peer": "me",
    "tags": "order:score meme",
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
    "time_tolerance": 60
}

cached: dict[str: int | str | list[str | dict[str: str]]] = {}


def get(key: str, *,
        config_file: str = "config.json") -> int | Next | Anything | str | list[str | dict[str: str]]:
    if key not in DEFAULT:
        raise KeyError(key)
    elif key == "start_id":
        if get("use_last_id") and (last_id := get_last_id()):
            return last_id

    global cached
    if cached:
        return cached.get(key, DEFAULT[key])

    with open(config_file, "r", encoding="utf-8") as f:
        cached = load(f)
        return cached.get(key, DEFAULT[key])


def get_schedule(dt: datetime):
    dt = dt.replace(microsecond=0)

    for time in cycle(get("schedule") + [""]):
        if not time:
            dt = dt.replace(day=dt.day+1, hour=0, minute=0, second=0)
            continue

        parsed = datetime.strptime(time, "%H:%M:%S")
        replaced = dt.replace(hour=parsed.hour, minute=parsed.minute, second=parsed.second)
        if replaced - timedelta(seconds=get("time_tolerance")) < dt:
            continue
        yield replaced


def get_last_id():
    if os.path.isfile("last_id.json"):
        with open("last_id.json", "r") as f:
            return Next(load(f)["id"])

    return None


def set_last_id(last_id: int):
    with open("last_id.json", "w") as f:
        dump({"id": last_id}, f)
