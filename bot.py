from re import sub
from decimal import Decimal


from webbot import Browser
import logging
import json
import sys

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(" webbot")

def login(config):
    web.type(config['email'], into='Email')
    web.click('Continue', tag='span')
    web.type(config['password'], into='Password', id='passwordFieldId')
    web.click('Sign In', id='signInButton')  # you are logged in . woohoooo

def search( product ):
    web.type(product, into="Search")
    web.press(web.Key.ENTER)
    results = web.find_elements(classname="product-finding-container")
    logger.debug("Found " + results)

def add_to_cart():
    cart_button = web.find_elements(xpath="//*[contains(text(),'add-to-cart-button')]")
    # look for temporarily unavailable
    for item in cart_button:
        if item.text == 'Temporarily unavailable':
            logger.error("not in yet")
            return False
        if item.text == 'Add to Cart':
            logger.info("Adding to Cart")
            web.press(web.Key.Enter, into=item)
            return True

    logger.debug("Cart is " + cart_button )

def get_price():
    current_price = web.find_elements(text="Our Price", xpath="//*[contains(text(),'priceblock')]", classname="active-price" )
    if len(current_price) > 0:
        ps = current_price[0].text.split('\n')
        listed_price = ps[1]
        logger.debug("Found Price is: " + listed_price)
        # convert the $ XX.XX to a number
        item_value = Decimal(sub(r'[^\d.]', '', listed_price))
        return item_value
    else:
        return -1

def load_configs():
    with open("config.json") as json_file:
        config = json.load(json_file)
        logger.debug("email " + config['email'])
        logger.debug("password  " + config['password'])
        logger.debug("url  " + config['url'])
        logger.debug("max price " + str(config['max price']))
    return config



bot_config = load_configs()

web = Browser()
try:
    web.go_to('midwayusa.com/account/authentication')

    login(bot_config)
    web.go_to(bot_config['url'])
    #search('CCI large pistol primer')

    price = get_price()
    if price == -1:
        sys.exit(1)
    if price <= bot_config['max price']:
        add_to_cart()
    web.close_current_tab()
except( RuntimeError, TypeError, NameError):
    logger.error("Took exception: ")