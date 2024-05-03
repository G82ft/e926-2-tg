from bot import bot, main
from validator import validate_config

validate_config()

bot.run(main())
