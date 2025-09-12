from bs4 import BeautifulSoup
import requests

import time
from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


class Crawl():
    def __init__(self) -> None:
        #검색어 리스트
        # self.search = ['리튬', '사재기',  '탈모', '세계최초','AI','당뇨','광산개발','자율주행','중입자','치매','데이터센터','딥페이크','게임체인저','비만','대선정책',
        #                 '단독', 'FDA', '완전관해', '사멸', '암','핵심원료','현대투자','초전도체','테슬라',
        #                 '매각', '인수', '독점', '상용화','딥시크',
        #                 '경영권분쟁', '인공지능', '이차전지', '로봇','MOU','신약','양자',
        #                '삼성투자', '국내최초', '의무화', 'm&a','전기차화재',
        #                '개발성공','엔비디아','재건','개발']
        self.search = ["리튬"]
        self.urls = [f"https://search.naver.com/search.naver?where=news&query={keyword}&sort=1&start=0" for keyword in self.search]
        self.list_set = set()

    def run(self, url):
        try:
            while True:
                #requests
                header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
                req = requests.get(url, headers = header)
                soup = BeautifulSoup(req.text, 'html.parser')
                articles = soup.select('.sds-comps-vertical-layout.sds-comps-full-layout.fds-news-item-list-tab > div')

                for article in articles:
                    
                    a_tag = article.select_one("a:has(span.sds-comps-text-type-headline1)")

                    title = a_tag.get_text(strip=True)
                    link = a_tag["href"]
                    if link not in self.list_set:
                        self.list_set.add(link)
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
