from selenium.webdriver.remote.webdriver import WebDriver
from bs4 import BeautifulSoup

class BasePage(object):
    """Base class to initialize the base page 
    that will be called from all pages
    """                         
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.driver.implicitly_wait(10)
        self.soup = BeautifulSoup(driver.page_source, 'html.parser')