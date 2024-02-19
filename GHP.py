import sys
import requests
from functools import partial
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QScrollArea, QPushButton,
                             QHBoxLayout, QMessageBox, QGridLayout, QDialog, QTextEdit)
from PyQt5.QtCore import QUrl, QRect, Qt
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFont, QColor, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView

class RepoDetailsDialog(QDialog):
    def __init__(self, repo_data):
        super().__init__()
        self.setWindowTitle(repo_data['name'])
        self.initUI(repo_data)

    def initUI(self, repo_data):
        layout = QVBoxLayout(self)
        details = QTextEdit()
        details.setReadOnly(True)
        details.setPlainText(f"Name: {repo_data['name']}\n"
                             f"URL: {repo_data['html_url']}\n"
                             f"Description: {repo_data.get('description', 'N/A')}\n"
                             f"Language: {repo_data.get('language', 'N/A')}\n"
                             f"Forks: {repo_data['forks_count']}\n"
                             f"Stars: {repo_data['stargazers_count']}")
        layout.addWidget(details)

class GitHubApp(QWidget):
    API_URL = "https://api.github.com/users/"
    PER_PAGE = 10

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()
        self.profile_data = None
        self.repos_data = []
        self.current_page = 1
        self.fetch_profile_data()
        self.fetch_repos_data()

    def initUI(self):
        """Initialize the user interface."""
        self.setWindowTitle("GitHub Profile")

        # Load and set the favicon
        self.setWindowIcon(QIcon(r'ASSETS\fav.PNG'))  # Ensure this path is correct

        # Set background image
        palette = QPalette()
        pixmap = QPixmap(r'ASSETS\portFO.PNG')  # Ensure this path is correct
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)

        self.grid_layout = QGridLayout(self)

        self.profile_label = QLabel("Loading profile...")
        self.grid_layout.addWidget(self.profile_label, 0, 0, 1, 1)

        self.repos_area = QScrollArea(self)
        self.repos_area.setWidgetResizable(True)
        self.grid_layout.addWidget(self.repos_area, 1, 0, 1, 1)

        self.webview = QWebEngineView(self)
        self.grid_layout.addWidget(self.webview, 0, 1, 2, 2)

        self.page_controls = QHBoxLayout()
        self.prev_button = QPushButton("Previous", self)
        self.prev_button.clicked.connect(self.prev_page)
        self.page_controls.addWidget(self.prev_button)

        self.page_label = QLabel("Page 1")
        self.page_controls.addWidget(self.page_label)

        self.next_button = QPushButton("Next", self)
        self.next_button.clicked.connect(self.next_page)
        self.page_controls.addWidget(self.next_button)

        self.grid_layout.addLayout(self.page_controls, 2, 0, 1, 1)

        self.profile_button = QPushButton("View Profile", self)
        self.profile_button.clicked.connect(self.view_profile)
        self.grid_layout.addWidget(self.profile_button, 2, 1, 1, 1)

        # Adjusting the column stretch factors
        self.grid_layout.setColumnStretch(0, 1)  # Repository panel
        self.grid_layout.setColumnStretch(1, 3)  # Web view

        self.resize(1000, 600)  # Adjusted window size
        self.centerWindow()

    def centerWindow(self):
        """Center the window on the screen."""
        qr = self.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def fetch_profile_data(self):
        """Fetch the profile data from the GitHub API."""
        try:
            response = requests.get(f"{self.API_URL}{self.username}")
            if response.status_code == 200:
                self.profile_data = response.json()
                self.update_profile_info()
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch profile data.")
        except requests.RequestException:
            QMessageBox.critical(self, "Error", "Network error.")

    def fetch_repos_data(self):
        """Fetch the repositories data from the GitHub API."""
        try:
            response = requests.get(f"{self.API_URL}{self.username}/repos?per_page={self.PER_PAGE}&page={self.current_page}")
            if response.status_code == 200:
                self.repos_data = response.json()
                self.update_repos_info()
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch repositories.")
        except requests.RequestException:
            QMessageBox.critical(self, "Error", "Network error.")

    def update_profile_info(self):
        """Update the profile information label."""
        if self.profile_data:
            profile_info = (
                f"Username: {self.profile_data['login']}\n"
                f"URL: {self.profile_data['html_url']}\n"
                f"Repositories: {self.profile_data['public_repos']}\n"
                f"Followers: {self.profile_data['followers']}\n"
                f"Following: {self.profile_data['following']}"
            )
            self.profile_label.setText(profile_info)

    def update_repos_info(self):
        """Update the repositories information in the scroll area."""
        container = QWidget()
        layout = QVBoxLayout()

        button_style = "QPushButton { font-weight: bold; color: white; background-color: black; border: 2px solid lightpurple; }"

        for repo in self.repos_data:
            repo_button = QPushButton(repo['name'])
            repo_button.clicked.connect(partial(self.show_repo_details, repo))
            repo_button.setStyleSheet(button_style)
            layout.addWidget(repo_button)

        container.setLayout(layout)
        self.repos_area.setWidget(container)
        self.page_label.setText(f"Page {self.current_page}")

    def show_repo_details(self, repo_data):
        dialog = RepoDetailsDialog(repo_data)
        dialog.exec_()

    def open_repo(self, url):
        """Open the repository URL in the web view."""
        self.webview.load(QUrl(url))

    def view_profile(self):
        """Open the user's profile URL in the web view."""
        self.webview.load(QUrl(self.profile_data['html_url']))

    def prev_page(self):
        """Go to the previous page of repositories."""
        if self.current_page > 1:
            self.current_page -= 1
            self.fetch_repos_data()

    def next_page(self):
        """Go to the next page of repositories."""
        if self.current_page * self.PER_PAGE < self.profile_data['public_repos']:
            self.current_page += 1
            self.fetch_repos_data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = GitHubApp("LoQiseaking69")
    mainWin.show()
    sys.exit(app.exec_())