import sys
import os
import re
import requests
from bs4 import BeautifulSoup
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import QUrl, QTimer
from PySide6.QtGui import QDesktopServices
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import datetime, timedelta

PRESS_FILE = os.path.join(os.path.dirname(__file__), "press2.txt")

class PressNewsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("언론사 뉴스 크롤러")
        self.resize(1000, 700)

        match_dict = {
            "디지털타임스": "https://www.dt.co.kr/economy/general",
            "BIOTIMES": "https://www.biotimes.co.kr/news/articleList.html",
            "핀포인트뉴스": "https://www.pinpointnews.co.kr/news/articleList.html?sc_section_code=S1N4&view_type=sm",
            "한국면세뉴스": "https://www.kdfnews.com/news/articleList.html?view_type=sm",
            "게임포커스": "https://gamefocus.co.kr/html_file.php?file=normal_all_news.html",
            "뉴시스 국제": "https://www.newsis.com/world/list/?cid=10100&scid=10101",
            "뉴시스 금융": "https://www.newsis.com/money/list/?cid=15000&scid=15001",
            "뉴시스 경제": "https://www.newsis.com/economy/list/?cid=10400&scid=10401",
            "뉴시스 산업": "https://www.newsis.com/business/list/?cid=13000&scid=13001",
            "TECH WORLD": "https://www.epnc.co.kr/news/articleList.html?view_type=sm",
            "비즈니스 포스트": "https://www.businesspost.co.kr/BP?command=sub&sub=2",
            "SIGNAL": "https://signalm.sedaily.com/Main/Content/HeadLine?NClass=AL",
            "EBN 산업경제": "https://www.ebn.co.kr/news/articleList.html?view_type=sm",
            "의학신문": "http://www.bosa.co.kr/news/articleList.html?view_type=sm",
            "PRESS9 팜비즈": "http://www.press9.kr/news/articleList.html?sc_section_code=S1N12&view_type=sm",
            "PRESS9 인더스터리": "http://www.press9.kr/news/articleList.html?sc_section_code=S1N14&view_type=sm",
            "M메디소비자뉴스": "https://www.medisobizanews.com/news/articleList.html?view_type=sm",
            "글로벌이코노믹": "https://www.g-enews.com/list.php?ct=g000000"
        }

        self.urls = []
        if os.path.exists(PRESS_FILE):
            with open(PRESS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip()
                    if word:
                        self.urls.append(match_dict[word])

        self.news_data = []  # [(press, title, link)]
        self.link_set = set()

        layout = QVBoxLayout()

        self.refresh_button = QPushButton("뉴스 새로고침")
        self.refresh_button.clicked.connect(self.load_news)
        layout.addWidget(self.refresh_button)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["매체", "시간", "기사 제목"])
        self.table.cellClicked.connect(self.open_link)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_news)
        self.timer.start(5000)  # 60초마다 자동 새로고침

        self.setLayout(layout)
        self.load_news()

    def format_time_kst(self, ts):
        # ts: timestamp (KST)
        return time.strftime("%H:%M", time.gmtime(ts))

    def normalize_date(self, date_str) -> str:
        formats = [
            "%Y-%m-%d %H:%M",  # 2025-09-07 18:51
            "%Y.%m.%d %H:%M",  # 2025.09.05 13:58,
            "%Y/%m/%d %H:%M",  # 2025.09.05 13:58
            "%Y-%m-%d",        # 2025-09-07
            "%Y.%m.%d",
            "%Y/%m/%d",
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime("%Y.%m.%d %H:%M") if " " in date_str else dt.strftime("%Y.%m.%d")
            except ValueError:
                continue
        raise ValueError(f"지원하지 않는 날짜 형식: {date_str}")

    def parse_dt_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.sec-list ul li")
        items = []
        
        for article in articles:
            a_tag = article.select_one("div.card-body h2.headline a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)

            link = "https://www.dt.co.kr" + a_tag["href"]

            date_tag = article.select_one("div.card-body p.byline span.date")
            date = date_tag.get_text(strip=True) 

            items.append(("디지털타임스", title, link, self.normalize_date(date)))
        return items

    def parse_biotimes_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.table-row")
        items = []

        for article in articles:
            a_tag = article.select_one("div.list-titles a.links")
            title = a_tag.get_text(strip=True)
            link = "https://www.biotimes.co.kr" + a_tag["href"]

            date_text = article.select_one("div.list-dated").get_text(strip=True)
            date = date_text.split("|")[-1].strip()
            
            items.append(("BIOTIMES", title, link, self.normalize_date(date)))
        return items
    
    def parse_pinpointnews_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("li")
        items = []
        
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
            else:
                now = datetime.now()
                date = now.strftime("%Y-%m-%d %H:%M")
            items.append(("핀포인트뉴스", title, link, self.normalize_date(date)))
        return items
    
    def parse_kdfnews_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.list-block")
        items = []

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
            items.append(("한국면세뉴스", title, link, self.normalize_date(date)))
        return items
    
    def parse_gamefocus_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        a_tags = soup.select("td[style*='padding-bottom'] a")
        items = []

        for a_tag in a_tags:
            title = a_tag.get_text(strip=True)
            link = "https://gamefocus.co.kr/" + a_tag["href"]

            tr = a_tag.find_parent("tr")
            date_tag = tr.find_next("font", style=lambda v: v and "858585" in v)
            date = date_tag.get_text(strip=True) if date_tag else ""
            now = datetime.now()
            hour_minute = now.strftime("%H:%M")
            date = f"{date} {hour_minute}" 
            items.append(("게임포커스", title, link, self.normalize_date(date)))
        return items
    
    def parse_newsis_world_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("ul.articleList2 > li")
        items = []

        for article in articles:
            a_tag = article.select_one("p.tit a")
            title = a_tag.get_text(strip=True)
            link = "https://www.newsis.com/" +  a_tag["href"]

            time_tag = article.select_one("p.time")
            date = "".join(time_tag.get_text(strip=True).split("기자")[1][:-3])
            items.append(("뉴시스 국제", title, link, self.normalize_date(date)))
        return items
    
    def parse_newsis_money_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("ul.articleList2 > li")
        items = []

        for article in articles:
            a_tag = article.select_one("p.tit a")
            title = a_tag.get_text(strip=True)
            link = "https://www.newsis.com/" +  a_tag["href"]

            time_tag = article.select_one("p.time")
            date = "".join(time_tag.get_text(strip=True).split("기자")[1][:-3])
            items.append(("뉴시스 금융", title, link, self.normalize_date(date)))
        return items

    def parse_newsis_economy_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("ul.articleList2 > li")
        items = []

        for article in articles:
            a_tag = article.select_one("p.tit a")
            title = a_tag.get_text(strip=True)
            link = "https://www.newsis.com/" +  a_tag["href"]

            time_tag = article.select_one("p.time")
            date = "".join(time_tag.get_text(strip=True).split("기자")[1][:-3])
            items.append(("뉴시스 경제", title, link, self.normalize_date(date)))
        return items
    
    def parse_newsis_business_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("ul.articleList2 > li")
        items = []

        for article in articles:
            a_tag = article.select_one("p.tit a")
            title = a_tag.get_text(strip=True)
            link = "https://www.newsis.com/" +  a_tag["href"]

            time_tag = article.select_one("p.time")
            date = "".join(time_tag.get_text(strip=True).split("기자")[1][:-3])
            items.append(("뉴시스 산업", title, link, self.normalize_date(date)))
        return items
    
    def parse_epnc_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("section#section-list ul.type2 > li")
        items = []

        for article in articles:
            a_tag = article.select_one("h2.titles a")
            title = a_tag.get_text(strip=True)
            link = "https://www.epnc.co.kr" + a_tag["href"]

            date_tag = article.select_one("span.byline em")
            date = date_tag.get_text(strip=True) if date_tag else ""
            items.append(("TECH WORLD", title, link, self.normalize_date(date)))
        return items
    
    def parse_businesspost_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.left_post")
        items = []

        for article in articles:
            title = article.select_one("h3").get_text(strip=True)
            link = article.select_one("a")["href"]
            now = datetime.now()
            date = now.strftime("%Y-%m-%d %H:%M")
            items.append(("비즈니스 포스트", title, link, self.normalize_date(date)))
        return items
    
    def parse_signalm_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.contPadding")
        items = []
    
        for article in articles:
            a_tag = article.select_one("a.lev1")
            if not a_tag:
                continue
            title_tag = a_tag.select_one("strong span")
            title = title_tag.get_text(strip=True) 

            link = "https://signal.sedaily.com" + a_tag["href"]
            time_tag = a_tag.select_one("span.mCon_writer span.time")
            
            date = time_tag.get_text(strip=True) if time_tag else ""
            items.append(("SIGNAL", title, link, self.normalize_date(date)))
        return items
    
    def parse_ebn_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("section#section-list ul.no-bullet > li")
        items = []

        for article in articles:
            a_tag = article.select_one("h2.titles a")

            title = a_tag.get_text(strip=True)
            link = a_tag["href"]
    
            date_divs = article.select("div.byline > div")
            date_year = date_divs[1].get_text(strip=True) if len(date_divs) > 1 else ""
            year = datetime.now().year
            date = f"2025-{date_year}"
            items.append(("EBN 산업경제", title, link, self.normalize_date(date)))
        return items
    
    def parse_bosa_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("section#section-list ul.type2 > li")
        items = []

        for article in articles:
            a_tag = article.select_one("h4.titles a")

            title = a_tag.get_text(strip=True)
            link = "http://www.bosa.co.kr" + a_tag["href"]
    
            em_tags = article.select("span.byline em")
            date = em_tags[2].get_text(strip=True) if len(em_tags) >= 3 else ""
            items.append(("의학신문", title, link, self.normalize_date(date)))
        return items
    
    def parse_press9_pharmbiz_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.list-block")
        items = []
    
        for article in articles:
            a_tag = article.select_one("div.list-titles a")

            title = a_tag.get_text(strip=True)
            link = "http://www.press9.kr" + a_tag["href"]
    
            date_text = article.select_one("div.list-dated")
            date = ""
            if date_text:
                parts = date_text.get_text(strip=True).split("|")
                date = parts[-1].strip() if len(parts) >= 1 else ""
            items.append(("PRESS9 팜비즈", title, link, self.normalize_date(date)))
        return items
    
    def parse_press9_industry_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.list-block")
        items = []
    
        for article in articles:
            a_tag = article.select_one("div.list-titles a")

            title = a_tag.get_text(strip=True)
            link = "http://www.press9.kr" + a_tag["href"]
    
            date_text = article.select_one("div.list-dated")
            date = ""
            if date_text:
                parts = date_text.get_text(strip=True).split("|")
                date = parts[-1].strip() if len(parts) >= 1 else ""
            items.append(("PRESS9 인더스터리", title, link, self.normalize_date(date)))
        return items
    
    def parse_medisobizanews_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("section#section-list ul.type2 > li")
        items = []

        for article in articles:
            a_tag = article.select_one("h4.titles a")

            title = a_tag.get_text(strip=True)
            link = "https://www.medisobizanews.com" + a_tag["href"]
    
            em_tags = article.select("span.byline em")
            date = em_tags[0].get_text(strip=True) if em_tags else ""
            items.append(("M메디소비자뉴스", title, link, self.normalize_date(date)))
        return items
    
    def parse_genews_news1(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.l1d div.w1")
        items = []
    
        for article in articles:
            a_tag = article.select_one("a.e2")
            if not a_tag:
                continue

            title = a_tag.get_text(strip=True)
            link = a_tag["href"]

            now = datetime.now()
            date = now.strftime("%Y-%m-%d %H:%M")
            items.append(("글로벌이코노믹", title, link, self.normalize_date(date)))
        return items   

    def parse_genews_news2(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.l2d ul > li")
        items = []

        for article in articles:
            a_tag = article.select_one("div.w2 a.e1")
            if not a_tag:
                continue

            title = a_tag.get_text(strip=True)
            link = a_tag["href"]

            date_tag = article.select_one("div.w2 p.e2")
            date = date_tag.get_text(strip=True) if date_tag else ""
            items.append(("글로벌이코노믹", title, link, self.normalize_date(date)))
        return items 
    
    def load_news(self):
        new_results = []
        new_links = set()
        def parse_url(url):
            if "dt.co.kr" in url:
                return self.parse_dt_news(url)
            elif "biotimes" in url:
                return self.parse_biotimes_news(url)
            elif "pinpointnews" in url:
                return self.parse_pinpointnews_news(url)
            elif "kdfnews" in url:
                return self.parse_kdfnews_news(url)
            elif "gamefocus" in url:
                return self.parse_gamefocus_news(url)
            elif "newsis.com/world" in url:
                return self.parse_newsis_world_news(url)   
            elif "newsis.com/money" in url:
                return self.parse_newsis_money_news(url)   
            elif "newsis.com/economy" in url:
                return self.parse_newsis_economy_news(url)
            elif "newsis.com/business" in url:
                return self.parse_newsis_business_news(url)
            elif "epnc" in url:
                return self.parse_epnc_news(url)
            elif "businesspost" in url:
                return self.parse_businesspost_news(url)
            elif "signalm" in url:
                return self.parse_signalm_news(url)
            elif "ebn" in url:
                return self.parse_ebn_news(url)
            elif "bosa" in url:
                return self.parse_bosa_news(url)
            elif "press9" in url and "S1N12" in url:
                return self.parse_press9_pharmbiz_news(url)
            elif "press9" in url and "S1N14" in url:
                return self.parse_press9_industry_news(url)
            elif "medisobizanews" in url:
                return self.parse_medisobizanews_news(url)
            elif "g-enews" in url:
                items1 = self.parse_genews_news1(url)
                items2 = self.parse_genews_news2(url)
                return items1 + items2
            else:
                return []

        with ThreadPoolExecutor(max_workers=len(self.urls)) as executor:
            futures = [executor.submit(parse_url, url) for url in self.urls]
            for future in futures:
                items = future.result()
                for press, title, link, ts in items:
                    if link not in self.link_set and link not in new_links:
                        new_results.append((press, title, link, ts))
                        new_links.add(link)
        if new_results:
            self.news_data.extend(new_results)
            self.link_set.update(new_links)
            # 테이블 전체 초기화 후 재삽입
            self.news_data.sort(key=lambda x: x[3] if isinstance(x[3], int) else x[3], reverse=True)
            self.table.setRowCount(0)
            for row, (press, title, link, ts) in enumerate(self.news_data):
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(press))
                self.table.setItem(row, 1, QTableWidgetItem(self.format_time_kst(ts) if isinstance(ts, int) else ts))
                self.table.setItem(row, 2, QTableWidgetItem(title))

    def open_link(self, row, col):
        link = self.news_data[row][2]
        QDesktopServices.openUrl(QUrl(link))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PressNewsApp()
    win.show()
    sys.exit(app.exec())
