import os
import sqlite3
import sys

import qrcode
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from random import choice
import hashlib

import create_dotenv
import random
import string
import re
import ctypes
import webbrowser

try:
    os.mkdir("Usersdb")
except OSError:
    pass
load_dotenv('Usersdb/.env')

app = QApplication(sys.argv)


def distribute_elements(list1, list2):
    result_lists = [[list1[i], list2[i]] for i in range(min(len(list1), len(list2)))]
    return result_lists


# Table model
class TableModel(QAbstractTableModel):
    def __init__(self, data, headers):
        super(TableModel, self).__init__()
        self.data = data
        self.headers = headers

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self.data)

    def columnCount(self, index):
        return 2

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self.headers[section])


class CheckWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedSize(750, 420)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: rgb(255,255,255)")

        self.icon = QLabel(self)
        self.icon.setFixedSize(30, 35)
        self.icon.move(6, 20)
        self.icon.setScaledContents(True)
        self.icon.setPixmap(QPixmap('pictures/safe_icon.png'))

        self.name = QLabel("Проверить пароль на надежность", self)
        self.name.setFixedSize(525, 35)
        self.name.move(50, 20)
        self.name.setStyleSheet("background-color: rgb(255,255,255); color: rgb(0, 0, 0)")
        self.name.setFont(QFont("Inter", 20))

        self.label = QLabel("Пароль", self)
        self.label.setFixedSize(142, 39)
        self.label.move(33, 140)
        self.label.setStyleSheet("background-color: rgb(255,255,255); color: rgb(115, 115, 115)")

        self.lineedit = QLineEdit(self)
        self.lineedit.setFixedSize(318, 75)
        self.lineedit.move(33, 175)
        self.lineedit.setFont(QFont("Arial", 22))
        self.lineedit.setStyleSheet("background-color: rgb(217, 217, 217)")

        self.visualisation = QLabel(self)
        self.visualisation.setFixedSize(242, 27)
        self.visualisation.move(448, 100)
        self.visualisation.setScaledContents(True)

        self.check_button = QPushButton("Проверить", self)
        self.check_button.setFixedSize(142, 35)
        self.check_button.move(404, 350)
        self.check_button.setStyleSheet("background-color: #E74D3C; color: rgb(255, 255, 255); border-radius: 12;")
        self.check_button.clicked.connect(self.check_pass)

        self.cancel_button = QPushButton("Отмена", self)
        self.cancel_button.setFixedSize(142, 35)
        self.cancel_button.move(197, 350)
        self.cancel_button.setStyleSheet("background-color: #E74D3C; color: rgb(255, 255, 255); border-radius: 12;")
        self.cancel_button.clicked.connect(self.close)

        self.lencheck = QCheckBox('Cодержит более 12 символов', self)
        self.lencheck.move(448, 140)
        self.lencheck.setFixedSize(185, 50)
        self.lencheck.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.registercheck = QCheckBox('Cодержит буквы разного регистра', self)
        self.registercheck.move(448, 180)
        self.registercheck.setFixedSize(285, 50)
        self.registercheck.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.speccheck = QCheckBox('Cодержит цифры и специальные символы \n (~ ... :|?<>=)', self)
        self.speccheck.move(448, 220)
        self.speccheck.setFixedSize(285, 50)
        self.speccheck.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.commoncheck = QCheckBox('Не является частым паролем', self)
        self.commoncheck.move(448, 270)
        self.commoncheck.setFixedSize(185, 50)
        self.commoncheck.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def check_pass(self):
        horrible = QPixmap('pictures/1.png')
        medium = QPixmap('pictures/3.png')
        strong = QPixmap('pictures/4.png')
        excellent = QPixmap('pictures/5.png')

        worst = ['12345',
                 '123456',
                 '123456789',
                 'test1',
                 'password',
                 '12345678',
                 'zinch',
                 'g_czechout',
                 'asdf',
                 'qwerty',
                 '1234567890',
                 '1234567',
                 'Aa123456.',
                 'iloveyou',
                 '1234',
                 'abc123',
                 '111111',
                 '123123',
                 'dubsmash',
                 'test',
                 'princess',
                 'qwertyuiop',
                 'sunshine',
                 'BvtTest123',
                 '11111',
                 'ashley',
                 '00000',
                 '000000',
                 'password1',
                 'monkey',
                 'livetest',
                 '55555',
                 'soccer',
                 'charlie',
                 'asdfghjkl',
                 '654321',
                 'family',
                 'michael',
                 '123321',
                 'football',
                 'baseball',
                 'q1w2e3r4t5y6',
                 'nicole',
                 'jessica',
                 'purple',
                 'shadow',
                 'hannah',
                 'chocolate',
                 'michelle',
                 'daniel',
                 'maggie',
                 'qwerty123',
                 'hello',
                 '112233',
                 'jordan',
                 'tigger',
                 '666666',
                 '987654321',
                 'superman',
                 '12345678910',
                 'summer',
                 '1q2w3e4r5t',
                 'fitness',
                 'bailey',
                 'zxcvbnm',
                 'fuckyou',
                 '121212',
                 'buster',
                 'butterfly',
                 'dragon',
                 'jennifer',
                 'amanda',
                 'justin',
                 'cookie',
                 'basketball',
                 'shopping',
                 'pepper',
                 'joshua',
                 'hunter',
                 'ginger',
                 'matthew',
                 'abcd1234',
                 'taylor',
                 'samantha',
                 'whatever',
                 'andrew',
                 '1qaz2wsx3edc',
                 'thomas',
                 'jasmine',
                 'animoto',
                 'madison',
                 '0987654321',
                 '54321',
                 'flower',
                 'Password',
                 'maria',
                 'babygirl',
                 'lovely',
                 'sophie',
                 'Chegg123']

        self.speccheck.setChecked(False)
        self.registercheck.setChecked(False)
        self.lencheck.setChecked(False)
        self.commoncheck.setChecked(False)

        password = self.lineedit.text()

        password_scores = {0: 'None', 1: 'Horrible', 2: 'Medium', 3: 'Strong', 4: 'Excellent'}
        password_strength = dict.fromkeys(['register', 'num_spec', 'lenght', 'common'], False)
        if re.search(r'[A-Z]', password) and re.search(r'[a-z]', password):
            password_strength['register'] = True
            self.registercheck.setChecked(True)
        if re.search(r'[0-9]', password) and re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password):
            password_strength['num_spec'] = True
            self.speccheck.setChecked(True)
        if len(password) > 12:
            password_strength['lenght'] = True
            self.lencheck.setChecked(True)
        if password not in worst:
            password_strength['common'] = True
            self.commoncheck.setChecked(True)

        score = len([b for b in password_strength.values() if b])

        if score == 1 or (password in worst):
            self.visualisation.setFixedSize(60, 27)
            self.visualisation.setPixmap(horrible)
            self.commoncheck.setChecked(False)
            self.lencheck.setChecked(False)
            self.speccheck.setChecked(False)
            self.registercheck.setChecked(False)
        elif score == 2:
            self.visualisation.setFixedSize(120, 27)
            self.visualisation.setPixmap(medium)
        elif score == 3:
            self.visualisation.setFixedSize(180, 27)
            self.visualisation.setPixmap(strong)
        elif score == 4:
            self.visualisation.setFixedSize(240, 27)
            self.visualisation.setPixmap(excellent)


