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
                     "https://www.etnews.com/news/section.html",
                     "https://www.newspim.com/news/lists?category_cd=1",
                     "https://www.newsprime.co.kr/news/section_list_all/?sec_no=56",
                     "https://www.newsprime.co.kr/news/section_list_all/?sec_no=57"]
        self.url = "https://www.newsprime.co.kr/news/section_list_all/?sec_no=57"
        
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

    def parse_newspim_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('article.thumb_h')

        for article in articles:
            title_tag = article.select_one("strong.subject a")
            title = title_tag.get_text(strip=True)
            link = f"https://www.newspim.com/{title_tag["href"]}"

            date_tag = article.select_one("span.date")
            date = date_tag.get_text(strip=True)
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break

            
    def parse_newsprime_news1(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*',
                  'Cookie': 'csrf_cookie_name=c4750f901e0aba407d4529a3492a27c3; TRACKER_MYLOG1=Mon%2C%2008%20Sep%202025%2004%3A02%3A56%20GMT; _fwb=34nsXtTmtiDC6WvsGUlcA.1757304176559; SID=d64f8fdbb8eea30391ffa229971eb859; _ga=GA1.1.624392975.1757304177; wcs_bt=ad0380f89be1f8:1757304797; _ga_BPMKJNZW0V=GS2.1.s1757304177$o1$g1$t1757304798$j1$l0$h0'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('td.news1')
        
        for article in articles:
            title_tag = article.select_one("a")
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]

            parent = article.find_parent("tr").find_next_sibling("tr")
            date_span = parent.select_one("span.font11blue2") if parent else None
            text = date_span.get_text(strip=True)
            date = text.split("]")[-1].strip() if "]" in text else text
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break
            
    def parse_newsprime_news2(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*',
                  'Cookie': 'csrf_cookie_name=c4750f901e0aba407d4529a3492a27c3; TRACKER_MYLOG1=Mon%2C%2008%20Sep%202025%2004%3A02%3A56%20GMT; _fwb=34nsXtTmtiDC6WvsGUlcA.1757304176559; SID=d64f8fdbb8eea30391ffa229971eb859; _ga=GA1.1.624392975.1757304177; wcs_bt=ad0380f89be1f8:1757304797; _ga_BPMKJNZW0V=GS2.1.s1757304177$o1$g1$t1757304798$j1$l0$h0'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('td.news1')
        
        for article in articles:
            title_tag = article.select_one("a")
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]

            parent = article.find_parent("tr").find_next_sibling("tr")
            date_span = parent.select_one("span.font11blue2") if parent else None
            text = date_span.get_text(strip=True)
            date = text.split("]")[-1].strip() if "]" in text else text
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
                elif "newspim" in url:
                    self.parse_newspim_news(url)
                elif "newsprime" in url and "sec_no=56" in url:
                    self.parse_newsprime_news1(url)
                elif "newsprime" in url and "sec_no=57" in url:
                    self.parse_newsprime_news2(url)
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
