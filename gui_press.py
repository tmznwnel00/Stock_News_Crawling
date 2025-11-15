import sys
import os
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

PRESS_FILE = os.path.join(os.path.dirname(__file__), "press1.txt")

class PressNewsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("언론사 뉴스 크롤러")
        self.resize(1000, 700)

        match_dict = {
            "인포스탁": "https://www.infostockdaily.co.kr/news/articleList.html?sc_section_code=S1N17&view_type=sm",
            "더벨": "https://www.thebell.co.kr/free/content/Article.asp?svccode=00",
            "더일렉": "https://www.thelec.kr/news/articleList.html",
            "지디넷코리아": "https://zdnet.co.kr/news/?lstcode=0000&page=1",
            "딜사이트": "https://dealsite.co.kr/newsflash/",
            "팜뉴스": "https://www.pharmnews.com/news/articleList.html?view_type=sm",
            "전자신문": "https://www.etnews.com/news/section.html",
            "뉴스핌": "https://www.newspim.com/news/lists?category_cd=1",
            "프라임경제 자본시장": "https://www.newsprime.co.kr/news/section_list_all/?sec_no=56",
            "프라임경제 산업": "https://www.newsprime.co.kr/news/section_list_all/?sec_no=57",
            "파이낸스스코프": "https://www.finance-scope.com/article/list/scp_SC007000000",
            "한국경제": "https://www.hankyung.com/press-release",
            "포인트경제": "https://www.pointe.co.kr/news/articleList.html?sc_section_code=S1N13&view_type=sm",
            "엠투데이": "https://www.autodaily.co.kr/news/articleList.html",
            "이코노미스트": "https://economist.co.kr/article/list/ecn_SC011000000",
            "메디소비자뉴스": "https://www.medisobizanews.com/news/articleList.html?view_type=sm"
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
        self.timer.start(5000)  

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
        today_str = (datetime.now() - timedelta(days=1)).strftime("%Y.%m.%d")

        ts = int(time.time()) + 9 * 3600
        for article in articles:
            a_tag = article.select_one("a.title")
            title = a_tag.text.strip()
            link = "https://dealsite.co.kr" + a_tag['href']
            time_tag = article.select_one("span.pub-date")
            pub_time = time_tag.text.strip() if time_tag else ""
            pub_time = today_str + " " + pub_time
            items.append(("딜사이트", title, link, self.normalize_date(pub_time)))
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
    
    def parse_newspim_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('article.thumb_h')
        items = []
        for article in articles:
            title_tag = article.select_one("strong.subject a")
            title = title_tag.get_text(strip=True)
            link = f"https://www.newspim.com/{title_tag["href"]}"

            date_tag = article.select_one("span.date")
            date = date_tag.get_text(strip=True)
            items.append(("뉴스핌", title, link, self.normalize_date(date)))
        return items
            
    def parse_newsprime_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*',
                  'Cookie': 'csrf_cookie_name=c4750f901e0aba407d4529a3492a27c3; TRACKER_MYLOG1=Mon%2C%2008%20Sep%202025%2004%3A02%3A56%20GMT; _fwb=34nsXtTmtiDC6WvsGUlcA.1757304176559; SID=d64f8fdbb8eea30391ffa229971eb859; _ga=GA1.1.624392975.1757304177; wcs_bt=ad0380f89be1f8:1757304797; _ga_BPMKJNZW0V=GS2.1.s1757304177$o1$g1$t1757304798$j1$l0$h0'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select('td.news1')
        items = []
        for article in articles:
            title_tag = article.select_one("a")
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]

            parent = article.find_parent("tr").find_next_sibling("tr")
            date_span = parent.select_one("span.font11blue2") if parent else None
            text = date_span.get_text(strip=True)
            date = text.split("]")[-1].strip() if "]" in text else text
            dt = datetime.strptime(date, "%Y.%m.%d %H:%M:%S")
            date = dt.strftime("%Y.%m.%d %H:%M")
            if "sec_no=56" in url:
                items.append(("프라임경제 자본시장", title, link, self.normalize_date(date)))
            elif "sec_no=57" in url:
                items.append(("프라임경제 산업", title, link, self.normalize_date(date)))
        return items
    
    def parse_finance_scope_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*',
                  'Cookie': 'csrf_cookie_name=c4750f901e0aba407d4529a3492a27c3; TRACKER_MYLOG1=Mon%2C%2008%20Sep%202025%2004%3A02%3A56%20GMT; _fwb=34nsXtTmtiDC6WvsGUlcA.1757304176559; SID=d64f8fdbb8eea30391ffa229971eb859; _ga=GA1.1.624392975.1757304177; wcs_bt=ad0380f89be1f8:1757304797; _ga_BPMKJNZW0V=GS2.1.s1757304177$o1$g1$t1757304798$j1$l0$h0'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.img_mark_reporter.m_colums")
        items = []
        
        for article in articles:
            title_tag = article.select_one("div.pick_ttl a")
    
            title = title_tag.get_text(strip=True)
            link = f"https://www.finance-scope.com{title_tag["href"]}"

            date_tag = article.select_one("div.img_mark_info span.color_999")
            date = date_tag.get_text(strip=True) if date_tag else ""
            now = datetime.now()
            hour_minute = now.strftime("%H:%M")
            date = f"{date} {hour_minute}" 

            if title == "프리미엄 회원에게만 제공되는 기사입니다":
                continue
            else:
                items.append(("파이낸스스코프", title, link, self.normalize_date(date)))
        return items
    
    def parse_hankyung_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*',
                  'Cookie': 'csrf_cookie_name=c4750f901e0aba407d4529a3492a27c3; TRACKER_MYLOG1=Mon%2C%2008%20Sep%202025%2004%3A02%3A56%20GMT; _fwb=34nsXtTmtiDC6WvsGUlcA.1757304176559; SID=d64f8fdbb8eea30391ffa229971eb859; _ga=GA1.1.624392975.1757304177; wcs_bt=ad0380f89be1f8:1757304797; _ga_BPMKJNZW0V=GS2.1.s1757304177$o1$g1$t1757304798$j1$l0$h0'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("ul.news-list li")
        items = []
        
        for article in articles:
            a_tag = article.select_one("h3.news-tit a")
            title = a_tag.get_text(strip=True)
            link = a_tag["href"]

            date_tag = article.select_one("div.news-info span.date")
            date = date_tag.get_text(strip=True) if date_tag else ""
            now = datetime.now()
            hour_minute = now.strftime("%H:%M")
            date = f"{date} {hour_minute}" 

            items.append(("한국경제", title, link, self.normalize_date(date)))
        return items
    
    def parse_pointe_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*',
                  'Cookie': 'csrf_cookie_name=c4750f901e0aba407d4529a3492a27c3; TRACKER_MYLOG1=Mon%2C%2008%20Sep%202025%2004%3A02%3A56%20GMT; _fwb=34nsXtTmtiDC6WvsGUlcA.1757304176559; SID=d64f8fdbb8eea30391ffa229971eb859; _ga=GA1.1.624392975.1757304177; wcs_bt=ad0380f89be1f8:1757304797; _ga_BPMKJNZW0V=GS2.1.s1757304177$o1$g1$t1757304798$j1$l0$h0'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("section#section-list ul.type2 li")
        items = []

        for article in articles:
            a_tag = article.select_one("div.view-cont h2.titles a")
            title = a_tag.get_text(strip=True)
            link = a_tag["href"]
            link = "https://www.pointe.co.kr" + link

            em_tags = article.select("div.view-cont span.byline em")
            date = em_tags[-1].get_text(strip=True) if em_tags else ""
            items.append(("포인트경제", title, link, self.normalize_date(date)))
        return items
    
    def parse_autodaily_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("ul.block-skin > li")
        items = []
    
        for article in articles:
            title_tag = article.select_one("h4.titles a")
            date_tag = article.select_one("span.dated")

            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = "https://www.autodaily.co.kr" + title_tag["href"]
            date = date_tag.get_text(strip=True) if date_tag else ""
            items.append(("엠투데이", title, link, self.normalize_date(date)))
        return items
    
    def parse_economist_news1(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.analysis_wrap div.img_part2_keyword_m")
        items = []

        for article in articles:
            title_tag = article.select_one("dt.analysis_ttl a")
            date_tag = article.select_one("dd.analysis_info span.color_999")

            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = "https://www.economist.co.kr" + title_tag["href"]

            date = date_tag.get_text(strip=True) if date_tag else ""
            items.append(("이코노미스트", title, link, self.normalize_date(date)))
        return items
    
    def parse_economist_news2(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("div.signal_pick_wrap_list_inner div.img_mark_reporter.m_colums")
        items = []
        
        for article in articles:
            title_tag = article.select_one("div.pick_ttl a")
            date_tag = article.select_one("div.img_mark_info span.color_999")

            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = "https://www.economist.co.kr" + title_tag["href"]

            date = date_tag.get_text(strip=True) if date_tag else ""
            items.append(("이코노미스트", title, link, self.normalize_date(date)))
        return items
    
    def parse_medisobizanews_news(self, url):
        header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46', 'Accept' : '*/*'}
        req = requests.get(url, headers = header)
        soup = BeautifulSoup(req.text, 'html.parser')
        articles = soup.select("section#section-list ul.type2 > li")
        items = []
        
        for article in articles:
            title_tag = article.select_one("div.view-cont h4.titles a")
            date_tag = article.select_one("div.view-cont span.byline em:first-child")

            title = title_tag.get_text(strip=True)
            link = "https://www.medisobizanews.com" + title_tag["href"]

            date = date_tag.get_text(strip=True) if date_tag else ""
            items.append(("메디소비자뉴스", title, link, self.normalize_date(date)))
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
            elif "newspim" in url:
                return self.parse_newspim_news(url)
            elif "newsprime" in url:
                return self.parse_newsprime_news(url)
            elif "finance-scope" in url:
                return self.parse_finance_scope_news(url)
            elif "hankyung" in url:
                return self.parse_hankyung_news(url)
            elif "pointe" in url:
                return self.parse_pointe_news(url)
            elif "autodaily" in url:
                return self.parse_autodaily_news(url)
            elif "economist" in url:
                items1 = self.parse_economist_news1(url)
                items2 = self.parse_economist_news2(url)
                return items1 + items2
            elif "medisobizanews" in url:
                return self.parse_medisobizanews_news(url)
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
