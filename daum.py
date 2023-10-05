from bs4 import BeautifulSoup
import requests

import time
from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor


class Crawl():
    def __init__(self) -> None:
        #검색어 리스트

        self.search = ['리튬', '사재기', '사우디', '탈모', '세계최초',
                        '단독', 'FDA', '완전관해', '사멸', '암',
                        '매각', '인수', '독점', '상용화',
                        '경영권', '판호']
        # self.urls = [f"https://search.naver.com/search.naver?where=news&query={keyword}&sort=1&start=0" for keyword in self.search]
        self.urls = [f"https://search.daum.net/search?w=news&q={keyword}&sort=recency" for keyword in self.search]
        self.list_set = set()

    def run(self, url):
        try:
            while True:
                #selenium
                # options = webdriver.ChromeOptions()
                # options.add_argument("headless")
                # driver = webdriver.Chrome('chromedriver', chrome_options= options)
                # driver = webdriver.Chrome('chromedriver')
                # driver.get(url)
                # req = driver.page_source
                # soup = BeautifulSoup(req, 'html.parser')
                # articles = soup.select('.news_tit')
                
                #requests
                req = requests.get(url)
                soup = BeautifulSoup(req.text, 'html.parser')
                articles = soup.select('.tit_main')
                # print(daum)
                for article in articles:
                    title = article.text
                    link = article['href']
                    if link not in self.list_set:
                        self.list_set.add(link)
                        print(title, link)
                    else:
                        break
                time.sleep(30)

        except KeyboardInterrupt:
            print('\nfinish')
            pass

    def crawl(self, urls):
        pool = ThreadPoolExecutor()
        for url in self.urls:
            pool.submit(self.run, url)
    


def main():
    c = Crawl()
    c.crawl(c.urls)

if __name__ == '__main__':
    main()
