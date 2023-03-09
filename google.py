from bs4 import BeautifulSoup
import requests
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

#웹드라이버 설정
# options = webdriver.ChromeOptions()
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option("useAutomationExtension", False)



    

#검색어 입력
search = input("검색할 키워드를 입력해주세요:")
# url = "https://search.naver.com/search.naver?where=news&query=" + search + '&sort=1' + "&start=0"


# with selenium
# options = webdriver.ChromeOptions()
# options.add_argument("headless")

# driver = webdriver.Chrome('chromedriver', chrome_options= options)
# driver.get(url)
# req = driver.page_source
# soup = BeautifulSoup(req, 'html.parser')

# with requests
req = requests.get(url)
soup = BeautifulSoup(req.text, 'html.parser')


articles = soup.select('.news_tit')
for article in articles:
    title = article.text
    # url = article.attrs['href']
    url = '<a href=\"' + url + '\">' + url + '</a>'
    # print(title, url)

# driver.quit()
Z