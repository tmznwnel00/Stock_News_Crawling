import sys
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
from datetime import datetime

class PressNewsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("언론사 뉴스 크롤러")
        self.resize(1000, 700)

        self.urls = [
            "https://www.infostockdaily.co.kr/news/articleList.html?sc_section_code=S1N17&view_type=sm",
            "https://www.thebell.co.kr/free/content/Article.asp?svccode=00",
            "https://www.thelec.kr/news/articleList.html",
            "https://zdnet.co.kr/news/?lstcode=0000&page=1",
            "https://dealsite.co.kr/newsflash/",
            "https://www.pharmnews.com/news/articleList.html?view_type=sm",
            "https://www.etnews.com/news/section.html"
        ]
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
        self.timer.start(60000)  # 60초마다 자동 새로고침

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
                return dt.strftime("%Y.%m.%d %H:%M") if " " in date_str else dt.strftime("%Y/%m/%d")
            except ValueError:
                continue
        raise ValueError(f"지원하지 않는 날짜 형식: {date_str}")

    def parse_info_news(self, url):
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept': '*/*'}
        req = requests.get(url, headers=header, verify=False)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('.list-block')
        items = []
        ts = int(time.time()) + 9 * 3600
        for article in articles:
            div = article.find('div', class_='list-titles')
            title = div.find('strong').text
            link = f"https://www.infostockdaily.co.kr{div.find('a')['href']}"
            dated_div = article.select_one("div.list-dated")
            text = dated_div.get_text(strip=True).split("|")[-1].strip()
            items.append(("인포스탁", title, link, self.normalize_date(text)))
        return items

    def parse_thebell_news(self, url):
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept': '*/*'}
        req = requests.get(url, headers=header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('div.listBox ul li')
        items = []
        ts = int(time.time()) + 9 * 3600
        for article in articles:
            article_find = article.find('a')
            title = article_find["title"]
            link = f"https://www.thebell.co.kr/free/content/{article_find['href']}"
            date_span = article.select_one("dd.userBox span.date")
            raw_date = date_span.get_text(strip=True)
            date_str = raw_date.replace("오전", "AM").replace("오후", "PM")
            
            dt = datetime.strptime(date_str, "%Y-%m-%d %p %I:%M:%S")
            date = dt.strftime("%Y/%m/%d %H:%M")
            items.append(("더벨", title, link, self.normalize_date(date)))
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

    def parse_thelec_news(self, url):
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept': '*/*'}
        req = requests.get(url, headers=header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('section.article-list-content.text-left > .table-row')
        items = []
        ts = int(time.time()) + 9 * 3600
        for article in articles:
            a_tag = article.find('a', class_='links')
            title = a_tag.find('strong').text.strip()
            link = f"https://www.thelec.kr{a_tag['href']}"
            date_div = article.select_one("div.list-dated")
            text = date_div.get_text(strip=True).split("|")[1].strip()
            items.append(("더일렉", title, link, self.normalize_date(text)))
        return items

    def parse_zdnet_news(self, url):
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept': '*/*'}
        req = requests.get(url, headers=header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('div.news_box > .newsPost')
        items = []
        ts = int(time.time()) + 9 * 3600
        for article in articles:
            a_tag = article.find('div', class_='assetText').find('a', href=True)
            title_tag = a_tag.find('h3')
            title = title_tag.text.strip()
            link = f"https://zdnet.co.kr{a_tag['href']}"
            date_span = soup.select_one("p.byline span")
            raw_date = date_span.text.strip() if date_span else ""
            date_split = raw_date.split(" ")
            date = f"{date_split[0]} {date_split[2]}"
            items.append(("지디넷코리아", title, link, self.normalize_date(date)))
        return items

    def parse_dealsite_news(self, url):
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept': '*/*'}
        req = requests.get(url, headers=header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('li[id^=article_]')
        items = []
        ts = int(time.time()) + 9 * 3600
        for article in articles:
            a_tag = article.select_one("a.title")
            title = a_tag.text.strip()
            link = "https://dealsite.co.kr" + a_tag['href']
            time_tag = article.select_one("span.pub-date")
            pub_time = time_tag.text.strip() if time_tag else ""
            items.append(("딜사이트", title, link, pub_time))
        return items

    def parse_pharmnews_news(self, url):
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept': '*/*'}
        req = requests.get(url, headers=header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('section#section-list ul.type li')
        items = []
        ts = int(time.time()) + 9 * 3600
        for article in articles:
            title_tag = article.select_one("h4.titles a")
            title = title_tag.text.strip()
            link = "https://www.pharmnews.com" + title_tag['href']
            date_tag = article.select_one("span.byline em.date")
            date = date_tag.text.strip() if date_tag else ""
            items.append(("팜뉴스", title, link, self.normalize_date(date)))
        return items

    def load_news(self):
        new_results = []
        new_links = set()
        def parse_url(url):
            if "infostockdaily" in url:
                return self.parse_info_news(url)
            elif "thebell" in url:
                return self.parse_thebell_news(url)
            elif "etnews" in url:
                return self.parse_etnews_news(url)
            elif "thelec" in url:
                return self.parse_thelec_news(url)
            elif "zdnet" in url:
                return self.parse_zdnet_news(url)
            elif "dealsite" in url:
                return self.parse_dealsite_news(url)
            elif "pharmnews" in url:
                return self.parse_pharmnews_news(url)
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
