import sys
import requests
from bs4 import BeautifulSoup
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
from PySide6.QtCore import QUrl, QTimer
from PySide6.QtGui import QDesktopServices
from concurrent.futures import ThreadPoolExecutor
import time

class NewsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("뉴스 크롤러")
        self.resize(800, 600)

        self.keywords = ['승인', '탈모', '세계최초','AI','매각','신약','현대투자','유리기판','데이터센터','게임체인저','양자','테슬라','3상',
                        '단독', 'FDA', '완전관해', '사멸', '암','삼성투자','당뇨','엔비디아',
                         '독점', '상용화','대선정책','승소','국산화',
                        '경영권분쟁',  '이차전지', '로봇','치매','인수',
                        '국내최초', 'm&a','비만',
                       '개발']  # 초기 키워드
        self.news_data = []  # [(media, ts, kw, title, link)]
        self.link_set = set()  # 링크 중복 방지용

        # 레이아웃
        layout = QVBoxLayout()

        # 키워드 입력
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("키워드 입력 후 Enter")
        self.keyword_input.returnPressed.connect(self.add_keyword)
        layout.addWidget(self.keyword_input)

        # 새로고침 버튼
        self.refresh_button = QPushButton("뉴스 새로고침")
        self.refresh_button.clicked.connect(self.load_news)
        layout.addWidget(self.refresh_button)

        # 테이블
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["매체", "시간", "키워드", "기사 제목"])
        self.table.cellClicked.connect(self.open_link)
        # 기사 제목 칸을 stretch로 설정
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        layout.addWidget(self.table)

        # 30초마다 자동 새로고침 타이머
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_news)
        self.timer.start(30000)  # 30초(30000ms)마다 load_news 호출

        self.setLayout(layout)

        # 프로그램 시작 시 자동으로 뉴스 로드
        self.load_news()

    def add_keyword(self):
        word = self.keyword_input.text().strip()
        if word and word not in self.keywords:
            self.keywords.append(word)
            QMessageBox.information(self, "키워드 추가", f"'{word}' 키워드가 추가되었습니다.")
        self.keyword_input.clear()

    def fetch_news_for_keyword_naver(self, kw):
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46',
            'Accept': '*/*'
        }
        url = f"https://search.naver.com/search.naver?where=news&query={kw}&sort=1&start=0"
        news_items = []
        try:
            req = requests.get(url, headers=header)
            soup = BeautifulSoup(req.text, 'html.parser')
            articles = soup.select('.sds-comps-vertical-layout.sds-comps-full-layout.sKYUZNwnLHdgmIxCzyqY')
            for article in articles:
                a_tag = article.select_one("a:has(span.sds-comps-text-type-headline1)")
                if not a_tag:
                    continue
                title = a_tag.get_text(strip=True)
                link = a_tag["href"]
                media = "Naver"
                # 네이버는 시간 정보가 없으므로 현재 KST 시간 사용
                ts = int(time.time()) + 9 * 3600
                news_items.append((media, ts, kw, title, link))
        except Exception as e:
            print(f"Error loading Naver news for {kw}: {e}")
        return news_items

    def parse_time(self, time_text):
        # KST 기준 timestamp 반환
        KST_OFFSET = 9 * 3600
        now = int(time.time()) + KST_OFFSET
        if not time_text:
            return now
        try:
            if '초 전' in time_text:
                sec = int(time_text.replace('초 전', '').strip())
                return now - sec
            elif '분 전' in time_text:
                mins = int(time_text.replace('분 전', '').strip())
                return now - mins * 60
            elif '시간 전' in time_text:
                hours = int(time_text.replace('시간 전', '').strip())
                return now - hours * 3600
            elif '일 전' in time_text:
                days = int(time_text.replace('일 전', '').strip())
                return now - days * 86400
            else:
                # 날짜 포맷 예: 2024.05.01.
                try:
                    t = time.strptime(time_text.strip(), "%Y.%m.%d.")
                    return int(time.mktime(t)) + KST_OFFSET
                except Exception:
                    return now
        except Exception:
            return now

    def format_time_kst(self, ts):
        # ts: timestamp (KST)
        return time.strftime("%H:%M", time.gmtime(ts))

    def load_news(self):
        # 기존 데이터 유지
        new_results = []
        new_links = set()
        with ThreadPoolExecutor(max_workers=min(16, len(self.keywords)*2)) as executor:
            naver_futures = [executor.submit(self.fetch_news_for_keyword_naver, kw) for kw in self.keywords]
            for future in naver_futures:
                news_items = future.result()
                for item in news_items:
                    link = item[4]
                    if link not in self.link_set and link not in new_links:
                        new_results.append(item)
                        new_links.add(link)
        # 새 기사만 추가
        if new_results:
            self.news_data.extend(new_results)
            self.link_set.update(new_links)
            # 시간순(최신순)으로 정렬
            self.news_data.sort(key=lambda x: x[1], reverse=True)
            # 테이블 전체 초기화 후 재삽입
            self.table.setRowCount(0)
            for row, (media, ts, kw, title, link) in enumerate(self.news_data):
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(media))
                self.table.setItem(row, 1, QTableWidgetItem(self.format_time_kst(ts)))
                self.table.setItem(row, 2, QTableWidgetItem(kw))
                self.table.setItem(row, 3, QTableWidgetItem(title))
        # 새 기사 없으면 아무 작업 안함

    def open_link(self, row, col):
        link = self.news_data[row][4]
        QDesktopServices.openUrl(QUrl(link))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = NewsApp()
    win.show()
    sys.exit(app.exec())