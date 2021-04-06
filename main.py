import logging
import sys
from midway import MidwayUsa

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(" webbot")

one_day = 60 * 60 * 24


def main():
    # instantiate and run
    bot = MidwayUsa()
    bot_config = bot.get_config()

    run_time = bot_config['max retries'] * bot_config['retry time']
    if run_time > one_day:
        runstring = str(run_time / one_day) + " days "
    else:
        runstring = str(run_time / (60 * 60)) + " minutes"

    logger.info("Will run for " + runstring)

    bot.login()

    restock = bot.restock_check()

    if restock:
        if bot.price_check():

            bot.add_to_cart()

            bot.checkout()

    bot.signout()

    sys.exit(0)


if __name__ == "__main__":
    main()
