from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from bs4 import BeautifulSoup
import requests

class BasePage(object):
    """Base class to initialize the base page 
    that will be called from all pages
    """                         
    def __init__(self,url:str):
        self.url = url
        res = requests.get(self.url)
        res.encoding = res.apparent_encoding  
        text = res.content
        self.soup = BeautifulSoup(text, 'html.parser')

class BasePageSelenium(object):
    def __init__(self,url:str):
        self.url = url
        self.driver = webdriver.Chrome()
        self.driver.get(url)
        self.driver.implicitly_wait(20)
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
    
    def close(self):
        self.driver.close()