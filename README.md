# e926-to-tg

Telegram userbot for scheduling image posts from [e926.net](https://e926.net).


## Table of contents
1. [Dependencies](#dependencies)
2. [Config](#config)
   1. [Default config](#default-config-1)
   2. [Arguments](#arguments)
   3. [Validating](#validating)
3. [Running](#running)
4. [Scheduling](#scheduling)
5. [Blacklist](#blacklist)


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
    "time_tolerance": 60
}
```


### Arguments

|  Argument name   |    Type     |                  Acceptable values                  | Explanation                                                                                                                                                                      |
|:----------------:|:-----------:|:---------------------------------------------------:|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|      `peer`      |    `str`    |                String without spaces                | Username of peer to whom bot will send the posts                                                                                                                                 |
|      `tags`      |    `str`    |     String with valid tags separated by spaces      | String that represents a search on e926[^2]. If you want to send favourites in the order they were added, specify `fav:!{user_id}` as the only tag.                              |
|      `post`      |    `str`    |         `"sample"`, `"preview"` or `"link"`         | Specifies format for sending posts. `"sample"` will send photo with link as caption, `"preview"` will use internal Telegram preview, and `"link"` will send link without preview |
|   `no_sample`    |    `str`    |          `"skip"`, `"preview"` or `"link"`          | Specifies fallback option if there is no sample for this post. Same meaning as values in `post`                                                                                  |
|  `use_last_id`   |   `bool`    |                  `true` or `false`                  | Starts with the last ID from the previous planning                                                                                                                               |
|    `start_id`    |    `int`    |            Integer representing post ID             | Ignores all posts until this ID is encountered                                                                                                                                   |
|     `end_id`     |    `int`    |            Integer representing post ID             | Schedules all posts until this ID is encountered                                                                                                                                 |
|   `start_page`   |    `int`    | Integer from 1 to 750[^3] representing page number  | Ignores all posts until this page is reached (not accurate, take a page before the one you want to start with, and fine-tune with `start_id`)                                    |
|   `start_page`   |    `int`    | Integer from 1 to 750[^3] representing page number  | Schedules all posts until this page is reached (not accurate, take a page after the one you want to end with, and fine-tune with `end_id`)                                       |
| `schedule_limit` |    `int`    |             Integer from 1 to 100 [^4]              | Maximum numbers of scheduled messages (includes those already scheduled)                                                                                                         |
|   `blacklist`    | `list[str]` | List of strings with valid tags separated by spaces | Same as blacklist on [e926.net](https://e926.net/help/blacklist) with some [minor changes](#blacklist)                                                                           |
|    `schedule`    |    `str`    |     String representing time in format HH:MM:SS     | Daily posting [schedule](#scheduling)                                                                                                                                            |
| `time_tolerance` |    `int`    | Integer from 0 to 3600*24 [^5] representing seconds | Tolerance for detecting already scheduled posts (Telegram clients tend to use current seconds by default when scheduling)                                                        |


### Validating

You can validate config using [validator.py](/validator.py).
```shell
python3 validator.py [config]
```


## Running

You must change [`config.json`](/config.json) ***before*** you build the image!
```shell
cd e926-2-tg/
docker build . -t e926-2-tg
```

When running, you must specify [timezone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List) and phone number (without any spaces/symbols) via environment variables.
```shell
docker run --rm -e "TZ=Europe/London" -e "PHONE=1234567890" e926-2-tg
```
Also, you can specify [LOG_LEVEL](https://docs.python.org/3.11/library/logging.html#logging-levels).


## Scheduling

Schedule is represented by a list of strings in format HH:MM:SS. After the list is exhausted, the bot switches to the next day and starts over.

The bot checks daily if the schedule limit is reached. If not, it will add posts after the last scheduled one.


## Blacklist

Blacklist is made by hand to support multiple entries. It works as one on [e926.net](https://e926.net/help/blacklist), but tag syntax differs a bit.

It supports `-` (not) operator, but does not support the `~` (or), `*` (wildcard) and `...` (range) operators. [^2]

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



---
[^1]: The configuration presented is written in Python, but the configuration file [config.json](/config.json) is in JSON format. You can't use Anything() in JSON
[^2]: [e926 search cheatsheet](https://e926.net/help/cheatsheet)
[^3]: [e926 limits](https://e926.net/help/api#posts_list)
[^4]: [Telegram limits](https://limits.tginfo.me/)
[^5]: [`datetime` — Python 3.11 documentation](https://docs.python.org/3.11/library/datetime.html#timedelta-objects)
