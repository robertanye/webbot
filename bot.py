import time
from abc import abstractmethod, ABCMeta
from re import sub
from decimal import Decimal
import smtplib
import ssl

from webbot import Browser
import logging
import json

smtp_server = "smtp.gmail.com"
port = 465
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(" webbot")


class Bot:
    __metaclass__ = ABCMeta
    web = None

    def __init__(self):
        with open("config.json") as json_file:
            self.config = json.load(json_file)
            logger.info("email " + self.config['email'])
            logger.info("password  " + self.config['password'])
            logger.info("url  " + self.config['url'])
            logger.info("max price " + str(self.config['max price']))
        self.web = Browser()

    def send_email(self, subject, body):
        message = """ 
        Subject: CCI Primers Available
        
        Found CCI Primers
        
        """
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(self.config['email'], self.config['email_pwd'])
            server.sendmail(self.config['email'], self.config['email'], message)

    @abstractmethod
    def restock_check(self):
        """
        This method should be defined in a derived class as it
        is different for different sites
        :return:
        """
    @abstractmethod
    def checkout(self):
        """
        This method should be defined in a derived class as it is
        is different for different sites
        :return:
        """


    @abstractmethod
    def signout(self):
        """
        only defined in the derived class
        :return:
        """

    def search(self, product):
        self.web.type(product, into="Search")
        self.web.press(self.web.Key.ENTER)
        results = self.web.find_elements(classname="product-finding-container")
        logger.info("Found " + results)

    @abstractmethod
    def check_for_available(self):
        """
        only defined in the derived class
        :return:
        """

    @abstractmethod
    def checkout(self):
        '''

        '''
        # finish the buy

    @abstractmethod
    def add_to_cart(self):
        """
        only defined in the derived class
        :return:
        """

    def price_check(self):
        price = self.get_price()
        if price == -1:
            return False

        if price <= self.config['max price']:
            return True
        else:
            return False

    @abstractmethod
    def get_price(self):
        """
        only defined in the derived class
        :return:
        """
    def get_config(self):
        return self.config

