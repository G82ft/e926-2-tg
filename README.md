# e621-to-tg

Telegram userbot for scheduling image posts from [e621.net](https://e621.net).

## Table of contents
1. [Dependencies](#dependencies)
2. [Config](#config)
    1. [Default config](#default-config-1)
    2. [Arguments](#arguments)
    3. [Validating](#validating)
3. [Getting the image](#getting-the-image)
    1. [Building from source code](#building-from-source-code)
    2. [Loading exported image](#loading-exported-image)
4. [Running](#running)
5. [Scheduling](#scheduling)
6. [Blacklist](#blacklist)
7. [Logs](#logs)


## Dependencies

[Docker](https://docs.docker.com/engine/install/).

Other dependencies are handled inside docker image.


## Config

### Default config [^1]

```python
class Anything:
    def __eq__(self, _):
        return True


DEFAULT = {
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
```


### Arguments

|  Argument name   |    Type     |                         Acceptable values                          | Explanation                                                                                                                                                                     |
|:----------------:|:-----------:|:------------------------------------------------------------------:|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      `peer`      |    `str`    |                       String without spaces                        | Username of peer to whom bot will send the posts[^2]                                                                                                                            |
|      `tags`      |    `str`    |             String with valid tags separated by spaces             | String that represents a search on e621[^3]. If you want to send favourites in the order they were added, specify `fav:!{user_id}` as the only tag.                             |
|      `post`      |    `str`    |                `"sample"`, `"preview"` or `"link"`                 | Specifies format for sending posts. `"sample"` will send photo with link as caption, `"preview"` will use internal Telegram preview and `"link"` will send link without preview |
|   `no_sample`    |    `str`    |                 `"skip"`, `"preview"` or `"link"`                  | Specifies fallback option if there is no sample for this post. Same meaning as values in `post`. Will be ignored if `post` is not `"sample"`                                    |
|  `use_last_id`   |   `bool`    |                         `true` or `false`                          | Starts with the last ID from the previous planning if `true`                                                                                                                    |
|    `start_id`    |    `int`    |                    Integer representing post ID                    | Ignores all posts until this ID is encountered                                                                                                                                  |
|     `end_id`     |    `int`    |                    Integer representing post ID                    | Schedules all posts until this ID is encountered (-1 means to schedule all posts until `end_page` is reached)                                                                   |
|    `end_page`    |    `int`    |         Integer from 1 to 750[^4] representing page number         | Ignores all posts until this page is reached (not accurate, take a page before the one you want to start with, and fine-tune with `start_id`)                                   |
|   `start_page`   |    `int`    |         Integer from 1 to 750[^4] representing page number         | Schedules all posts until this page is reached (not accurate, take a page after the one you want to end with, and fine-tune with `end_id`)                                      |
| `schedule_limit` |    `int`    |                     Integer from 1 to 100 [^5]                     | Maximum numbers of scheduled messages (includes those already scheduled)                                                                                                        |
|   `blacklist`    | `list[str]` |        List of strings with valid tags separated by spaces         | Same as blacklist on [e621.net](https://e621.net/help/blacklist) with some [minor changes](#blacklist)                                                                          |
|    `schedule`    |    `str`    |            String representing time in format HH:MM:SS             | Daily posting [schedule](#scheduling)                                                                                                                                           |
| `time_tolerance` |    `int`    |        Integer from 0 to 3600*24 [^6] representing seconds         | Tolerance for detecting already scheduled posts (Telegram clients tend to use current seconds by default when scheduling)                                                       |
|    `reversed`    |   `bool`    |                         `true` or `false`                          | Reverses the posts if `true`. This significantly slow down the scheduling, since all posts must be fetched before reversing                                                     |


### Validating

You can validate config using [validator.py](/validator.py).
```shell
python3 validator.py [config]
```

## Getting the image

There are two ways to get an image:
- Build from source code
- Load exported image from the [releases page](/releases)

### Building from source code

Clone the repository:
```shell
git clone https://github.com/G82ft/e926-2-tg.git
```

Checkout e621:
```shell
git checkout -B e621 origin/e621
```

After that, [config](#config)ure the bot.

Finally, build the image:
```shell
cd e926-2-tg/
docker build . -t e621-2-tg
```

### Loading exported image

Download the image from the [releases page](/releases). To load the image use:
```shell
docker load -i e926-2-tg_v1.1.tar
```

Default config will be provided in this image. The only way to change it is to attach to the container running this image.
```shell
docker exec -it <container> ash
```

## Running

When running, you must specify [timezone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List) and phone number (without any spaces/symbols) via environment variables.
```shell
docker run -e "TZ=Europe/London" -e "PHONE=1234567890" e621-2-tg
```
Also, you can specify [LOG_LEVEL](https://docs.python.org/3.11/library/logging.html#logging-levels).


## Scheduling

Schedule is represented by a list of strings in format HH:MM:SS. After the list is exhausted, the bot switches to the next day and starts over.

The bot checks daily if the schedule limit is reached. If not, it will add posts after the last scheduled one.


## Blacklist

Blacklist is made by hand to support multiple entries. It works as one on [e621.net](https://e621.net/help/blacklist), but tag syntax differs a bit.

It supports `-` (not) operator, but does not support the `~` (or), `*` (wildcard) and `...` (range) operators. [^3]

All tags in `"tags"` can be written without any prefixes.
```json
{
    "id": 123456,
    "created_at": "...",
    "updated_at": "...",
    "tags": {
        "general": ["..."],
        "artist": ["..."],
        "copyright": ["..."],
        "character": ["..."],
        "species": ["..."],
        "invalid": ["..."],
        "meta": ["..."],
        "lore": ["..."]
    },
    "change_seq": 123456,
    "rating": "s",
    "fav_count": 123456,
    "approver_id": 123456,
    "uploader_id": 123456,
    "description": "...",
    "comment_count": 123456,
    "has_notes": false
}
```

Post-related tags like `rating` must be written like this:
```json
{
    "blacklist": [
        "key:value"
    ]
}
```

For example:
```json
{
    "blacklist": [
        "-id:123456 fav_count:123456",
        "approver_id:123456"
    ]
}
```


## Logs

Logs are stored in `app/logs/`. There are two files:
- `logs.csv` - contains all logs.
- `no_sample.log` - contains posts without sample. It will log all posts without sample no matter what you specify in `no_sample` config field (if you have specified to send posts with samples).


---
[^1]: The configuration presented is written in Python, but the configuration file [config.json](/config.json) is in JSON format.

    Differences between Python code and JSON format:
    - You can't use Anything() in JSON
    - Bool literals (True, False) are written in lowercase (true, false) in JSON
[^2]: [`resolve_peer()` — Pyrogram documentation](https://docs.pyrogram.org/api/methods/resolve_peer) 
[^3]: [e621 search cheatsheet](https://e621.net/help/cheatsheet)
[^4]: [e621 limits](https://e621.net/help/api#posts_list)
[^5]: [Telegram limits](https://limits.tginfo.me/)
[^6]: [`datetime` — Python 3.11 documentation](https://docs.python.org/3.11/library/datetime.html#timedelta-objects)
