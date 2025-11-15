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

PRESS_FILE = os.path.join(os.path.dirname(__file__), "press3.txt")

class PressNewsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("언론사 뉴스 크롤러")
        self.resize(1000, 700)

        match_dict = {
            "네이버뉴스 경제": "https://news.naver.com/section/101",
            "네이버뉴스 IT/과학": "https://news.naver.com/section/105",
            "네이버뉴스 세계": "https://news.naver.com/section/104",
            "더구루": "https://www.theguru.co.kr/news/article_list_all.html",
            "약업": "https://www.yakup.com/news/index.html",
            "전자신문": "https://www.etnews.com/news/section.html",
            "핀포인트뉴스": "https://www.pinpointnews.co.kr/news/articleList.html?sc_section_code=S1N4&view_type=sm",
        }

        self.urls = []
        if os.path.exists(PRESS_FILE):
            with open(PRESS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip()
                    if word and word.startswith('#') is False:
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
    
    def parse_naver_eco_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        section = soup.select_one("div.section_latest")
        articles = section.select("li.sa_item") 
        items = []

        for article in articles:
            title_tag = article.select_one("div.sa_text a.sa_text_title strong.sa_text_strong")
            link_tag = article.select_one("div.sa_text a.sa_text_title")

            if not title_tag or not link_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = link_tag["href"].strip()

            now = datetime.now()
            date = now.strftime("%Y-%m-%d %H:%M")
            items.append(("네이버뉴스 경제", title, link, self.normalize_date(date)))
        return items

    def parse_naver_it_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        section = soup.select_one("div.section_latest")
        articles = section.select("li.sa_item") 
        items = []

        for article in articles:
            title_tag = article.select_one("div.sa_text a.sa_text_title strong.sa_text_strong")
            link_tag = article.select_one("div.sa_text a.sa_text_title")

            if not title_tag or not link_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = link_tag["href"].strip()

            now = datetime.now()
            date = now.strftime("%Y-%m-%d %H:%M")
            items.append(("네이버뉴스 it/과학", title, link, self.normalize_date(date)))
        return items
    
    def parse_naver_world_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        section = soup.select_one("div.section_latest")
        articles = section.select("li.sa_item") 
        items = []

        for article in articles:
            title_tag = article.select_one("div.sa_text a.sa_text_title strong.sa_text_strong")
            link_tag = article.select_one("div.sa_text a.sa_text_title")

            if not title_tag or not link_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = link_tag["href"].strip()

            now = datetime.now()
            date = now.strftime("%Y-%m-%d %H:%M")
            items.append(("네이버뉴스 세계", title, link, self.normalize_date(date)))
        return items
    
    def parse_theguru_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("ul.art_list_all > li")
        items = []

        for article in articles:
            a_tag = article.select_one("a")
            if not a_tag:
                continue

            link = a_tag["href"].strip()

            title_tag = a_tag.select_one("h2.cmp.c2")
            title = title_tag.get_text(strip=True) if title_tag else ""

            date_tag = a_tag.select_one("ul.art_info li.date")
            date = date_tag.get_text(strip=True) if date_tag else ""
            items.append(("더구루", title, link, self.normalize_date(date)))
        return items 
    
    def parse_yakup_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.info_con ul > li")
        items = []

        for article in articles:
            a_tag = article.select_one("a")
            if not a_tag:
                continue

            link = a_tag.get("href", "").strip()
            if link.startswith("/"):
                link = "https://www.yakup.com" + link

            title_tag = article.select_one("div.title_con > span")
            if title_tag:
                title = title_tag.get_text(strip=True) 
            else:
                continue

            now = datetime.now()
            date = now.strftime("%Y-%m-%d %H:%M")
            items.append(("약업", title, link, self.normalize_date(date)))
        return items 
    
    def parse_etnews_news(self, url):
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept': '*/*'}
        req = requests.get(url, headers=header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('ul.news_list li')
        items = []
        ts = int(time.time()) + 9 * 3600
        for article in articles:
            title_tag = article.select_one("strong a")
            title = title_tag.text.strip() if title_tag else ""
            link = "https://www.etnews.com" + title_tag['href'] if title_tag else ""
            date_tag = article.select_one("div.flex span.date")
            date = date_tag.text.strip() if date_tag else ""
            items.append(("전자신문", title, link, self.normalize_date(date)))
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
    
    def load_news(self):
        new_results = []
        new_links = set()
        def parse_url(url):
            if url == "https://news.naver.com/section/101":
                return self.parse_naver_eco_news(url)
            elif url == "https://news.naver.com/section/105":
                return self.parse_naver_it_news(url)
            elif url == "https://news.naver.com/section/104":
                return self.parse_naver_world_news(url)
            elif "theguru" in url:
                return self.parse_theguru_news(url)
            elif "yakup" in url:
                return self.parse_yakup_news(url)
            elif "etnews" in url:
                return self.parse_etnews_news(url)
            elif "pinpointnews" in url:
                return self.parse_pinpointnews_news(url)
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
