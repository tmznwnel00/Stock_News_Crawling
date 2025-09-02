from bs4 import BeautifulSoup
import requests

import time
from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


class Crawl():
    def __init__(self) -> None:
        #검색어 리스트
        self.search = ['승인']
        # self.urls = [f"https://search.naver.com/search.naver?where=news&query={keyword}&sort=1&start=0" for keyword in self.search]
        self.urls = [f"https://search.daum.net/search?w=news&q={keyword}&sort=recency" for keyword in self.search]
        # self.urls.extend(self.daum)
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
                header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46'}
                req = requests.get(url, headers = header)
                if 'captcha.search.daum.net' in req.text:
                    print(req.text)
                else:
                    soup = BeautifulSoup(req.text, 'html.parser')
                    articles = soup.select('.tit-g')
                    # if 'naver' in url:
                    #     articles = soup.select('.news_tit')
                    # elif 'daum' in url:
                    #     articles = soup.select('.tit_main')
                    for article in articles:
                        article_find = article.find('a')
                        title = article_find.text
                        link = article_find['href']
                        if title not in self.list_set:
                            self.list_set.add(title)
                            print(title, link)
                        else:
                            break
                time.sleep(10)

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
