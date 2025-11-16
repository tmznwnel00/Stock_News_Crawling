from bs4 import BeautifulSoup
from datetime import datetime
import re
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
                     "https://www.newsprime.co.kr/news/section_list_all/?sec_no=57",
                     "https://www.finance-scope.com/article/list/scp_SC007000000",
                     "https://www.hankyung.com/press-release",
                     "https://www.pointe.co.kr/news/articleList.html?sc_section_code=S1N13&view_type=sm",
                     "https://www.dt.co.kr/economy/general",
                     "https://www.biotimes.co.kr/news/articleList.html",
                     "https://www.pinpointnews.co.kr/news/articleList.html?sc_section_code=S1N4&view_type=sm",
                     "https://www.kdfnews.com/news/articleList.html?view_type=sm",
                     "https://gamefocus.co.kr/html_file.php?file=normal_all_news.html",
                     "https://www.newsis.com/world/list/?cid=10100&scid=10101",
                     "https://www.newsis.com/money/list/?cid=15000&scid=15001",
                     "https://www.newsis.com/economy/list/?cid=10400&scid=10401",
                     "https://www.newsis.com/business/list/?cid=13000&scid=13001",
                     "https://www.epnc.co.kr/news/articleList.html?view_type=sm",
                     "https://www.businesspost.co.kr/BP?command=sub&sub=2",
                     "https://signalm.sedaily.com/Main/Content/HeadLine?NClass=AL",
                     "https://www.ebn.co.kr/news/articleList.html?view_type=sm",
                     "http://www.bosa.co.kr/news/articleList.html?view_type=sm",
                     "http://www.press9.kr/news/articleList.html?sc_section_code=S1N12&view_type=sm",
                     "http://www.press9.kr/news/articleList.html?sc_section_code=S1N14&view_type=sm",
                     "https://www.medisobizanews.com/news/articleList.html?view_type=sm",
                     "https://www.g-enews.com/list.php?ct=g000000",
                     "https://www.autodaily.co.kr/news/articleList.html",
                     "https://economist.co.kr/article/list/ecn_SC011000000",
                     "https://www.medisobizanews.com/news/articleList.html?view_type=sm",
                     "https://news.naver.com/section/101",
                     "https://www.theguru.co.kr/news/article_list_all.html",
                     "https://www.yakup.com/news/index.html",
                     "https://news.mtn.co.kr/category-news/M1500",
                     "https://www.dailypharm.com/Users/News/SectionList.html?Section=2",
                     "https://www.whosaeng.com/sub_view.html?type=abs",
                     "https://www.paxetv.com/news/articleList.html?sc_section_code=S1N14&view_type=sm",
                     "https://www.medipana.com/news/articleList.html?sc_section_code=S1N2&view_type=sm",
                     "https://www.boannews.com/media/t_list.asp"
                     ]
        self.url = "https://www.medipana.com/news/articleList.html?sc_section_code=S1N2&view_type=sm"
        
        self.list_set = set()

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
                elif "finance-scope" in url:
                    self.parse_finance_scope_news(url)
                elif "hankyung" in url: 
                    self.parse_hankyung_news(url)
                elif "pointe" in url:
                    self.parse_pointe_news(url)
                elif "dt.co.kr" in url:
                    self.parse_dt_news(url)
                elif "biotimes" in url:
                    self.parse_biotimes_news(url)
                elif "pinpointnews" in url:
                    self.parse_pinpointnews_news(url)
                elif "kdfnews" in url:
                    self.parse_kdfnews_news(url)
                elif "gamefocus" in url:
                    self.parse_gamefocus_news(url)
                elif "newsis.com/world" in url:
                    self.parse_newsis_world_news(url)   
                elif "newsis.com/money" in url:
                    self.parse_newsis_money_news(url)   
                elif "newsis.com/economy" in url:
                    self.parse_newsis_economy_news(url)
                elif "newsis.com/business" in url:
                    self.parse_newsis_business_news(url)
                elif "epnc" in url:
                    self.parse_epnc_news(url)
                elif "businesspost" in url:
                    self.parse_businesspost_news(url)
                elif "signalm" in url:
                    self.parse_signalm_news(url)
                elif "ebn" in url:
                    self.parse_ebn_news(url)
                elif "bosa" in url:
                    self.parse_bosa_news(url)
                elif "press9" in url and "S1N12" in url:
                    self.parse_press9_pharmbiz_news(url)
                elif "press9" in url and "S1N14" in url:
                    self.parse_press9_industry_news(url)
                elif "medisobizanews" in url:
                    self.parse_medisobizanews_news(url)
                elif "g-enews" in url:
                    self.parse_genews_news1(url)
                    self.parse_genews_news2(url)
                elif "autodaily" in url:
                    self.parse_autodaily_news(url)
                elif "economist" in url:
                    self.parse_economist_news1(url)
                    self.parse_economist_news2(url)
                elif "medisobizanews" in url:
                    self.parse_medisobizanews_news(url)
                elif "naver.com" in url:
                    self.parse_naver_news(url)
                elif "theguru" in url:
                    self.parse_theguru_news(url)
                elif "mtn.co" in url:
                    self.parse_mtn_it_news(url)
                elif "dailypharm" in url:
                    self.parse_dailypharm_news(url)
                elif "whosaeng" in url:
                    self.parse_whosaeng_news(url)
                elif "paxetv" in url:
                    self.parse_paxetv_news(url)
                elif "medipana" in url:
                    self.parse_medipana_news(url)
                elif "boannews" in url:
                    self.parse_boannews_news(url)
                time.sleep(60)  
        except KeyboardInterrupt:
            print('\nfinish')
            pass

    def parse_boannews_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.news_list")

        for article in articles:
            a_tag = article.find("a", href=True)
            title_tag = article.find("span", class_="news_txt")
            title = title_tag.get_text(strip=True)
            link = "https://www.boannews.com" + a_tag['href']
            date_tag = article.find("span", class_="news_writer")
            date_str = date_tag.get_text(strip=True).split("|")[-1].strip()
            dt = datetime.strptime(date_str, "%Y년 %m월 %d일 %H:%M")
            date = dt.strftime("%Y-%m-%d %H:%M")
            

            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 

    def parse_medipana_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("li.altlist-webzine-item")

        for article in articles:
            title_tag = article.select_one("h2.altlist-subject a")
            title = title_tag.get_text(strip=True)
            link = title_tag['href']

            date_tag = article.select("div.altlist-info-item")[-1]
            date = date_tag.get_text(strip=True)

            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 

    def parse_paxetv_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        req.encoding = req.apparent_encoding
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.list-block")

        for article in articles:
            title_tag = article.select_one("div.list-titles a strong")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link_tag = article.select_one("div.list-titles a")
            href = link_tag.get("href", "")
            link = "https://www.paxetv.com" + href   

            date_tag = article.select_one("div.list-dated")
            full_date_text = date_tag.get_text(strip=True) if date_tag else ""
            date = full_date_text.split("|")[-1].strip() if "|" in full_date_text else full_date_text

            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 
    
    def parse_whosaeng_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.news_list2")

        for article in articles:
            title_tag = article.select_one("dd.title a")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = "https://www.whosaeng.com" + title_tag['href']

            date_tag = article.select_one("dd.write span.wdate")
            date = date_tag.get_text(strip=True) if date_tag else ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 

    def parse_dailypharm_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        req.encoding = 'euc-kr' 
        soup = BeautifulSoup(req.text, 'html.parser')
        sections = soup.select("li.SectionList")

        for sec in sections:
            articles = sec.select("div.SectionBody ul > li")

            for article in articles:
                a_tag = article.select_one("a[href]")
                if not a_tag:
                    continue

                link = "https://www.dailypharm.com/Users/News/" + a_tag["href"].lstrip("/")

                title_tag = article.select_one("div.HeadText div.Title")

                if not title_tag:
                    title_tag = a_tag

                title = title_tag.get_text(strip=True)
                date = ""
                if title not in self.list_set:
                    self.list_set.add(title)
                    print(title, link, date)
                else:
                    break 
    
    def parse_mtn_it_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("ul.css-ratt8o > li")

        for article in articles:
            a_tag = article.select_one("a")
            if not a_tag:
                continue

            link = "https://news.mtn.co.kr" + a_tag["href"]

            title_tag = article.select_one("div.css-9gdod1 h3")
            date_tag = article.select_one("div.css-9gdod1 time")

            title = title_tag.get_text(strip=True) if title_tag else ""
            date = date_tag.get_text(strip=True) if date_tag else ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 

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
        articles = soup.select("div.info_con ul > li")
    
        for article in articles:
            a_tag = article.select_one("a")
            if not a_tag:
                continue

            link = a_tag.get("href", "").strip()
            if link.startswith("/"):
                link = "https://www.yakup.com" + link

            title_tag = article.select_one("div.title_con > span")
            title = title_tag.get_text(strip=True) if title_tag else ""

            date_tag = article.select_one("div.name_con span.date")
            date = date_tag.get_text(strip=True) if date_tag else ""
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

    def parse_finance_scope_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.img_mark_reporter.m_colums")
        
        for article in articles:
            title_tag = article.select_one("div.pick_ttl a")
    
            title = title_tag.get_text(strip=True)
            link = f"https://www.finance-scope.com{title_tag["href"]}"

            date_tag = article.select_one("div.img_mark_info span.color_999")
            date = date_tag.get_text(strip=True) if date_tag else ""
            if title == "프리미엄 회원에게만 제공되는 기사입니다":
                continue
            elif title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break
    
    
    def parse_hankyung_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("ul.news-list li")
        
        for article in articles:
            a_tag = article.select_one("h3.news-tit a")
            title = a_tag.get_text(strip=True)
            link = a_tag["href"]

            # 날짜
            date_tag = article.select_one("div.news-info span.date")
            date = date_tag.get_text(strip=True) if date_tag else ""

            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break

    def parse_pointe_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*',
}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("section#section-list ul.type2 li")
        
        for article in articles:
            a_tag = article.select_one("div.view-cont h2.titles a")
            title = a_tag.get_text(strip=True)
            link = a_tag["href"]
            link = "https://www.pointe.co.kr" + link

            # 날짜
            em_tags = article.select("div.view-cont span.byline em")
            date = em_tags[-1].get_text(strip=True) if em_tags else ""

            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break
        
    def parse_dt_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.sec-list ul li")
        for article in articles:
            
            a_tag = article.select_one("div.card-body h2.headline a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)

            link = "https://www.dt.co.kr" + a_tag["href"]

            date_tag = article.select_one("div.card-body p.byline span.date")
            date = date_tag.get_text(strip=True) 
            
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
                
            else:
                break
        
    def parse_biotimes_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.table-row")
        for article in articles:
            a_tag = article.select_one("div.list-titles a.links")
            title = a_tag.get_text(strip=True)
            link = "https://www.biotimes.co.kr" + a_tag["href"]

            date_text = article.select_one("div.list-dated").get_text(strip=True)
            date = date_text.split("|")[-1].strip()
            
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
                
            else:
                break

    def parse_pinpointnews_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("li")
        
        for article in articles:
            a_tag = article.select_one("h4.titles a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)
            if not title:
                continue
            link = "https://www.pinpointnews.co.kr" + a_tag["href"]

            byline = article.select_one("span.byline")
            date = None
            if byline:
                text = byline.get_text(strip=True)
                
                match = re.search(r"\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}", text)
                if match:
                    date = match.group(0)
            # else:
            #     now = datetime.now()
            #     hour_minute = now.strftime("%H:%M")
            #     date = f"{date} {hour_minute}" 

            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
                
            else:
                break

    def parse_kdfnews_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.list-block")
        for article in articles:
            a_tag = article.select_one("div.list-titles a")
            
            title = a_tag.get_text(strip=True)
            link = "https://www.kdfnews.com" + a_tag["href"] 
            
            date_tag = article.select_one("div.list-dated")
            date = None
            if date_tag:
                text = date_tag.get_text(strip=True)
                match = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", text)
                if match:
                    date = match.group(0)
            
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
                
            else:
                break 
            
    def parse_gamefocus_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        a_tags = soup.select("td[style*='padding-bottom'] a")

        for a_tag in a_tags:
            title = a_tag.get_text(strip=True)
            link = "https://gamefocus.co.kr/" + a_tag["href"]

            # 같은 tr 안에서 날짜(font) 찾기
            tr = a_tag.find_parent("tr")
            date_tag = tr.find_next("font", style=lambda v: v and "858585" in v)
            date = date_tag.get_text(strip=True) if date_tag else ""
            
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
                
            else:
                break 

    def parse_newsis_world_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("ul.articleList2 > li")

        for article in articles:
            a_tag = article.select_one("p.tit a")
            title = a_tag.get_text(strip=True)
            link = "https://www.newsis.com/" +  a_tag["href"]

            time_tag = article.select_one("p.time")
            date = time_tag.get_text(strip=True).split("기자")[1] if time_tag else ""
            
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 

    def parse_newsis_money_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("ul.articleList2 > li")

        for article in articles:
            a_tag = article.select_one("p.tit a")
            title = a_tag.get_text(strip=True)
            link = "https://www.newsis.com/" +  a_tag["href"]

            time_tag = article.select_one("p.time")
            date = time_tag.get_text(strip=True).split("기자")[1] if time_tag else ""
            
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 

    def parse_newsis_economy_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("ul.articleList2 > li")

        for article in articles:
            a_tag = article.select_one("p.tit a")
            title = a_tag.get_text(strip=True)
            link = "https://www.newsis.com/" +  a_tag["href"]

            time_tag = article.select_one("p.time")
            date = time_tag.get_text(strip=True).split("기자")[1] if time_tag else ""
            
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 

    def parse_newsis_business_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("ul.articleList2 > li")

        for article in articles:
            a_tag = article.select_one("p.tit a")
            title = a_tag.get_text(strip=True)
            link = "https://www.newsis.com/" +  a_tag["href"]

            time_tag = article.select_one("p.time")
            date = time_tag.get_text(strip=True).split("기자")[1] if time_tag else ""
            
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 
    
    def parse_epnc_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("section#section-list ul.type2 > li")
    
        for article in articles:
            a_tag = article.select_one("h2.titles a")
            title = a_tag.get_text(strip=True)
            link = "https://www.epnc.co.kr" + a_tag["href"]

            date_tag = article.select_one("span.byline em")
            date = date_tag.get_text(strip=True) if date_tag else ""
            
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 
    
    def parse_businesspost_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.left_post")
    
        for article in articles:
            title = article.select_one("h3").get_text(strip=True)
            link = article.select_one("a")["href"]
            date = None
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 

    def parse_signalm_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.contPadding")
    
        for article in articles:
            a_tag = article.select_one("a.lev1")
            if not a_tag:
                continue
            title_tag = a_tag.select_one("strong span")
            title = title_tag.get_text(strip=True) 

            link = "https://signal.sedaily.com" + a_tag["href"]
            time_tag = a_tag.select_one("span.mCon_writer span.time")
            
            date = time_tag.get_text(strip=True) if time_tag else ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 

    def parse_ebn_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("section#section-list ul.no-bullet > li")
    
        for article in articles:
            a_tag = article.select_one("h2.titles a")

            title = a_tag.get_text(strip=True)
            link = a_tag["href"]
    
            date_divs = article.select("div.byline > div")
            date_year = date_divs[1].get_text(strip=True) if len(date_divs) > 1 else ""
            # year = datetime.now().year
            date = f"2025-{date_year}"
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 

    def parse_bosa_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("section#section-list ul.type2 > li")
    
        for article in articles:
            a_tag = article.select_one("h4.titles a")

            title = a_tag.get_text(strip=True)
            link = "http://www.bosa.co.kr" + a_tag["href"]
    
            em_tags = article.select("span.byline em")
            date = em_tags[2].get_text(strip=True) if len(em_tags) >= 3 else ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 

    def parse_press9_pharmbiz_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.list-block")
    
        for article in articles:
            a_tag = article.select_one("div.list-titles a")

            title = a_tag.get_text(strip=True)
            link = "http://www.press9.kr" + a_tag["href"]
    
            date_text = article.select_one("div.list-dated")
            date = ""
            if date_text:
                parts = date_text.get_text(strip=True).split("|")
                date = parts[-1].strip() if len(parts) >= 1 else ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 

    def parse_press9_industry_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.list-block")
    
        for article in articles:
            a_tag = article.select_one("div.list-titles a")

            title = a_tag.get_text(strip=True)
            link = "http://www.press9.kr" + a_tag["href"]
    
            em_tags = article.select("span.byline em")
            date_text = article.select_one("div.list-dated")
            date = ""
            if date_text:
                parts = date_text.get_text(strip=True).split("|")
                date = parts[-1].strip() if len(parts) >= 1 else ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 
            
    def parse_medisobizanews_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("section#section-list ul.type2 > li")
    
        for article in articles:
            a_tag = article.select_one("h4.titles a")

            title = a_tag.get_text(strip=True)
            link = "https://www.medisobizanews.com" + a_tag["href"]
    
            em_tags = article.select("span.byline em")
            date = em_tags[0].get_text(strip=True) if em_tags else ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 
    
    def parse_genews_news1(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.l1d div.w1")
    
        for article in articles:
            a_tag = article.select_one("a.e2")
            if not a_tag:
                continue

            title = a_tag.get_text(strip=True)
            link = a_tag["href"]

            date = ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break       

    def parse_genews_news2(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.l2d ul > li")
    
        for article in articles:
            a_tag = article.select_one("div.w2 a.e1")
            if not a_tag:
                continue

            title = a_tag.get_text(strip=True)
            link = a_tag["href"]

            date_tag = article.select_one("div.w2 p.e2")
            date = date_tag.get_text(strip=True) if date_tag else ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break       

    def parse_autodaily_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("ul.block-skin > li")
    
        for article in articles:
            title_tag = article.select_one("h4.titles a")
            date_tag = article.select_one("span.dated")

            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = "https://www.autodaily.co.kr" + title_tag["href"]
            date = date_tag.get_text(strip=True) if date_tag else ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break    

    def parse_economist_news1(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.analysis_wrap div.img_part2_keyword_m")
        
        for article in articles:
            title_tag = article.select_one("dt.analysis_ttl a")
            date_tag = article.select_one("dd.analysis_info span.color_999")

            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = "https://www.economist.co.kr" + title_tag["href"]

            date = date_tag.get_text(strip=True) if date_tag else ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break    
    
    def parse_economist_news2(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.signal_pick_wrap_list_inner div.img_mark_reporter.m_colums")

        
        for article in articles:
            title_tag = article.select_one("div.pick_ttl a")
            date_tag = article.select_one("div.img_mark_info span.color_999")

            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = "https://www.economist.co.kr" + title_tag["href"]

            date = date_tag.get_text(strip=True) if date_tag else ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break    

    def parse_medisobizanews_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("section#section-list ul.type2 > li")
        
        for article in articles:
            title_tag = article.select_one("div.view-cont h4.titles a")
            date_tag = article.select_one("div.view-cont span.byline em:first-child")

            title = title_tag.get_text(strip=True)
            link = "https://www.medisobizanews.com" + title_tag["href"]

            date = date_tag.get_text(strip=True) if date_tag else ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break    

    def parse_naver_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        section = soup.select_one("div.section_latest")
        articles = section.select("li.sa_item") 

        for article in articles:
            title_tag = article.select_one("div.sa_text a.sa_text_title strong.sa_text_strong")
            link_tag = article.select_one("div.sa_text a.sa_text_title")

            if not title_tag or not link_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = link_tag["href"].strip()

            date = ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 

    def parse_theguru_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("ul.art_list_all > li")

        for article in articles:
            a_tag = article.select_one("a")
            if not a_tag:
                continue

            link = a_tag["href"].strip()

            title_tag = a_tag.select_one("h2.cmp.c2")
            title = title_tag.get_text(strip=True) if title_tag else ""

            date_tag = a_tag.select_one("ul.art_info li.date")
            date = date_tag.get_text(strip=True) if date_tag else ""
            if title not in self.list_set:
                self.list_set.add(title)
                print(title, link, date)
            else:
                break 

    

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
