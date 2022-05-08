from random import choice
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium import webdriver
from dotenv import dotenv_values

config = dotenv_values(".env") 

agent = UserAgent().google
 
chrome_options = Options()
chrome_options.add_argument(f"user-agent={agent}")
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

window_sizes = ['1280,800', '1650,900', '2100,1115', '1330,650'], 
chrome_options.add_argument(f"window-size={choice(window_sizes)}")

chrome_path = config['chrome_path']

driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")