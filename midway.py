from bot import Bot
import time
from re import sub
from decimal import Decimal

import logging

smtp_server = "smtp.gmail.com"
port = 465
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(" midwayusa")


# the midwayusa.com implementation of the basic bot
class MidwayUsa(Bot):
    retry_count = 0

    def __init__(self):
        Bot.__init__(self)

    def login(self):
        self.web.go_to(self.config['login_url'])
        time.sleep(0.5)
        self.web.type(self.config['email'], into='Email')
        self.web.click('Continue', tag='span')
        self.web.type(self.config['password'], into='Password', id='Password')
        self.web.click('Sign In', id='signInButton')  # you are logged in . woohoooo

    def signout(self):
        self.web.click('Account', css_selector=".header-account-icon")
        self.web.click('Sign Out', css_selector=".fakeLinks")

    def search(self, product):
        self.web.type(product, into="Search")
        self.web.press(self.web.Key.ENTER)
        results = self.web.find_elements(classname="product-finding-container")
        logger.info("Found " + results)

    def restock_check(self):
        while self.retry_count < self.config['max retries']:
            self.web.go_to(self.config['url'])
            if (self.check_for_available()):
                return True
            else:
                self.retry_count += 1
                logger.info("Product Unavailable retry_count: " + str(self.retry_count))
                time.sleep(self.config['retry time'])

        # max retries
        logger.info("Max Retries exceeded")
        return False

    def check_for_available(self):
        try:
            available = self.web.find_elements(tag='button',
                                               xpath='/html/body/div[1]/div[2]/div[2]/div[2]/div[4]/div[2]/div/'
                                                     'div[''1]/div[2]/mw-modal-trigger/button/span')
            if len(available) > 1:
                for item in available:
                    if item.text == "Temporarily unavailable":
                        return False
                    if item.text == "Available":
                        return True
            else:
                return False
        except Exception as e:
            logger.error("check_for_available exception: " + str(e))
            return False
        return False

    def add_to_cart(self):
        cart_button = self.web.find_elements(text='Add to cart', xpath="//*[contains(text(),'add-to-cart-button')]")
        # look for temporarily unavailable
        for item in cart_button:
            if item.text == 'Temporarily unavailable':
                logger.error("not in yet")
                return False
            if item.text == 'Add to Cart':
                logger.info("Adding to Cart")
                # self.web.click(text="Add to Cart", xpath='//*[@id="l-product"]/div[2]/div[4]/div[2]/div/div[3]/form/button')
                self.web.click(text="Add to Cart")
                time.sleep(0.5)
                self.web.click(text="Go to Cart", xpath='//*[@id="cart-intercept-main"]/div[3]/a')
                # self.web.click("Go to Cart")
                # self.web.click("Begin Checkout")
                # self.web.click("Select Visa-1122")
                return True

    def get_price(self):

        current_price = self.web.find_elements(text="Our Price",
                                               xpath='//*[@id="product-item-information"]/div[1]/div[2]')
        # current_price = self.web.find_elements(text="Our Price", xpath="//*[contains(text(),'priceblock')]",
        #                                      classname="active-price")
        if len(current_price) > 0:
            if current_price[0].text.count('$') > 1:
                # multiple prices - last one is the actual price
                start = current_price[0].text.rfind('$')
                listed_price = current_price[0].text[start:]
                item_value = Decimal(sub(r'[^\d.]', '', listed_price))
            else:
                ps = current_price[0].text.split('\n')
                listed_price = ps[1]
                item_value = Decimal(sub(r'[^\d.]', '', listed_price))
            # convert the $ XX.XX to a number
            logger.info("Found Price is: " + str(item_value))
            return item_value
        else:
            return -1

    def checkout(self):
        self.web.click(text="Begin Checkout")
        self.web.click(text="Continue", xpath='//*[@id="mainContent"]/div/div[3]/div[7]/form/button')
        self.web.click(text="Place Order",
                       xpath='//*[@id="mainContent"]/aside/div[2]/button')
