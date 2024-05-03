from bot import bot, main
from logs import get_logger
from validator import validate_config

logger = get_logger(__name__)

validate_config()

logger.info("Starting bot...")

bot.run(main())
