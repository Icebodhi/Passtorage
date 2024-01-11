import os
import sqlite3
import sys

import qrcode
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import hashlib

import create_dotenv
import random
import string
import re

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


class Window(QMainWindow):
    front_widget = None

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setFixedSize(600, 500)
        self.setWindowTitle("Passtorage")

        # Connect dotenv
        try:
            SECRET = os.getenv('SECRET')
            SECRET = SECRET.encode()
            self.cipher_main = Fernet(SECRET)
        except AttributeError:
            create_dotenv.create()
            QMessageBox.information(self, 'Первый запуск', 'Создан уникальный ключ, '
                                                           'перезапустите программу')
            exec(exit(0))

        # Stacked layout
        self.layout_4_widgets = QStackedLayout()

        # Widgets

        self.login_widgets()
        self.menubar()
        self.selection_widgets()
        self.table_widgets()
        self.qr_widgets()
        self.passgen_widgets()
        self.passcheck_widgets()

        # Change widgets

        self.widgets_state("login")

        # Get from db
        connect_db = sqlite3.connect("Accounts.db")
        cursor = connect_db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS Accounts (login TEXT, password TEXT)')
        connect_db.commit()
        connect_db.close()

    def menubar(self):
        self.mbar = self.menuBar()
        usermenu = QMenu("&Пользователь", self)

        logout = QAction("Выйти из аккаунта", self)
        usermenu.addAction(logout)
        usermenu.triggered[QAction].connect(self.logout)

        navmenu = QMenu("&Навигация", self)
        goback = QAction("Вернуться", self)
        navmenu.triggered[QAction].connect(lambda: self.widgets_state("select"))

        navmenu.addAction(goback)

        self.mbar.addMenu(navmenu)
        self.mbar.addMenu(usermenu)

        self.layout_4_widgets.addWidget(self.mbar)

    def selection_widgets(self):
        self.createqr = QPushButton("Создать QR код", self)
        self.createqr.move(50, 150)
        self.createqr.setFixedSize(141, 131)
        self.createqr.clicked.connect(lambda: self.widgets_state("qr"))

        self.tableview = QPushButton("Сохраненные пароли", self)
        self.tableview.move(230, 150)
        self.tableview.setFixedSize(141, 131)
        self.tableview.clicked.connect(lambda: self.widgets_state("table"))

        self.passgen = QPushButton("Сгенерировать пароль", self)
        self.passgen.move(410, 150)
        self.passgen.setFixedSize(141, 131)
        self.passgen.clicked.connect(lambda: self.widgets_state("passgen"))

        self.passcheck = QPushButton("Проверить надежность \n пароля", self)
        self.passcheck.move(230, 300)
        self.passcheck.setFixedSize(141, 131)
        self.passcheck.clicked.connect(lambda: self.widgets_state("passcheck"))

        self.encrypt = QPushButton("Шифровка файла", self)
        self.encrypt.move(320, 300)
        self.encrypt.setFixedSize(141, 131)
        self.encrypt.clicked.connect(lambda: self.widgets_state('encrypt'))

        self.layout_4_widgets.addWidget(self.createqr)
        self.layout_4_widgets.addWidget(self.tableview)
        self.layout_4_widgets.addWidget(self.passgen)
        self.layout_4_widgets.addWidget(self.passcheck)
        self.layout_4_widgets.addWidget(self.encrypt)

    def login_widgets(self):
        self.login_label = QLabel('Логин:', self)
        self.login_label.setFixedSize(50, 50)
        self.login_label.move(50, 110)

        self.login_input = QLineEdit(self)
        self.login_input.setPlaceholderText("Введите логин...")
        self.login_input.setFixedSize(360, 25)
        self.login_input.move(120, 120)

        self.password_label = QLabel('Пароль:', self)
        self.password_label.setFixedSize(50, 50)
        self.password_label.move(50, 240)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль...")
        self.password_input.setFixedSize(360, 25)
        self.password_input.move(120, 250)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.log_button = QPushButton("Войти", self)
        self.log_button.setFixedSize(131, 71)
        self.log_button.move(130, 350)
        self.log_button.clicked.connect(self.login)

        self.register_button = QPushButton("Зарегистрироваться", self)
        self.register_button.setFixedSize(131, 71)
        self.register_button.move(310, 350)
        self.register_button.clicked.connect(self.register)

        self.layout_4_widgets.addWidget(self.login_label)
        self.layout_4_widgets.addWidget(self.login_input)
        self.layout_4_widgets.addWidget(self.password_label)
        self.layout_4_widgets.addWidget(self.password_input)

    def qr_widgets(self):
        self.textedit = QLineEdit(self)
        self.textedit.move(150, 370)
        self.textedit.setFixedSize(300, 20)

        self.image = QLabel(self)
        self.image.move(150, 40)
        self.image.setFixedSize(300, 300)
        self.image.setScaledContents(True)

        self.qrcreate = QPushButton("Создать", self)
        self.qrcreate.move(160, 420)
        self.qrcreate.setFixedSize(75, 23)
        self.qrcreate.clicked.connect(self.qr_generator)

        self.saveqr = QPushButton("Сохранить", self)
        self.saveqr.move(350, 420)
        self.saveqr.setFixedSize(75, 23)
        self.saveqr.clicked.connect(self.qr_save)

        self.layout_4_widgets.addWidget(self.textedit)
        self.layout_4_widgets.addWidget(self.image)
        self.layout_4_widgets.addWidget(self.qrcreate)
        self.layout_4_widgets.addWidget(self.saveqr)

    def table_widgets(self):
        self.main_table = QTableView(self)
        self.main_table.setFixedSize(581, 401)
        self.main_table.move(10, 25)

        self.add_button = QPushButton('Записать', self)
        self.add_button.setFixedSize(75, 23)
        self.add_button.move(20, 435)
        self.add_button.clicked.connect(self.add_2_table)

        self.delete_button = QPushButton("Удалить", self)
        self.delete_button.setFixedSize(75, 23)
        self.delete_button.move(120, 435)
        self.delete_button.clicked.connect(self.delete_from_table)

        self.find_button = QPushButton("Найти", self)
        self.find_button.setFixedSize(75, 23)
        self.find_button.move(220, 435)
        self.find_button.clicked.connect(self.find_needed_password)

        self.layout_4_widgets.addWidget(self.main_table)
        self.layout_4_widgets.addWidget(self.add_button)
        self.layout_4_widgets.addWidget(self.delete_button)

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

        self.layout_4_widgets.addWidget(self.numcheck_gen)
        self.layout_4_widgets.addWidget(self.capletters)
        self.layout_4_widgets.addWidget(self.smallletters)
        self.layout_4_widgets.addWidget(self.specsymbols)
        self.layout_4_widgets.addWidget(self.lenght_label)
        self.layout_4_widgets.addWidget(self.lenght)
        self.layout_4_widgets.addWidget(self.listview)
        self.layout_4_widgets.addWidget(self.generate)
        self.layout_4_widgets.addWidget(self.clear)

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

        self.layout_4_widgets.addWidget(self.pass_line)
        self.layout_4_widgets.addWidget(self.safety_label)
        self.layout_4_widgets.addWidget(self.checkbtn)
        self.layout_4_widgets.addWidget(self.numcheck)
        self.layout_4_widgets.addWidget(self.smallcheck)
        self.layout_4_widgets.addWidget(self.bigcheck)
        self.layout_4_widgets.addWidget(self.speccheck)

    def widgets_state(self, state):
        if state == "login":
            self.mbar.hide()
            self.find_button.hide()

            self.login_label.show()
            self.login_input.show()
            self.password_label.show()
            self.password_input.show()
            self.log_button.show()
            self.register_button.show()

            self.createqr.hide()
            self.tableview.hide()
            self.passgen.hide()
            self.passcheck.hide()
            self.encrypt.hide()
        if state == "table":
            self.main_table.show()
            self.add_button.show()
            self.delete_button.show()
            self.find_button.show()

            self.createqr.hide()
            self.tableview.hide()
            self.passgen.hide()
            self.passcheck.hide()
            self.encrypt.hide()
        if state == "qr":
            self.textedit.show()
            self.image.show()
            self.qrcreate.show()
            self.saveqr.show()

            self.createqr.hide()
            self.tableview.hide()
            self.passgen.hide()
            self.passcheck.hide()
            self.encrypt.hide()
        if state == "passgen":
            self.numcheck_gen.show()
            self.capletters.show()
            self.smallletters.show()
            self.specsymbols.show()
            self.lenght_label.show()
            self.lenght.show()
            self.listview.show()
            self.generate.show()
            self.clear.show()

            self.createqr.hide()
            self.tableview.hide()
            self.passgen.hide()
            self.passcheck.hide()
            self.encrypt.hide()

        if state == "passcheck":
            self.pass_line.show()
            self.safety_label.show()
            self.checkbtn.show()
            self.numcheck.show()
            self.smallcheck.show()
            self.bigcheck.show()
            self.speccheck.show()

            self.createqr.hide()
            self.tableview.hide()
            self.passgen.hide()
            self.passcheck.hide()
            self.encrypt.hide()
        if state == "select":
            self.mbar.show()

            self.login_label.hide()
            self.login_input.hide()
            self.password_label.hide()
            self.password_input.hide()
            self.log_button.hide()
            self.register_button.hide()

            self.main_table.hide()
            self.add_button.hide()
            self.delete_button.hide()
            self.find_button.hide()

            self.numcheck.hide()
            self.capletters.hide()
            self.smallletters.hide()
            self.specsymbols.hide()
            self.lenght_label.hide()
            self.lenght.hide()
            self.listview.hide()
            self.generate.hide()
            self.clear.hide()

            self.createqr.hide()
            self.tableview.hide()
            self.passgen.hide()

            self.textedit.hide()
            self.image.hide()
            self.qrcreate.hide()
            self.saveqr.hide()

            self.pass_line.hide()
            self.safety_label.hide()
            self.checkbtn.hide()
            self.numcheck.hide()
            self.smallcheck.hide()
            self.bigcheck.hide()
            self.speccheck.hide()

            self.createqr.show()
            self.tableview.show()
            self.passgen.show()
            self.passcheck.show()

    def register(self):
        login = self.login_input.text()
        password = self.password_input.text()

        conn = sqlite3.connect('Accounts.db')
        cursor = conn.cursor()

        hashed_login = hashlib.sha512(login.encode('UTF-8')).hexdigest()
        hashed_password = hashlib.sha512(password.encode('UTF-8')).hexdigest()

        # Check if name is engaged
        cursor.execute('SELECT * FROM Accounts WHERE login=?', (login,))
        if cursor.fetchone() is not None:
            QMessageBox.information(self, "Пользователь уже существует", "Пользователь с таким именем уже существует")
        else:
            cursor.execute('INSERT INTO Accounts VALUES (?, ?)', (hashed_login, hashed_password))
            conn.commit()

            QMessageBox.information(self, "Успешно", "Регистрация прошла успешно")

            self.widgets_state("select")

    def login(self):

        self.logged = self.login_input.text()
        password = self.password_input.text()

        hashed_login = hashlib.sha512(self.logged.encode('UTF-8')).hexdigest()
        hashed_password = hashlib.sha512(password.encode('UTF-8')).hexdigest()

        # Find user
        conn = sqlite3.connect('Accounts.db')
        cursor = conn.cursor()

        cursor.execute('SELECT password FROM Accounts WHERE login=?', (hashed_login,))
        result = cursor.fetchone()

        if result is None:
            QMessageBox.information(self, 'Не найдено', 'Пользователь не найден')
            return

        if hashed_password == result[0]:
            QMessageBox.information(self, 'Вход', 'Вход выполнен успешно')

            # Create services passwords db for user

            isExists = os.path.exists('Usersdb')
            if not isExists:
                os.makedirs('Usersdb')
            conn_user = sqlite3.connect(f'Usersdb/{self.logged}.db')
            cursor_user = conn_user.cursor()

            cursor_user.execute('CREATE TABLE IF NOT EXISTS services (service TEXT, password TEXT, key BLOB)')

            conn_user.commit()
            conn_user.close()

            # Show main widgets

            self.widgets_state("select")

            # Show passwords

            self.create_table_4_user()

        else:
            QMessageBox.warning(self, "Вход не выполнен", "Неверный пароль")

    def create_table_4_user(self):
        # Get data

        connection = sqlite3.connect(f'Usersdb/{self.logged}.db')
        cursor = connection.cursor()

        query = "SELECT service FROM services"
        cursor.execute(query)
        service_column_encrypted = [row[0] for row in cursor.fetchall()]

        query = "SELECT password FROM services"
        cursor.execute(query)
        column_password_encrypted = [row[0] for row in cursor.fetchall()]

        query = "SELECT key FROM services"
        cursor.execute(query)
        key_column_encrypted = [row[0] for row in cursor.fetchall()]

        column_password_decrypted = []
        key_column = []
        service_column = []

        if len(key_column_encrypted) != 0:
            for i in range(len(key_column_encrypted)):
                # Key decrypt
                decrypted_1 = self.cipher_main.decrypt(key_column_encrypted[i]).decode()
                key_column.append(decrypted_1)

                # Password decrypt
                cipher = Fernet(key_column[i])
                decrypted_2 = cipher.decrypt(column_password_encrypted[i]).decode()
                column_password_decrypted.append(decrypted_2)
                # Name decrypt
                decrypted_3 = self.cipher_main.decrypt(service_column_encrypted[i]).decode()
                service_column.append(decrypted_3)

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
        confirmation = QMessageBox.question(self, "Подтверждение выхода", "Вы уверены, что хотите выйти?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirmation == QMessageBox.StandardButton.Yes:
            self.login_input.setText('')
            self.password_input.setText('')

            self.widgets_state("login")

    def add_2_table(self):
        dialog = QDialog()
        Vbox_layout = QVBoxLayout(dialog)

        service_line = QLineEdit()
        service_line.setPlaceholderText("Введите название сервиса")

        password_line = QLineEdit()
        password_line.setPlaceholderText("Введите пароль")

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        Vbox_layout.addWidget(service_line)
        Vbox_layout.addWidget(password_line)
        Vbox_layout.addWidget(button_box)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            service = service_line.text()
            password = password_line.text()

            if service == '' or password == '':
                QMessageBox.warning(self, "Пустые поля", "Введите данные")
                self.add_2_table()

            else:
                key = Fernet.generate_key()
                encrypted_key = self.cipher_main.encrypt(key)
                encrypted_service = self.cipher_main.encrypt(service.encode())
                cipher = Fernet(key)

                encrypted_password = cipher.encrypt(password.encode())

                connection = sqlite3.connect(f'Usersdb/{self.logged}.db')
                cursor = connection.cursor()

                cursor.execute('INSERT INTO services VALUES (?, ?, ?)',
                               (encrypted_service, encrypted_password, encrypted_key))

                connection.commit()
                connection.close()

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

            connect = sqlite3.connect(f'Usersdb/{self.logged}.db')
            cursor = connect.cursor()

            confirmation = QMessageBox.question(self, "Подтверждение удаления",
                                                "Вы уверены, что хотите удалить пароль от этого сервиса?",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirmation == QMessageBox.StandardButton.Yes:
                try:
                    cursor.execute('DELETE FROM services WHERE service = ?', (service,))
                except sqlite3.OperationalError:
                    QMessageBox.warning(self, "Удаление не выполнено", "Такого названия не существует в таблице")

            connect.commit()
            connect.close()

        elif pressed_button != QDialog.DialogCode.Rejected:
            QMessageBox.warning(self, "Пустые поля", "Введите данные")
            self.delete_from_table()

        self.create_table_4_user()

    def find_needed_password(self):
        dialog = QDialog()
        dialog.resize(350, 100)
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

                connect = sqlite3.connect(f'Usersdb/{self.logged}.db')
                cursor = connect.cursor()

                cursor.execute('SELECT password FROM services WHERE service=?', (service,))
                result = cursor.fetchone()[-1]
                cursor.execute('SELECT key FROM services WHERE service=?', (service,))
                key = self.cipher_main.decrypt(cursor.fetchone()[-1]).decode()
                cipher = Fernet(key)

                if result is None:
                    QMessageBox.information(self, 'Не найдено', 'Записанного пароля не найдено')
                    return
                else:
                    decrypted_password = cipher.decrypt(result).decode()
                    QMessageBox.information(self, "Найден пароль", f"Пароль от {service}: {decrypted_password}")

                connect.commit()
                connect.close()
            except TypeError:
                QMessageBox.warning(self, "Не найдено", "Записанного пароля не найдено")
                self.find_needed_password()

        elif pressed_button != QDialog.DialogCode.Rejected:
            QMessageBox.warning(self, "Пустые поля", "Введите данные")
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

    def generate_pass(self):
        charlist = ''
        numcheck = self.numcheck.isChecked()
        capcheck = self.capletters.isChecked()
        smallcheck = self.smallletters.isChecked()
        speccheck = self.specsymbols.isChecked()
        lenght = self.lenght.value()
        if numcheck == True:
            charlist += string.digits
            print('yes num')
        if capcheck == True:
            charlist += string.ascii_uppercase
        if smallcheck == True:
            charlist += string.ascii_lowercase
        if speccheck == True:
            charlist += string.punctuation
        password = ''
        for i in range(lenght):
            randomchar = random.choice(charlist)
            password += randomchar
        print('yes sir')
        self.listview.addItem(password)

    def check_pass(self):
        horrible = QPixmap('pictures/1.png')
        weak = QPixmap('pictures/2.png')
        medium = QPixmap('pictures/3.png')
        strong = QPixmap('pictures/4.png')
        excellent = QPixmap('pictures/5.png')

        self.speccheck.setChecked(False)
        self.bigcheck.setChecked(False)
        self.smallcheck.setChecked(False)
        self.numcheck.setChecked(False)

        password = self.pass_line.text()

        password_scores = {0: 'None', 1: 'Horrible', 2: 'Weak', 3: 'Medium', 4: 'Strong', 5: 'Excellent'}
        password_strength = dict.fromkeys(['has_upper', 'has_lower', 'has_num', 'lenght', 'has_spec'], False)
        if re.search(r'[A-Z]', password):
            password_strength['has_upper'] = True
            self.bigcheck.setChecked(True)
        if re.search(r'[a-z]', password):
            password_strength['has_lower'] = True
            self.smallcheck.setChecked(True)
        if re.search(r'[0-9]', password):
            password_strength['has_num'] = True
            self.numcheck.setChecked(True)
        if len(password) > 8:
            password_strength['lenght'] = True
        if re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password):
            password_strength['has_spec'] = True
            self.speccheck.setChecked(True)

        score = len([b for b in password_strength.values() if b])

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

        if password in worst:
            score = 0
            self.safety_label_text.setText('Часто используется')
            self.safety_label.setFixedSize(90, 31)
            self.safety_label.setPixmap(horrible)

        if score == 1:
            self.safety_label_text.setText('Очень ненадежный')
            self.safety_label.setFixedSize(90, 31)
            self.safety_label.setPixmap(horrible)
        elif score == 2:
            self.safety_label_text.setText('Ненадежный')
            self.safety_label.setFixedSize(180, 31)
            self.safety_label.setPixmap(weak)
        elif score == 3:
            self.safety_label_text.setText('Средней надежности')
            self.safety_label.setFixedSize(270, 31)
            self.safety_label.setPixmap(medium)
        elif score == 4:
            self.safety_label_text.setText('Надежный')
            self.safety_label.setFixedSize(360, 31)
            self.safety_label.setPixmap(strong)
        elif score == 5:
            self.safety_label_text.setText('Очень надежный')
            self.safety_label.setFixedSize(450, 31)
            self.safety_label.setPixmap(excellent)

    def select_file(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "Текстовые файлы (*.txt)")
        file = open(fileName)
        self.file_content = file.read()


window = Window()
window.show()
sys.exit(app.exec())
