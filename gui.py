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
from datetime import datetime, timedelta

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
        self.news_data = []

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

    def add_keyword(self):
        word = self.keyword_input.text().strip()
        if word and word not in self.keywords:
            self.keywords.append(word)
            QMessageBox.information(self, "키워드 추가", f"'{word}' 키워드가 추가되었습니다.")
        self.keyword_input.clear()

    def fetch_news_for_keyword(self, kw):
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.46'
        }
        url = f"https://search.daum.net/search?w=news&q={kw}&sort=recency"
        news_items = []
        try:
            req = requests.get(url, headers=header)
            soup = BeautifulSoup(req.text, "html.parser")
            articles = soup.select(".tit-g")
            for a in articles:
                a_tag = a.find('a')
                if not a_tag:
                    continue
                title = a_tag.text.strip()
                link = a_tag['href']
                media = "Daum"
                # 시간 정보 추출
                parent = a.parent
                time_text = None
                # .tit-g의 부모에 .txt_info가 있는 경우
                if parent:
                    time_tag = parent.find("span", class_="txt_info")
                    if time_tag:
                        time_text = time_tag.get_text(strip=True)
                # 시간 파싱
                parsed_time = self.parse_time(time_text)
                news_items.append((media, time_text if time_text else "", kw, title, link, parsed_time))
        except Exception as e:
            print(f"Error loading news for {kw}: {e}")
        return news_items

    def parse_time(self, time_text):
        # Daum 뉴스의 시간 포맷 예시: '1분 전', '2시간 전', '2024.05.01.'
        if not time_text:
            return datetime.min
        try:
            if '초 전' in time_text:
                sec = int(time_text.replace('초 전', '').strip())
                return datetime.now() - timedelta(seconds=sec)
            elif '분 전' in time_text:
                mins = int(time_text.replace('분 전', '').strip())
                return datetime.now() - timedelta(minutes=mins)
            elif '시간 전' in time_text:
                hours = int(time_text.replace('시간 전', '').strip())
                return datetime.now() - timedelta(hours=hours)
            elif '일 전' in time_text:
                days = int(time_text.replace('일 전', '').strip())
                return datetime.now() - timedelta(days=days)
            else:
                # 날짜 포맷 예: 2024.05.01.
                try:
                    return datetime.strptime(time_text.strip(), "%Y.%m.%d.")
                except Exception:
                    return datetime.min
        except Exception:
            return datetime.min

    def load_news(self):
        self.news_data.clear()
        self.table.setRowCount(0)

        results = []
        with ThreadPoolExecutor(max_workers=min(8, len(self.keywords))) as executor:
            futures = [executor.submit(self.fetch_news_for_keyword, kw) for kw in self.keywords]
            for future in futures:
                news_items = future.result()
                results.extend(news_items)

        # 시간순(최신순)으로 정렬
        results.sort(key=lambda x: x[5], reverse=True)
        self.news_data = results

        for row, (media, t, kw, title, link, _) in enumerate(self.news_data):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(media))
            self.table.setItem(row, 1, QTableWidgetItem(t))
            self.table.setItem(row, 2, QTableWidgetItem(kw))
            self.table.setItem(row, 3, QTableWidgetItem(title))

    def open_link(self, row, col):
        link = self.news_data[row][4]
        QDesktopServices.openUrl(QUrl(link))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = NewsApp()
    win.show()
    sys.exit(app.exec())