from bs4 import BeautifulSoup
import requests

import time
from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


class Crawl():
    def __init__(self) -> None:
        #검색어 리스트
        self.search = ['리튬', '사재기', '사우디', '탈모', '세계최초',
                        '단독', 'FDA', '완전관해', '사멸', '암',
                        '매각', '인수', '독점', '상용화',
                        '경영권', '판호']
        # self.urls = [f"https://search.naver.com/search.naver?where=news&query={keyword}&sort=1&start=0" for keyword in self.search]
        self.urls = [f"https://search.daum.net/search?w=news&q={keyword}&sort=recency" for keyword in self.search]
        # self.urls.extend(self.daum)
        self.list_set = set()

    def run(self, url):
        try:
            while True:
                #selenium
                options = webdriver.ChromeOptions()
                options.add_argument("headless")
                driver = webdriver.Chrome('chromedriver', options=options)
                driver.get(url)
                req = driver.page_source
                soup = BeautifulSoup(req, 'html.parser')
                # articles = soup.select('.news_tit')
                articles = soup.select('.tit_main')
                
                #requests
                # req = requests.get(url)
                # soup = BeautifulSoup(req.text, 'html.parser')
                # articles = soup.select('.tit_main')
                # if 'naver' in url:
                #     articles = soup.select('.news_tit')
                # elif 'daum' in url:
                #     articles = soup.select('.tit_main')
                for article in articles:
                    title = article.text
                    link = article['href']
                    if title not in self.list_set:
                        self.list_set.add(title)
                        print(title, link)
                    else:
                        break
                time.sleep(5)

        except KeyboardInterrupt:
            print('\nfinish')
            pass

    def crawl(self):
        pool = ThreadPoolExecutor(max_workers = 32)
        for url in self.urls:
            pool.submit(self.run, url)
    


def main():
    c = Crawl()
    c.crawl()
    
if __name__ == '__main__':
    main()
