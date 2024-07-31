from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import requests
import numpy as np
import re
import pandas as pd



# Set up the WebDriver (e.g., Chrome)
driver = webdriver.Chrome()

# Go to the URL
url = 'https://www.goodreads.com/list/show/1.Best_Books_Ever'
driver.get(url)

# Optionally, wait for the page to fully load (especially if it has dynamic content)
time.sleep(5)

# Get the page source and parse it with BeautifulSoup
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')

# Close the WebDriver
driver.quit()

# Print or process the soup as needed
print(soup.prettify())
