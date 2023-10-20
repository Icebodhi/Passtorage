import sqlite3
import sys
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from cryptography.fernet import Fernet

app = QApplication(sys.argv)


def distribute_elements(list1, list2):
    result_lists = [[list1[i], list2[i]] for i in range(min(len(list1), len(list2)))]
    return result_lists


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
        return len(self.data[0])

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

        # Stacked layout
        self.layout_4_widgets = QStackedLayout()

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
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.log_button = QPushButton("Войти", self)
        self.log_button.setFixedSize(131, 71)
        self.log_button.move(130, 350)
        self.log_button.clicked.connect(self.login)

        self.register_button = QPushButton("Зарегистрироваться", self)
        self.register_button.setFixedSize(131, 71)
        self.register_button.move(310, 350)
        self.register_button.clicked.connect(self.register)

        # Main widgets
        self.main_table = QTableView(self)
        self.main_table.setFixedSize(581, 401)
        self.main_table.move(10, 10)

        self.add_button = QPushButton('Записать', self)
        self.add_button.setFixedSize(75, 23)
        self.add_button.move(20, 420)

        self.delete_button = QPushButton("Удалить", self)
        self.delete_button.setFixedSize(75, 23)
        self.delete_button.move(120, 420)

        self.logout_button = QPushButton("Выйти", self)
        self.logout_button.setFixedSize(75, 23)
        self.logout_button.move(490, 420)
        self.logout_button.clicked.connect(self.logout)

        # Add login widgets to layout

        self.layout_4_widgets.addWidget(self.login_label)
        self.layout_4_widgets.addWidget(self.login_input)
        self.layout_4_widgets.addWidget(self.password_label)
        self.layout_4_widgets.addWidget(self.password_input)

        # Add main widgets to layout

        self.layout_4_widgets.addWidget(self.main_table)
        self.layout_4_widgets.addWidget(self.add_button)
        self.layout_4_widgets.addWidget(self.delete_button)
        self.layout_4_widgets.addWidget(self.logout_button)

        # Hide main widgets from log screen

        self.main_table.hide()
        self.add_button.hide()
        self.delete_button.hide()
        self.logout_button.hide()

        # Show widgets login

        self.login_label.show()
        self.login_input.show()
        self.password_input.show()
        self.password_label.show()

        # Get from db
        connect_db = sqlite3.connect("Accounts.db")
        cursor = connect_db.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS Accounts (login TEXT, password TEXT, column BLOB)')
        connect_db.commit()
        connect_db.close()

    def register(self):
        login = self.login_input.text()
        password = self.password_input.text()

        # Save login for future

        key = Fernet.generate_key()
        cipher = Fernet(key)

        conn = sqlite3.connect('Accounts.db')
        cursor = conn.cursor()

        encrypted_password = cipher.encrypt(password.encode())

        # Check if name is engaged
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

        self.logged = login

        # Find user
        conn = sqlite3.connect('Accounts.db')
        cursor = conn.cursor()

        cursor.execute('SELECT password FROM Accounts WHERE login=?', (login,))
        result = cursor.fetchone()

        if result is None:
            QMessageBox.information(self, 'Не найдено', 'Пользователь не найден')
            return

        # Decrypt password
        query = f"SELECT * FROM Accounts WHERE login = '{self.logged}'"
        cursor.execute(query)
        key = cursor.fetchone()[-1]
        cipher = Fernet(key)
        decrypted_password = cipher.decrypt(result[0]).decode()

        if password == decrypted_password:
            QMessageBox.information(self, 'Вход', 'Вход выполнен успешно')

            # Create services passwords db for user

            isExists = os.path.exists('Usersdb')
            if not isExists:
                os.makedirs('Usersdb')
                print('yes')
            conn_user = sqlite3.connect(f'Usersdb/{login}.db')
            cursor_user = conn_user.cursor()

            cursor_user.execute('CREATE TABLE IF NOT EXISTS services (service TEXT, password TEXT, key BLOB)')
            conn_user.commit()
            conn_user.close()

            # Show main widgets
            self.main_table.show()
            self.add_button.show()
            self.delete_button.show()
            self.logout_button.show()

            self.login_label.hide()
            self.login_input.hide()
            self.password_label.hide()
            self.password_input.hide()
            self.log_button.hide()
            self.register_button.hide()

            # Show passwords

            self.create_table_4_user()

        else:
            QMessageBox.warning(self, "Вход не выполнен", "Неверный пароль")

    def create_table_4_user(self):

        # Get services data
        connection = sqlite3.connect(f'Usersdb/{self.logged}.db')
        cursor = connection.cursor()

        query = "SELECT service FROM services"
        cursor.execute(query)
        column_sevice = [row[0] for row in cursor.fetchall()]

        cursor.close()
        connection.close()

        # Get password data

        connection = sqlite3.connect(f'Usersdb/{self.logged}.db')
        cursor = connection.cursor()

        query = "SELECT password FROM services"
        cursor.execute(query)
        column_password = [row[0] for row in cursor.fetchall()]

        cursor.close()
        connection.close()

        # Create list for table

        list_4_table = distribute_elements(column_sevice, column_password)

        headers_names = ['Сервис', 'Пароль']
        print(list_4_table)

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
            self.login_label.show()
            self.login_input.show()
            self.password_label.show()
            self.password_input.show()
            self.log_button.show()
            self.register_button.show()

            self.login_input.setText('')
            self.password_input.setText('')

            self.main_table.hide()
            self.add_button.hide()
            self.delete_button.hide()
            self.logout_button.hide()


window = Window()
window.show()
sys.exit(app.exec())