class AddPassword(QWidget):
    def __init__(self,login,cipher_main,main_table):
        super().__init__()

        self.login = login
        self.cipher_main = cipher_main

        self.setFixedSize(750, 420)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: rgb(255,255,255)")

        self.name = QLabel("Изменить пароль", self)
        self.name.setFixedSize(277, 39)
        self.name.move(23, 24)
        self.name.setStyleSheet("background-color: rgb(255,255,255); color: rgb(0, 0, 0)")
        self.name.setFont(QFont("Inter", 20))

        self.service_name = QLabel("Название/ссылка сервиса", self)
        self.service_name.setFixedSize(195, 25)
        self.service_name.move(28, 114)
        self.service_name.setStyleSheet("background-color: rgb(255,255,255); color: rgb(115, 115, 115)")
        self.service_name.setFont(QFont("Inter", 10))

        self.password_name = QLabel("Пароль", self)
        self.password_name.setFixedSize(195, 25)
        self.password_name.move(396, 114)
        self.password_name.setStyleSheet("background-color: rgb(255,255,255); color: rgb(115, 115, 115)")
        self.password_name.setFont(QFont("Inter", 10))

        self.service_line = QLineEdit(self)
        self.service_line.setFixedSize(298, 47)
        self.service_line.move(28, 146)
        self.service_line.setFont(QFont("Arial", 18))
        self.service_line.setStyleSheet("background-color: rgb(217, 217, 217)")

        self.password_line = QLineEdit(self)
        self.password_line.setFixedSize(298, 47)
        self.password_line.move(396, 146)
        self.password_line.setFont(QFont("Arial", 18))
        self.password_line.setStyleSheet("background-color: rgb(217, 217, 217)")

        self.generate_button = QPushButton("Сгенерировать случайный пароль", self)
        self.generate_button.setIcon(QIcon('pictures/safe_icon.png'))
        self.generate_button.setIconSize(QSize(30,30))
        self.generate_button.setFixedSize(400, 30)
        self.generate_button.move(28, 238)
        self.generate_button.setStyleSheet("background: transparent; border: none; text-align: left;")
        self.generate_button.clicked.connect(self.generate_pass)

        self.save_button=QPushButton("Добавить",self)
        self.save_button.setFixedSize(142, 35)
        self.save_button.move(404, 350)
        self.save_button.setStyleSheet("background-color: #E74D3C; color: rgb(255, 255, 255); border-radius: 12;")
        self.save_button.clicked.connect(lambda :self.save_pass(self.login,self.cipher_main,main_table))

        self.cancel_button = QPushButton("Отмена", self)
        self.cancel_button.setFixedSize(142, 35)
        self.cancel_button.move(197, 350)
        self.cancel_button.setStyleSheet("background-color: #E74D3C; color: rgb(255, 255, 255); border-radius: 12;")
        self.cancel_button.clicked.connect(self.close)

    def save_pass(self,login,cipher_main,main_table):
        service = self.service_line.text()
        password = self.password_line.text()

        if service == '' or password == '':
            QMessageBox.information(self, "Пустые поля", "Введите данные")
            self.update_table(login,cipher_main,main_table)
        else:
            key = Fernet.generate_key()
            encrypted_key = cipher_main.encrypt(key)

            cipher = Fernet(key)

            encrypted_password = cipher.encrypt(password.encode())

            connection = sqlite3.connect(f'Usersdb/{login}.db')
            cursor = connection.cursor()

            try:

                cursor.execute('INSERT INTO services VALUES (?, ?, ?)',
                               (service, encrypted_password, encrypted_key))
            except sqlite3.OperationalError:
               QMessageBox.information(self,"Ошибка","Не удалось сохранить пароль. Попробуйте еще раз.")

            connection.commit()
            connection.close()
        self.update_table(login,cipher_main,main_table)
    def generate_pass(self):
        charlist = ''
        charlist += string.digits
        charlist += string.ascii_letters
        charlist += "-_."
        password = ''
        for i in range(20):
            randomchar = random.choice(charlist)
            password += randomchar
        self.password_line.setText(password)

    def update_table(self,login,cipher_main,main_table):
        connection = sqlite3.connect(f'Usersdb/{login}.db')
        cursor = connection.cursor()

        query = "SELECT service FROM services"
        cursor.execute(query)
        service_column = [row[0] for row in cursor.fetchall()]

        query = "SELECT password FROM services"
        cursor.execute(query)
        column_password_encrypted = [row[0] for row in cursor.fetchall()]

        query = "SELECT key FROM services"
        cursor.execute(query)
        key_column_encrypted = [row[0] for row in cursor.fetchall()]

        column_password_decrypted = []
        key_column = []

        if len(key_column_encrypted) != 0:
            for i in range(len(key_column_encrypted)):
                # Key decrypt
                decrypted_1 = cipher_main.decrypt(key_column_encrypted[i]).decode()
                key_column.append(decrypted_1)

                # Password decrypt
                cipher = Fernet(key_column[i])
                decrypted_2 = cipher.decrypt(column_password_encrypted[i]).decode()
                column_password_decrypted.append(decrypted_2)

        cursor.close()
        connection.close()

        list_4_table = distribute_elements(service_column, column_password_decrypted)

        headers_names = ['Сервис', 'Пароль']

        # Create table model and resize headers
        table_model = TableModel(list_4_table, headers_names)
        main_table.setModel(table_model)

        header = main_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

