import sys
import requests
from bs4 import BeautifulSoup
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QListWidget, QListWidgetItem, QDialog
)
from PySide6.QtCore import QUrl, QTimer
from PySide6.QtGui import QDesktopServices
from concurrent.futures import ThreadPoolExecutor
import time
import os

KEYWORD_FILE = os.path.join(os.path.dirname(__file__), "keyword.txt")

class KeywordManager(QDialog):
    def __init__(self, keywords, parent=None):
        super().__init__(parent)
        self.setWindowTitle("키워드 관리")
        self.resize(400, 400)
        self.keywords = keywords

        layout = QVBoxLayout()

        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("키워드 입력 후 입력란 아래의 '키워드 추가' 버튼 클릭")
        layout.addWidget(self.keyword_input)

        self.add_button = QPushButton("키워드 추가")
        self.add_button.clicked.connect(self.add_keyword)
        layout.addWidget(self.add_button)

        self.list_widget = QListWidget()
        self.refresh_list()
        layout.addWidget(self.list_widget)

        self.delete_button = QPushButton("선택 키워드 삭제")
        self.delete_button.clicked.connect(self.delete_keyword)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def refresh_list(self):
        self.list_widget.clear()
        for kw in self.keywords:
            item = QListWidgetItem(kw)
            self.list_widget.addItem(item)

    def add_keyword(self):
        word = self.keyword_input.text().strip()
        if word and word not in self.keywords:
            self.keywords.append(word)
            with open(KEYWORD_FILE, "a", encoding="utf-8") as f:
                f.write(f"{word}\n")
            QMessageBox.information(self, "키워드 추가", f"'{word}' 키워드가 추가되었습니다.")
            self.refresh_list()
        self.keyword_input.clear()

    def delete_keyword(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "삭제 오류", "삭제할 키워드를 선택하세요.")
            return
        for item in selected_items:
            kw = item.text()
            if kw in self.keywords:
                self.keywords.remove(kw)
        with open(KEYWORD_FILE, "w", encoding="utf-8") as f:
            for kw in self.keywords:
                f.write(f"{kw}\n")
        self.refresh_list()
        QMessageBox.information(self, "키워드 삭제", "선택한 키워드가 삭제되었습니다.")

class NewsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("뉴스 크롤러")
        self.resize(800, 600)

        self.keywords = self.load_keywords_from_file()
        self.news_data = []  # [(media, ts, kw, title, link)]
        self.link_set = set()  # 링크 중복 방지용

        layout = QVBoxLayout()

        self.keyword_manage_button = QPushButton("키워드 관리")
        self.keyword_manage_button.clicked.connect(self.open_keyword_manager)
        layout.addWidget(self.keyword_manage_button)

        self.refresh_button = QPushButton("뉴스 새로고침")
        self.refresh_button.clicked.connect(self.load_news)
        layout.addWidget(self.refresh_button)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["매체", "시간", "키워드", "기사 제목"])
        self.table.cellClicked.connect(self.open_link)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_news)
        self.timer.start(30000)  # 30초마다 자동 새로고침

        self.setLayout(layout)
        self.load_news()

    def open_keyword_manager(self):
        dlg = KeywordManager(self.keywords, self)
        dlg.exec()
        self.keywords = self.load_keywords_from_file()
        self.load_news()

    def load_keywords_from_file(self):
        keywords = []
        if os.path.exists(KEYWORD_FILE):
            with open(KEYWORD_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip()
                    if word:
                        keywords.append(word)
        return keywords

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
            articles = soup.select('.sds-comps-vertical-layout.sds-comps-full-layout.fds-news-item-list-tab > div')
            for article in articles:
                a_tag = article.select_one("a:has(span.sds-comps-text-type-headline1)")
                if not a_tag:
                    continue
                title = a_tag.get_text(strip=True)
                link = a_tag["href"]
                media = "Naver"
                ts = int(time.time()) + 9 * 3600  # KST
                news_items.append((media, ts, kw, title, link))
        except Exception as e:
            print(f"Error loading Naver news for {kw}: {e}")
        return news_items

    def format_time_kst(self, ts):
        return time.strftime("%H:%M", time.gmtime(ts))

    def load_news(self):
        if not self.keywords:
            self.table.setRowCount(0)
            return

        new_results = []
        new_links = set()
        with ThreadPoolExecutor(max_workers=min(8, len(self.keywords))) as executor:
            naver_futures = [executor.submit(self.fetch_news_for_keyword_naver, kw) for kw in self.keywords]
            for future in naver_futures:
                news_items = future.result()
                for item in news_items:
                    link = item[4]
                    if link not in self.link_set and link not in new_links:
                        new_results.append(item)
                        new_links.add(link)
        if new_results:
            self.news_data.extend(new_results)
            self.link_set.update(new_links)
            self.news_data.sort(key=lambda x: x[1], reverse=True)
            self.table.setRowCount(0)
            for row, (media, ts, kw, title, link) in enumerate(self.news_data):
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(media))
                self.table.setItem(row, 1, QTableWidgetItem(self.format_time_kst(ts)))
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