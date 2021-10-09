from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.chrome.options import Options

class BasePage(object):
    """Base class to initialize the base page 
    that will be called from all pages
    """                         
    def __init__(self,url:str):
        self.url = url
        res = requests.get(self.url)  
        self.soup = BeautifulSoup(res.content.decode("euc-jp", "ignore"), 'html.parser')

class BasePageSelenium(object):
    def __init__(self,url:str, option=None):
        self.url = url
        options = Options()
        if option is not None:
            options.add_argument('--headless')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.get(url)
        self.driver.implicitly_wait(20)
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
    
    def close(self):
        self.driver.close()