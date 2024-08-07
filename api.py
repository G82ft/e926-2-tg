from time import sleep
from unittest import TestCase
from urllib.parse import quote_plus

import requests

import config
from logs import get_logger

s = requests.Session()
s.headers["user-agent"] = "e926-2-tg-bot/test (by G82ft)"

ORIGIN: str = "https://e926.net"
DEFAULT_LIMIT: int = 75
LIMIT: int = 320

logger = get_logger(__name__)


def get_posts(tags: str, validate: bool = False):
    posts: list

    start = (config.get("start_page") * DEFAULT_LIMIT // LIMIT) or 1
    end = config.get("end_page") * DEFAULT_LIMIT // LIMIT + 2  # +1 for range and +1 for floor

    logger.debug(f'Getting posts from page {start} to {end - 1}...')

    started: bool = validate

    for page in range(start, end):
        if tags.startswith("fav:!") and " " not in tags:
            url = f'{ORIGIN}/favorites.json?user_id={tags.split("!")[1]}&page={page}&limit={LIMIT}'
        else:
            url = f'{ORIGIN}/posts.json?tags={quote_plus(tags)}&page={page}&limit={LIMIT}'
        logger.debug(url)
        sleep(0.5)  # Rate limit (https://e926.net/help/api; Basic concepts > Rate limiting)

        if "posts" not in (res := s.get(url).json()):
            logger.error(f'Failed to get posts: {res}')
            return
        posts = res["posts"]
        if not posts:
            logger.warning(f'No posts found with tags "{tags}"')
            return

        for post in posts:
            if not started and config.get("start_id") != post["id"]:
                continue

            started = True
            if not is_blacklisted(post, config.get("blacklist")) or validate:
                yield f'{ORIGIN}/posts/{post["id"]}'
            else:
                logger.debug(f'Blacklisted: {post["id"]}')

            if config.get("end_id") == post["id"]:
                logger.info(f'End reached: {post["id"]}')
                return


def is_blacklisted(post: dict, blacklist: list[str]) -> bool:
    return any(is_match(post, entry) for entry in blacklist)


def is_match(post: dict, entry: str) -> bool:
    tags: tuple[str] = get_tags(post)

    results: list[bool] = []
    for tag in entry.split():
        tag: str

        invert: bool = False
        if tag.startswith('-'):
            tag = tag[1:]
            invert = True

        result: bool = tag in tags
        if ":" in tag:
            key, value = tag.split(":")
            if key not in post:
                raise KeyError(key)
            result = type(post[key])(value) == post[key]

        result = invert ^ result

        results.append(result)

    return all(results) and bool(results)


def get_tags(post: dict) -> tuple[str]:
    tags: dict[str: list] = post["tags"]
    return tuple(
        tags["general"] + tags["artist"]
        + tags["copyright"] + tags["character"]
        + tags["species"]
        + tags["meta"] + tags["lore"]
    )


class Test(TestCase):
    post: dict = {
        'id': 0,
        'tags': {
            'general': ['anthro', 'collar', 'duo', 'fluffy', 'fur', 'happy', 'tail', 'white_body', 'white_fur'],
            'artist': ['3rdperson_iz'],
            'copyright': [],
            'character': [],
            'species': ['canid', 'canine', 'fox', 'mammal'],
            'meta': ['colored', 'portrait'],
            'lore': []

        },
        'rating': 's'
    }

    def test_is_match(self):
        post = self.post.copy()
        # Basic check
        self.assertTrue(is_match(post, "fox"))
        self.assertFalse(is_match(post, "dog"))

        # Multiple tags
        self.assertTrue(is_match(post, "fox fluffy"))
        self.assertFalse(is_match(post, "fox angiewolf"))

        # Negative tags
        self.assertTrue(is_match(post, "-dog"))
        self.assertFalse(is_match(post, "-fox"))

        # Multiple tags + negative tags
        self.assertTrue(is_match(post, "fox -female"))
        self.assertFalse(is_match(post, "female -fluffy"))

    def test_is_blacklisted(self):
        post = self.post.copy()

        self.assertFalse(is_blacklisted(
            post, []
        ))
        self.assertTrue(is_blacklisted(
            post,
            [
                "fox",
                "fox fluffy",
                "-dog",
                "fox -female"
            ]
        ))
        self.assertFalse(is_blacklisted(
            post,
            [
                "dog",
                "fox angiewolf",
                "-fox",
                "female -fluffy"
            ]
        ))
