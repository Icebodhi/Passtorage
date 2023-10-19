import sqlite3
import sys
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from cryptography.fernet import Fernet

app = QApplication(sys.argv)


class Window(QMainWindow):
    front_widget = None

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setFixedSize(600, 500)
        self.setWindowTitle("Passtorage")

        # oImage=QImage("background.png")
        # sImage=oImage.scaled(QSize(600, 500))
        # palette=QPalette()
        # palette.setBrush(QPalette.Window, QBrush(sImage))
        # self.setPalette(palette)

        # Central widget
        self.central_widget = QWidget()
        self.layout_4_widgets = QStackedLayout()

        # Button to switch

        # Login widgets
        self.login_label = QLabel('Логин:', self)
        self.login_label.setFixedSize(50, 50)
        self.login_label.move(50, 110)

        self.login_input = QLineEdit(self)
        self.login_input.setFixedSize(360, 25)
        self.login_input.move(120, 120)

        self.password_label = QLabel('Пароль:', self)
        self.password_label.setFixedSize(50, 50)
        self.password_label.move(50, 240)

        self.password_input = QLineEdit(self)
        self.password_input.setFixedSize(360, 25)
        self.password_input.move(120, 250)

        self.log_button = QPushButton("Войти", self)
        self.log_button.setFixedSize(131, 71)
        self.log_button.move(130, 350)
        self.log_button.clicked.connect(self.login)

        self.register_button = QPushButton("Зарегистрироваться", self)
        self.register_button.setFixedSize(131, 71)
        self.register_button.move(310, 350)
        self.register_button.clicked.connect(self.register)

        # Layout for widgets
        self.layout_4_widgets.addWidget(self.login_label)
        self.layout_4_widgets.addWidget(self.login_input)
        self.layout_4_widgets.addWidget(self.password_label)
        self.layout_4_widgets.addWidget(self.password_input)

        # Show widgets
        self.login_label.show()
        self.login_input.show()
        self.password_input.show()
        self.password_label.show()

        # Get text from login

        # Get from db
        connect_db = sqlite3.connect("Accounts.db")
        cursor = connect_db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS Accounts (login TEXT, password TEXT, column BLOB)')
        connect_db.commit()
        connect_db.close()

    def switch_widgets(self):
        if self.front_widget == 1:
            self.login_label.hide()
            self.login_input.hide()
            self.password_input.hide()
            self.password_label.hide()

            self.front_widget = 2
        else:
            self.login_label.show()
            self.login_input.show()
            self.password_input.show()
            self.password_label.show()

            self.front_widget = 1

    # def login(self):
    #    login = self.login_input.text()
    #    password = self.password_input.text()
    #    if not login or not password:
    #        QMessageBox.warning(self, "Введите тест", "Пожалуйста, заполните все поля")
    #        pass
    #    conn = sqlite3.connect('Accounts.db')
    #    cursor = conn.cursor()

    def register(self):
        login = self.login_input.text()
        password = self.password_input.text()

        key = Fernet.generate_key()
        cipher = Fernet(key)

        conn = sqlite3.connect('Accounts.db')
        cursor = conn.cursor()

        encrypted_password = cipher.encrypt(password.encode())

        # Проверяем, существует ли пользователь с таким именем
        cursor.execute('SELECT * FROM Accounts WHERE login=?', (login,))
        if cursor.fetchone() is not None:
            QMessageBox.information(self, "Пользователь уже существует", "Пользователь с таким именем уже существует")
        else:
            cursor.execute('INSERT INTO Accounts VALUES (?, ?, ?)', (login, encrypted_password, key))
            conn.commit()

            QMessageBox.information(self, "Успешно", "Регистрация прошла успешно")

    def login(self):
        login = self.login_input.text()
        password = self.password_input.text()

        # Создаём соединение с базой данных
        conn = sqlite3.connect('Accounts.db')
        cursor = conn.cursor()

        # Получаем зашифрованный пароль пользователя
        cursor.execute('SELECT password FROM Accounts WHERE login=?', (login,))
        result = cursor.fetchone()

        if result is None:
            QMessageBox.information(self, 'Не найдено', 'Пользователь не найден')

        # Расшифровываем пароль
        query=f"SELECT * FROM Accounts WHERE login = '{login}'"
        cursor.execute(query)
        key=cursor.fetchone()[-1]
        cipher=Fernet(key)
        decrypted_password = cipher.decrypt(result[0]).decode()

        if password == decrypted_password:
            QMessageBox.information(self, 'Вход', 'Вход выполнен успешно')
        else:
            QMessageBox.warning(self, "Вход не выполнен", "Неверный пароль")


window = Window()
window.show()
sys.exit(app.exec())
