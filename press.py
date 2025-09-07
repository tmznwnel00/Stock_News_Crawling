from bs4 import BeautifulSoup
import requests

import time
from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


class Crawl():
    def __init__(self) -> None:
        self.urls = ["https://www.infostockdaily.co.kr/news/articleList.html?sc_section_code=S1N17&view_type=sm",
                     "https://www.thebell.co.kr/free/content/Article.asp?svccode=00",
                     "https://www.thelec.kr/news/articleList.html",
                     "https://zdnet.co.kr/news/?lstcode=0000&page=1",
                     "https://dealsite.co.kr/newsflash/",
                     "https://www.pharmnews.com/news/articleList.html?view_type=sm",
                     "https://www.etnews.com/news/section.html"]
        self.url = "https://www.infostockdaily.co.kr/news/articleList.html?sc_section_code=S1N17&view_type=sm"
        
        self.list_set = set()

    def parse_info_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header, verify=False)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('.list-block')
        
        for article in articles:
            div = article.find('div', class_='list-titles')
            title = div.find('strong').text
            link = f"https://www.infostockdaily.co.kr{div.find('a')['href']}"
            dated_div = article.select_one("div.list-dated")
            text = dated_div.get_text(strip=True).split("|")[-1].strip()
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, text)
            else:
                break
                
    def parse_thebell_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('div.listBox ul li')
        for article in articles:
            article_find = article.find('a')
            title = article_find["title"]
            link = f"https://www.thebell.co.kr/free/content/{article_find['href']}"
            date_span = article.select_one("dd.userBox span.date")
            raw_date = date_span.get_text(strip=True)
            date_str = raw_date.replace("오전", "AM").replace("오후", "PM")
            from datetime import datetime
            dt = datetime.strptime(date_str, "%Y-%m-%d %p %I:%M:%S")
            date = dt.strftime("%Y/%m/%d %H:%M:%S")
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break

    def parse_etnews_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('ul.news_list li')
        
        for article in articles:
            title_tag = article.select_one("strong a")
            title = title_tag.text.strip() 
            link = "https://www.etnews.com" + title_tag['href'] if title_tag else ""
            date_tag = article.select_one("div.flex span.date")
            date = date_tag.text.strip() if date_tag else ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break

    def parse_thelec_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('section.article-list-content.text-left > .table-row')

        for article in articles:
            a_tag = article.find('a', class_='links')
            title = a_tag.find('strong').text.strip()
            link = f"https://www.thelec.kr{a_tag['href']}"


            date_div = article.select_one("div.list-dated")
            text = date_div.get_text(strip=True).split("|")[1].strip()
            
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, text)
            else:
                break

    def parse_zdnet_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('div.news_box > .newsPost')
        
        for article in articles:
            a_tag = article.find('div', class_='assetText').find('a', href=True)
            title_tag = a_tag.find('h3')

            title = title_tag.text.strip() 
            link = f"https://zdnet.co.kr{a_tag['href']}"
            date_span = soup.select_one("p.byline span")
            raw_date = date_span.text.strip() if date_span else ""
            date_split = raw_date.split(" ")
            date = f"{date_split[0]} {date_split[2]}"
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break
    
    def parse_yakup_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        print(soup)
        articles = soup.select('div.list_con ul li')
        print(len(articles))
        
        for article in articles:
            a_tag = article.find('div', class_='assetText').find('a', href=True)
            title_tag = a_tag.find('h3')

            title = title_tag.text.strip() 
            link = f"https://zdnet.co.kr{a_tag['href']}"
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link)
            else:
                break

    def parse_dealsite_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('li[id^=article_]')

        for article in articles:
            a_tag = article.select_one("a.title")
            title = a_tag.text.strip() 
            link = "https://dealsite.co.kr" + a_tag['href'] 
            time_tag = article.select_one("span.pub-date")
            pub_time = time_tag.text.strip() if time_tag else ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, pub_time)
            else:
                break

    def parse_pharmnews_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('section#section-list ul.type li')

        for article in articles:
            title_tag = article.select_one("h4.titles a")
            title = title_tag.text.strip() 
            link = "https://www.pharmnews.com" + title_tag['href'] 
            date_tag = article.select_one("span.byline em.date")
            date = date_tag.text.strip() if date_tag else ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break
    
    
    def run(self, url):
        try:
            while True:
                #requests
                if "infostockdaily" in url:
                    self.parse_info_news(url)     
                elif "thebell" in url:
                    self.parse_thebell_news(url)
                elif "etnews" in url:
                    self.parse_etnews_news(url)
                elif "thelec" in url:
                    self.parse_thelec_news(url)
                elif "zdnet" in url:
                    self.parse_zdnet_news(url)
                elif "yakup" in url:
                    self.parse_yakup_news(url)
                elif "dealsite" in url:
                    self.parse_dealsite_news(url)
                elif "pharmnews" in url:
                    self.parse_pharmnews_news(url)
                time.sleep(60)
        except KeyboardInterrupt:
            print('\nfinish')
            pass

    def crawl(self):
        pool = ThreadPoolExecutor(max_workers = 7)
        # for url in self.urls:
        #     pool.submit(self.run, url)
        pool.submit(self.run, self.url)
    


def main():
    c = Crawl()
    c.crawl()
    
if __name__ == '__main__':
    main()