class Window(QMainWindow):
    front_widget = None

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setFixedSize(1024, 720)
        self.setWindowTitle("Passtorage")

        self.setWindowIcon(QIcon('pictures/window-icon.png'))

        self.CheckWindow = None

        # Connect dotenv
        try:
            SECRET = os.getenv('SECRET')
            SECRET = SECRET.encode()
            self.cipher_main = Fernet(SECRET)
        except AttributeError:
            create_dotenv.create()
            self.msg_box.information(None, "Первый запуск", "Создан уникальный ключ перезапустите программу")
            exec(exit(0))

        # Widgets
        self.msg_box = QMessageBox(self)
        self.msg_box.setStyleSheet("background-color: rgb(255,255,255);")

        self.name_label = QLabel("МЕНЕДЖЕР ПАРОЛЕЙ", self)
        self.name_label.setFixedSize(497, 54)
        self.name_label.move(85, 27)
        self.name_label.setStyleSheet("color: rgb(255, 255, 255); background-color: rgba(255,255,255,0)")
        self.name_label.setFont(QFont("Inter", 25))

        self.return_button = QPushButton(self)
        self.return_button.setFixedSize(57, 57)
        self.return_button.move(20, 27)
        self.return_button.setStyleSheet("border: none; background-color: rgba(255,255,255,0)")
        self.return_button.setIcon(QIcon("pictures/left-arrow.png"))
        self.return_button.setIconSize(QSize(57, 57))
        self.return_button.clicked.connect(lambda: self.widgets_state('select'))
        self.return_button.hide()

        self.logout_button = QPushButton(self)
        self.logout_button.setFixedSize(57, 57)
        self.logout_button.move(933, 20)
        self.logout_button.setStyleSheet("border: none;background-color: rgba(255,255,255,0)")
        self.logout_button.setIcon(QIcon("pictures/user-logout.png"))
        self.logout_button.setIconSize(QSize(57, 57))
        self.logout_button.clicked.connect(self.logout)
        self.logout_button.hide()

        self.login_widgets()
        self.selection_widgets()
        self.table_widgets()
        self.qr_widgets()
        # self.passgen_widgets()
        # self.passcheck_widgets()

        # Change status

        self.state = 'login'
        self.widgets_state("login")

        # Get from db
        connect_db = sqlite3.connect("Accounts.db")
        cursor = connect_db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS Accounts (login TEXT, password TEXT)')
        connect_db.commit()
        connect_db.close()

    def selection_widgets(self):
        self.black_frame = QFrame(self)
        self.black_frame.move(0, 0)
        self.black_frame.setFixedSize(1024, 96)
        self.black_frame.setStyleSheet("background-color: rgb(21,21,21);")

        self.createqr = QPushButton("Создать QR код", self)
        self.createqr.move(585, 270)
        self.createqr.setFixedSize(380, 288)
        self.createqr.clicked.connect(lambda: self.widgets_state("qr"))
        self.createqr.setStyleSheet("background-color: #3398DB;")

        self.tableview = QPushButton("Сохраненные пароли", self)
        self.tableview.move(88, 270)
        self.tableview.setFixedSize(380, 288)
        self.tableview.clicked.connect(lambda: self.widgets_state("table"))
        self.tableview.setStyleSheet("background-color: #3398DB;")

        self.createqr.hide()
        self.tableview.hide()

    def login_widgets(self):

        self.white_back_x = 69
        self.white_back_y = 130
        self.white_back = QFrame(self)
        self.white_back.setFixedSize(890, 478)
        self.white_back.move(self.white_back_x, self.white_back_y)
        self.white_back.setStyleSheet("background-color: rgb(255,255,255); border-radius: 33")

        self.log_name = QLabel('Вход', self)
        self.log_name.setFixedSize(271, 54)
        self.log_name.move(self.white_back_x + 90, self.white_back_y + 48)
        self.log_name.setStyleSheet("background-color: rgb(255,255,255)")
        self.log_name.setFont(QFont("Inter", 30, QFont.Weight.Medium))

        self.login_label = QLabel('логин', self)
        self.login_label.setFixedSize(89, 30)
        self.login_label.move(self.white_back_x + 90, self.white_back_y + 137)
        self.login_label.setStyleSheet("background-color: rgb(255,255,255); color: rgb(115, 115, 115)")
        self.login_label.setFont(QFont("Inter", 14))

        self.login_input = QLineEdit(self)
        self.login_input.setFixedSize(594, 44)
        self.login_input.move(self.white_back_x + 90, self.white_back_y + 184)
        self.login_input.setStyleSheet("background-color: rgb(217, 217, 217)")

        self.password_label = QLabel('пароль', self)
        self.password_label.setFixedSize(89, 30)
        self.password_label.move(self.white_back_x + 90, self.white_back_y + 245)
        self.password_label.setStyleSheet("background-color: rgb(255,255,255); color: rgb(115, 115, 115)")
        self.password_label.setFont(QFont("Inter", 14))

        self.password_input = QLineEdit(self)
        self.password_input.setFixedSize(594, 44)
        self.password_input.move(self.white_back_x + 90, self.white_back_y + 292)
        self.password_input.setStyleSheet("background-color: rgb(217, 217, 217)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.confirm_button = QPushButton("Подтвердить", self)
        self.confirm_button.setFixedSize(201, 50)
        self.confirm_button.move(self.white_back_x + 329, self.white_back_y + 371)
        self.confirm_button.setStyleSheet("background-color: #E74D3C; color: rgb(255, 255, 255); border-radius: 24;")
        self.confirm_button.clicked.connect(self.confirm)

        self.change_button = QPushButton("Регистрация", self)
        self.change_button.setFixedSize(122, 50)
        self.change_button.move(self.white_back_x + 740, self.white_back_y + 23)
        self.change_button.setStyleSheet("background-color: #E74D3C; color: rgb(255, 255, 255); border: none")
        self.change_button.clicked.connect(self.change_status)

        self.hide_password_button = QPushButton(self)
        self.hide_password_button.setIcon(QIcon('pictures/eye-icon.png'))
        self.hide_password_button.setFixedSize(25, 25)
        self.hide_password_button.move(self.white_back_x + 647, self.white_back_y + 303)
        self.hide_password_button.setStyleSheet("background: transparent; border: none")
        self.hide_password_button.clicked.connect(self.hide_password)

    def qr_widgets(self):
        self.textedit = QLineEdit(self)
        self.textedit.move(200, 525)
        self.textedit.setFixedSize(600, 30)
        self.textedit.setStyleSheet("background-color: rgb(217, 217, 217)")

        self.image = QLabel(self)
        self.image.move(350, 150)
        self.image.setFixedSize(300, 300)
        self.image.setScaledContents(True)

        self.qrcreate = QPushButton("Создать", self)
        self.qrcreate.move(150, 600)
        self.qrcreate.setFixedSize(263, 54)
        self.qrcreate.setStyleSheet("background-color: #E74D3C; color: rgb(255, 255, 255); border-radius: 24;")
        self.qrcreate.clicked.connect(self.qr_generator)

        self.saveqr = QPushButton("Сохранить", self)
        self.saveqr.move(600, 600)
        self.saveqr.setFixedSize(263, 54)
        self.saveqr.setStyleSheet("background-color: #E74D3C; color: rgb(255, 255, 255); border-radius: 24;")
        self.saveqr.clicked.connect(self.qr_save)

        self.textedit.hide()
        self.image.hide()
        self.qrcreate.hide()
        self.saveqr.hide()

    def table_widgets(self):
        self.main_table = QTableView(self)
        self.main_table.setFixedSize(1024, 546)
        self.main_table.move(0, 96)
        self.main_table.doubleClicked.connect(self.open_link)
        self.main_table.keyPressEvent = self.delete_row

        self.add_button = QPushButton(self)
        self.add_button.setFixedSize(30, 30)
        self.add_button.move(40, 670)
        self.add_button.setIcon(QIcon("pictures/add-icon.png"))
        self.add_button.setIconSize(QSize(30, 30))
        self.add_button.setStyleSheet("background: transparent; border: none")
        self.add_button.clicked.connect(self.add_2_table)

        self.delete_button = QPushButton(self)
        self.delete_button.setFixedSize(30, 30)
        self.delete_button.move(120, 670)
        self.delete_button.setIcon(QIcon("pictures/remove-icon.png"))
        self.delete_button.setIconSize(QSize(30, 30))
        self.delete_button.setStyleSheet("background: transparent; border: none")
        self.delete_button.clicked.connect(self.delete_from_table)

        self.find_button = QPushButton(self)
        self.find_button.setFixedSize(30, 30)
        self.find_button.move(200, 670)
        self.find_button.setIcon(QIcon("pictures/find-icon.png"))
        self.find_button.setIconSize(QSize(30, 30))
        self.find_button.setStyleSheet("background: transparent; border: none")
        self.find_button.clicked.connect(self.find_needed_password)

        self.check_button = QPushButton(self)
        self.check_button.setFixedSize(30, 30)
        self.check_button.move(280, 670)
        self.check_button.setIcon(QIcon("pictures/check-icon.png"))
        self.check_button.setIconSize(QSize(30, 30))
        self.check_button.setStyleSheet("background: transparent; border: none")
        self.check_button.clicked.connect(self.check_pass)

        self.main_table.hide()
        self.check_button.hide()
        self.add_button.hide()
        self.delete_button.hide()

    def passgen_widgets(self):
        self.numcheck_gen = QCheckBox("Цифры", self)
        self.numcheck_gen.move(40, 160)
        self.numcheck_gen.setFixedSize(71, 21)

        self.capletters = QCheckBox("Прописные буквы", self)
        self.capletters.move(40, 70)
        self.capletters.setFixedSize(130, 21)

        self.smallletters = QCheckBox("Заглавные буквы", self)
        self.smallletters.move(40, 100)
        self.smallletters.setFixedSize(130, 21)

        self.specsymbols = QCheckBox("Спец. символы", self)
        self.specsymbols.move(40, 130)
        self.specsymbols.setFixedSize(101, 21)

        self.lenght_label = QLabel("Длина пароля:", self)
        self.lenght_label.move(40, 190)
        self.lenght_label.setFixedSize(81, 16)

        self.lenght = QSpinBox(self)
        self.lenght.move(130, 190)
        self.lenght.setFixedSize(71, 22)

        self.listview = QListWidget(self)
        self.listview.move(290, 30)
        self.listview.setFixedSize(281, 431)

        self.generate = QPushButton("Сгенерировать", self)
        self.generate.setFixedSize(91, 31)
        self.generate.move(40, 412)
        self.generate.clicked.connect(self.generate_pass)

        self.clear = QPushButton("Очистить", self)
        self.clear.setFixedSize(91, 31)
        self.clear.move(150, 412)
        self.clear.clicked.connect(lambda: self.listview.clear())

        self.numcheck_gen.hide()
        self.capletters.hide()
        self.smallletters.hide()
        self.specsymbols.hide()
        self.lenght_label.hide()
        self.lenght.hide()
        self.listview.hide()
        self.generate.hide()
        self.clear.hide()

    def passcheck_widgets(self):
        self.pass_line = QLineEdit(self)
        self.pass_line.setPlaceholderText("Введите пароль для проверки...")
        self.pass_line.move(70, 100)
        self.pass_line.setFixedSize(450, 31)

        self.safety_label = QLabel(self)
        self.safety_label.move(70, 170)
        self.safety_label.setScaledContents(True)

        self.safety_label_text = QLabel(self)
        self.safety_label_text.move(240, 230)
        self.safety_label_text.setFixedSize(120, 16)

        self.checkbtn = QPushButton("Проверить", self)
        self.checkbtn.move(220, 300)
        self.checkbtn.setFixedSize(151, 61)
        self.checkbtn.clicked.connect(self.check_pass)

        self.numcheck = QCheckBox('Цифры', self)
        self.numcheck.move(80, 260)
        self.numcheck.setFixedSize(70, 17)
        self.numcheck.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.smallcheck = QCheckBox('Строчные буквы', self)
        self.smallcheck.move(170, 260)
        self.smallcheck.setFixedSize(116, 17)
        self.smallcheck.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.bigcheck = QCheckBox('Заглавные буквы', self)
        self.bigcheck.move(310, 260)
        self.bigcheck.setFixedSize(116, 17)
        self.bigcheck.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.speccheck = QCheckBox('Спец. символы', self)
        self.speccheck.move(440, 260)
        self.speccheck.setFixedSize(106, 17)
        self.speccheck.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.pass_line.hide()
        self.safety_label.hide()
        self.safety_label_text.hide()
        self.checkbtn.hide()
        self.numcheck.hide()
        self.smallcheck.hide()
        self.bigcheck.hide()
        self.speccheck.hide()

    def widgets_state(self, state):
        if state == "login":
            self.setStyleSheet("background-color: rgb(21, 21, 21);")

            self.find_button.hide()
            self.black_frame.hide()
            self.check_button.hide()

            self.white_back.show()
            self.login_label.show()
            self.log_name.show()
            self.login_input.show()
            self.password_label.show()
            self.password_input.show()
            self.confirm_button.show()
            self.change_button.show()
            self.hide_password_button.show()

            self.createqr.hide()
            self.tableview.hide()
            self.logout_button.hide()
        if state == "table":
            self.black_frame.show()
            self.main_table.show()
            self.add_button.show()
            self.delete_button.show()
            self.find_button.show()
            self.return_button.show()
            self.check_button.show()

            self.createqr.hide()
            self.tableview.hide()
        if state == "qr":
            self.black_frame.show()
            self.textedit.show()
            self.image.show()
            self.qrcreate.show()
            self.saveqr.show()
            self.return_button.show()

            self.createqr.hide()
            self.tableview.hide()
        if state == "select":
            self.setStyleSheet("background-color: rgb(237, 241, 242);")
            self.black_frame.show()
            self.logout_button.show()
            self.logout_button.raise_()
            self.name_label.raise_()
            self.return_button.raise_()

            self.log_name.hide()
            self.white_back.hide()
            self.login_input.hide()
            self.password_label.hide()
            self.password_input.hide()
            self.confirm_button.hide()
            self.change_button.hide()
            self.login_label.hide()
            self.hide_password_button.hide()
            self.check_button.hide()

            self.main_table.hide()
            self.add_button.hide()
            self.delete_button.hide()
            self.find_button.hide()
            self.return_button.hide()

            self.textedit.hide()
            self.image.hide()
            self.qrcreate.hide()
            self.saveqr.hide()

            self.createqr.show()
            self.tableview.show()

    def hide_password(self):
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def change_status(self):
        if self.state == 'login':
            self.log_name.setText('Регистрация')
            self.change_button.setText("Вход")
            self.change_button.move(self.white_back_x + 692, self.white_back_y + 23)
            self.state = 'register'

        elif self.state == 'register':
            self.log_name.setText('Вход')
            self.change_button.setText("Регистрация")
            self.change_button.move(self.white_back_x + 740, self.white_back_y + 23)
            self.state = 'login'

    def confirm(self):
        self.login = self.login_input.text()
        password = self.password_input.text()
        if self.state == 'register':

            conn = sqlite3.connect('Accounts.db')
            cursor = conn.cursor()

            hashed_login = hashlib.sha512(self.login.encode('UTF-8')).hexdigest()
            hashed_password = hashlib.sha512(password.encode('UTF-8')).hexdigest()

            # Check if name is engaged
            cursor.execute('SELECT * FROM Accounts WHERE login=?', (hashed_login,))

            if cursor.fetchone() is not None:
                self.msg_box.information(None, "Пользователь уже существует",
                                         "Пользователь с таким именем уже существует")

            elif self.login != '' and password != '':
                cursor.execute('INSERT INTO Accounts VALUES (?, ?)', (hashed_login, hashed_password))
                conn.commit()

                self.msg_box.information(None, "Успешно", "Регистрация прошла успешно")

                self.widgets_state("select")

                self.state = 'register'
                self.change_status()
            else:
                self.msg_box.warning(None, "Ошибка", "Введите логин и пароль для регистрации")

        elif self.state == 'login':

            hashed_login = hashlib.sha512(self.login.encode('UTF-8')).hexdigest()
            hashed_password = hashlib.sha512(password.encode('UTF-8')).hexdigest()

            # Find user
            conn = sqlite3.connect('Accounts.db')
            cursor = conn.cursor()

            cursor.execute('SELECT password FROM Accounts WHERE login=?', (hashed_login,))
            result = cursor.fetchone()

            if result is None:
                self.msg_box.information(None, "Не найдено", "Пользователь не найден")
                return

            if hashed_password == result[0]:

                self.msg_box.information(None, "Вход", "Вход выполнен успешно")

                # Create services passwords db for user

                isExists = os.path.exists('Usersdb')
                if not isExists:
                    os.makedirs('Usersdb')
                conn_user = sqlite3.connect(f'Usersdb/{self.login}.db')
                cursor_user = conn_user.cursor()

                cursor_user.execute('CREATE TABLE IF NOT EXISTS services (service TEXT, password TEXT, key BLOB)')

                conn_user.commit()
                conn_user.close()

                # Show main widgets

                self.widgets_state("select")

                # Show passwords

                self.create_table_4_user()
            else:
                self.msg_box.warning(None, "Вход не выполнен", "Неверный логин или пароль")

    def create_table_4_user(self):
        # Get data

        connection = sqlite3.connect(f'Usersdb/{self.login}.db')
        cursor = connection.cursor()

        query = "SELECT service FROM services"
        cursor.execute(query)
        service_column = [row[0] for row in cursor.fetchall()]

        query = "SELECT password FROM services"
        cursor.execute(query)
        column_password_encrypted = [row[0] for row in cursor.fetchall()]

        query = "SELECT key FROM services"
        cursor.execute(query)
        key_column_encrypted = [row[0] for row in cursor.fetchall()]

        column_password_decrypted = []
        key_column = []

        if len(key_column_encrypted) != 0:
            for i in range(len(key_column_encrypted)):
                # Key decrypt
                decrypted_1 = self.cipher_main.decrypt(key_column_encrypted[i]).decode()
                key_column.append(decrypted_1)

                # Password decrypt
                cipher = Fernet(key_column[i])
                decrypted_2 = cipher.decrypt(column_password_encrypted[i]).decode()
                column_password_decrypted.append(decrypted_2)

        cursor.close()
        connection.close()

        # Create list for table

        list_4_table = distribute_elements(service_column, column_password_decrypted)

        headers_names = ['Сервис', 'Пароль']

        # Create table model and resize headers
        table_model = TableModel(list_4_table, headers_names)
        self.main_table.setModel(table_model)

        header = self.main_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def logout(self):
        confirmation = self.msg_box.question(None, "Подтверждение выхода", "Вы уверены, что хотите выйти?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirmation == QMessageBox.StandardButton.Yes:
            self.login_input.setText('')
            self.password_input.setText('')

            self.widgets_state("login")

            self.main_table.hide()
            self.add_button.hide()
            self.delete_button.hide()
            self.find_button.hide()

            self.createqr.hide()
            self.tableview.hide()

            self.textedit.hide()
            self.image.hide()
            self.qrcreate.hide()
            self.saveqr.hide()

    def add_2_table(self):
        self.AddPassword = AddPassword(self.login,self.cipher_main,self.main_table)
        self.AddPassword.show()

        self.create_table_4_user()

    def delete_from_table(self):
        dialog = QDialog()
        dialog.resize(300, 100)
        Vbox_layout = QVBoxLayout(dialog)

        service_line = QLineEdit()
        service_line.setPlaceholderText("Введите название сервиса для его удаления")

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        Vbox_layout.addWidget(service_line)
        Vbox_layout.addWidget(button_box)

        pressed_button = dialog.exec()

        if pressed_button == QDialog.DialogCode.Accepted and service_line.text() != '':
            service = service_line.text()

            connect = sqlite3.connect(f'Usersdb/{self.login}.db')
            cursor = connect.cursor()

            confirmation = self.msg_box.question(None, "Подтверждение удаления",
                                                 "Вы уверены, что хотите удалить пароль от этого сервиса?",
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, )
            if confirmation == QMessageBox.StandardButton.Yes:
                try:
                    cursor.execute('DELETE FROM services WHERE service = ?', (service,))
                except sqlite3.OperationalError:

                    self.msg_box.warning(None, "Удаление не выполнено", "Такого названия не существует в таблице")

            connect.commit()
            connect.close()

        elif pressed_button != QDialog.DialogCode.Rejected:
            self.msg_box.warning(None, "Пустые поля", "Введите данные")

            self.delete_from_table()

        self.create_table_4_user()

    def find_needed_password(self):
        dialog = QDialog()
        dialog.resize(350, 100)
        dialog.setStyleSheet("background-color: rgb(255,255,255);")
        Vbox_layout = QVBoxLayout(dialog)

        service_line = QLineEdit()
        service_line.setPlaceholderText("Введите название сервиса для поиска пароля от него")

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        Vbox_layout.addWidget(service_line)
        Vbox_layout.addWidget(button_box)

        pressed_button = dialog.exec()
        if pressed_button == QDialog.DialogCode.Accepted and service_line.text() != '':
            try:
                service = service_line.text()

                connect = sqlite3.connect(f'Usersdb/{self.login}.db')
                cursor = connect.cursor()

                cursor.execute('SELECT password FROM services WHERE service=?', (service,))
                result = cursor.fetchone()[-1]
                cursor.execute('SELECT key FROM services WHERE service=?', (service,))
                key = self.cipher_main.decrypt(cursor.fetchone()[-1]).decode()
                cipher = Fernet(key)

                if result is None:
                    self.msg_box.information(None, "Не найдено", "Записанный пароль не найден")
                    return
                else:
                    decrypted_password = cipher.decrypt(result).decode()

                    self.msg_box.information(None, "Найден пароль", f"Пароль от {service}: {decrypted_password}")

                connect.commit()
                connect.close()
            except TypeError:
                self.msg_box.information(None, "Не найдено", "Записанный пароль не найден")
                self.find_needed_password()

        elif pressed_button != QDialog.DialogCode.Rejected:
            self.msg_box.information(None, "Пустые поля", "Введите данные")
            self.find_needed_password()

            self.create_table_4_user()

    def qr_generator(self):
        self.widgets_state("qr")

        text = self.textedit.text()
        qr = qrcode.QRCode(border=2)
        qr.add_data(text)
        image = qr.make_image(back_color=(0, 0, 0), fill_color="black")
        image.save("qr_code_cache.png")
        pixmap = QPixmap("qr_code_cache.png")

        self.image.setPixmap(pixmap)
        os.remove("qr_code_cache.png")

    def qr_save(self):
        path = os.path
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", f"{path}/qrcode.png",
                                                  "PNG (*.png);;JPEG (*.jpg;*.jpeg;*.jpe;*.jfif)")
        try:
            text = self.textedit.text()
            image = qrcode.make(text)
            image.save(fileName)
        except FileNotFoundError:
            return

    def check_pass(self):
        self.CheckWindow = CheckWindow()
        self.CheckWindow.show()

    def select_file(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "Текстовые файлы (*.txt)")
        file = open(fileName)
        self.file_content = file.read()

    def open_link(self, item):
        if item.column() == 0:
            index = self.main_table.selectionModel().currentIndex()
            text = index.sibling(index.row(), index.column()).data()
            webbrowser.open(text)

    def delete_row(self, e):
        if e.key() == Qt.Key.Key_Delete:
            index = self.main_table.selectionModel().currentIndex()
            service = index.sibling(index.row(), index.column()).data()

            connect = sqlite3.connect(f'Usersdb/{self.login}.db')
            cursor = connect.cursor()

            confirmation = self.msg_box.question(None, "Подтверждение удаления",
                                                 "Вы уверены, что хотите удалить сохранённый пароль?",
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, )
            if confirmation == QMessageBox.StandardButton.Yes:
                try:
                    cursor.execute('DELETE FROM services WHERE service = ?', (service,))
                except sqlite3.OperationalError:

                    self.msg_box.warning(None, "Удаление не выполнено", "Такого названия не существует в таблице")

            connect.commit()
            connect.close()
        self.create_table_4_user()

    def closeEvent(self, a0):
        QApplication.quit()


myappid = 'Nobody.Passtorage.none.0.2'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
window = Window()
window.show()
sys.exit(app.exec())
