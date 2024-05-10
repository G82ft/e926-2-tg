from argparse import ArgumentParser

# Unfortunately this file is not used :(

parser: ArgumentParser = ArgumentParser(
    "e926-2-tg-bot",
    description="Telegram bot for scheduling image posts from e926.",
    epilog="https://github.com/G82ft/e926-2-tg",
)

parser.add_argument(
    "config",
    nargs="?",
    default="config.json"
)
parser.add_argument("--peer", "-p")
parser.add_argument("--tags", "-t")
parser.add_argument("--start_id", type=int)
parser.add_argument("--use-last-id", "--last", type=bool, default=True)
parser.add_argument("--end_id", type=int)
parser.add_argument("--start_page", "--start", "-s", type=int)
parser.add_argument("--end_page", "--end", "-e", type=int)
parser.add_argument("--schedule_limit", "--limit", "-l", type=int)
parser.add_argument("--time_tolerance", "--tolerance", type=int)
parser.add_argument("--blacklist", "--bl", "-b", nargs="*")

args = parser.parse_args()
