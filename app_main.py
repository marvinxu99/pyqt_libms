import sys
from configparser import ConfigParser
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.uic.load_ui import loadUi, loadUiType
from datetime import datetime, date, timedelta

import MySQLdb


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        loadUi("library.ui", self)
        self.setWindowTitle("Library Management System")

        self._DB = self.read_db_config()

        self.handle_UI_changes()
        self.handle_buttons()

    def handle_UI_changes(self):
        self.main_tab_widget.tabBar().setVisible(False)
        self.setStyleSheet("QStatusBar{border-top: 1px outset grey;}");

        self.show_themes(False)
        # self.set_theme(theme='darkgray')

        # tbl_header_style = "::section { background-color: #efeeea; }"
        # self.table_categories.horizontalHeader().setStyleSheet(tbl_header_style)
        # self.table_authors.horizontalHeader().setStyleSheet(tbl_header_style)
        # self.table_publishers.horizontalHeader().setStyleSheet(tbl_header_style)

        self.table_categories.verticalHeader().setVisible(True)
        # self.table_categories.verticalHeader().setStyleSheet(tbl_header_style)
        self.table_authors.verticalHeader().setVisible(True)
        # self.table_authors.verticalHeader().setStyleSheet(tbl_header_style)
        self.table_publishers.verticalHeader().setVisible(True)
        # self.table_publishers.verticalHeader().setStyleSheet(tbl_header_style)

        # Hide the following fields
        self.lbl_edit_book_id.setVisible(False)
        self.edit_book_id.setVisible(False)
        self.lbl_edit_client_id.setVisible(False)
        self.edit_client_id.setVisible(False)


    def handle_buttons(self):
        # Main tabs
        self.btn_daily_operations.clicked.connect(self.open_daily_operations_tab)
        self.btn_books.clicked.connect(self.open_books_tab)
        self.btn_clients.clicked.connect(self.open_clients_tab)
        self.btn_users.clicked.connect(self.open_users_tab)
        self.btn_settings.clicked.connect(self.open_settings_tab)

        # Day to day operations
        self.btn_daily_operations_add.clicked.connect(self.daily_operations_add)

        # Books
        self.btn_add_new_book.clicked.connect(self.add_new_book)
        self.btn_book_search.clicked.connect(self.search_book)
        self.btn_edit_book_save.clicked.connect(self.edit_book_save)
        self.btn_edit_book_delete.clicked.connect(self.edit_book_delete)

        # Clients
        self.btn_add_new_client.clicked.connect(self.add_new_client)
        self.btn_client_name_search.clicked.connect(self.search_client_national_id)
        self.btn_update_client.clicked.connect(self.update_client)
        self.btn_delete_client.clicked.connect(self.delete_client)

        # Users
        self.btn_add_user.clicked.connect(self.add_new_user)
        self.btn_user_login.clicked.connect(self.user_login)
        self.btn_update_user_data.clicked.connect(self.update_user_data)

        # Settings
        self.btn_add_category.clicked.connect(self.add_category)
        self.btn_add_author.clicked.connect(self.add_author)
        self.btn_add_publisher.clicked.connect(self.add_publisher)

        # Themes
        self.btn_show_themes.clicked.connect(lambda: self.show_themes(True))
        self.btn_hide_themes.clicked.connect(lambda: self.show_themes(False))
        self.btn_theme_light.clicked.connect(lambda: self.set_theme(theme='light'))
        self.btn_theme_darkgray.clicked.connect(lambda: self.set_theme(theme='darkgray'))
        self.btn_theme_darkblue.clicked.connect(lambda: self.set_theme(theme='darkblue'))
        self.btn_theme_darkorange.clicked.connect(lambda: self.set_theme(theme='darkorange'))

    def read_db_config(self, filename='.env', section='mysql'):
        """ Read database configuration file and return a dictionary object
        :param filename: name of the configuration file
        :param section: section of database configuration
        :return: a dictionary of database parameters
        """
        # create parser and read ini configuration file
        parser = ConfigParser()
        parser.read(filename)

        # get section, default to mysql
        db = {}
        if parser.has_section(section):
            items = parser.items(section)
            for item in items:
                db[item[0]] = item[1]
        else:
            raise Exception('{0} not found in the {1} file'.format(section, filename))

        return db

    ###############################################
    ## Open Tabs
    ###############################################
    def open_daily_operations_tab(self):
        # self.main_tab_widget.setCurrentIndex(0)
        self.main_tab_widget.setCurrentWidget(self.tab_daily_operations)
        self.show_daily_operations()

    def open_books_tab(self):
        self.main_tab_widget.setCurrentWidget(self.tab_books)
        self.get_items_book_combobox()
        self.display_all_books()

    def open_clients_tab(self):
        # self.main_tab_widget.setCurrentIndex(3)
        self.main_tab_widget.setCurrentWidget(self.tab_clients)
        self.display_all_clients()

    def open_users_tab(self):
        # self.main_tab_widget.setCurrentIndex(2)
        self.main_tab_widget.setCurrentWidget(self.tab_users) 

    def open_settings_tab(self):
        # self.main_tab_widget.setCurrentIndex(3)
        self.main_tab_widget.setCurrentWidget(self.tab_settings)
        self.display_categories()
        self.display_authors()
        self.display_publishers()

    ###############################################
    ## Dat to Day Operations
    ###############################################
    def daily_operations_add(self):
        book_title  = self.daily_ops_book_title.text()
        client_name  = self.daily_ops_client_name.text()
        type        = self.daily_ops_type.currentText()
        days        = self.daily_ops_days.currentText()
        today        = datetime.today() 

        if book_title and type and days:
            with MySQLdb.connect(**self._DB) as db_conn:
                cur = db_conn.cursor()
                cur.execute("""
                    INSERT INTO dailyoperations (book_name, client_name, type, days, transaction_date)
                    VALUES (%s, %s, %s, %s, %s)
                """, (book_title, client_name, type, days, today))
                db_conn.commit()

                self.daily_ops_book_title.setText('')
                self.daily_ops_client_name.setText('')
                self.daily_ops_type.setCurrentIndex(-1)
                self.daily_ops_type.setCurrentIndex(-1)
                self.statusBar().showMessage("New daily operation added.")
                self.show_daily_operations()

    def show_daily_operations(self):
        with MySQLdb.connect(**self._DB) as db_conn:
            cur = db_conn.cursor()
            sql = """SELECT book_name, client_name, type, transaction_date, days  
                from dailyoperations 
                ORDER BY transaction_date
            """ 
            cur.execute(sql)
            operations = cur.fetchall()

            if operations:
                self.daily_ops_table.setRowCount(0)   # Clear up the table
                for row, operation in enumerate(operations):
                    row_pos = self.daily_ops_table.rowCount()
                    self.daily_ops_table.insertRow(row_pos)
                    for column, item in enumerate(operation):
                        if column == 3:   # date - From
                            from_str = item.strftime("%d-%m-%Y")
                            self.daily_ops_table.setItem(row, column, QTableWidgetItem(from_str))
                        elif column == 4:  # date - to
                            to_str = (operation[3] + timedelta(days=int(item))).strftime("%d-%m-%Y")
                            self.daily_ops_table.setItem(row, column, QTableWidgetItem(to_str))
                        else:
                            self.daily_ops_table.setItem(row, column, QTableWidgetItem(str(item)))
            else:
                self.statusBar().showMessage("No daily operations found.")


    ###############################################
    ## Books
    ###############################################
    def display_all_books(self):
        with MySQLdb.connect(**self._DB) as db_conn:
            cur = db_conn.cursor()
            sql = """ SELECT b.code, b.name, b.description, c.name, a.name, p.name, b.price
                FROM book AS b
                INNER JOIN category AS c ON c.id = b.category_id
                INNER JOIN author AS a ON a.id = b.author_id 
                INNER JOIN publisher AS p ON p.id = b.publisher_id
                ORDER BY b.name
            """ 
            cur.execute(sql)
            books = cur.fetchall()

            if books:
                self.table_all_books.setRowCount(0)   # Clear up the table
                for row, book in enumerate(books):
                    row_pos = self.table_all_books.rowCount()
                    self.table_all_books.insertRow(row_pos)
                    for column, item in enumerate(book):
                        self.table_all_books.setItem(row, column, QTableWidgetItem(str(item)))
            else:
                self.statusBar().showMessage("No books found.")

    def add_new_book(self):
        with MySQLdb.connect(**self._DB) as db_conn:
            cur = db_conn.cursor()

            title           = self.new_book_title.text()
            description     = self.new_book_description.toPlainText()
            code            = self.new_book_code.text()
            category_id     = self._categories[self.new_book_category.currentText()]
            author_id       = self._authors[self.new_book_author.currentText()]
            publisher_id    = self._publishers[self.new_book_publisher.currentText()]
            price           = self.new_book_price.text()

            cur.execute("""
                INSERT INTO book (name, description, code, category_id, author_id, publisher_id, price)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (title, description, code, category_id, author_id, publisher_id, price))
            db_conn.commit()

            self.statusBar().showMessage("New book added.")

            self.new_book_title.setText('')
            self.new_book_description.setText('')
            self.new_book_code.setText('')
            self.new_book_category.setCurrentIndex(-1)
            self.new_book_author.setCurrentIndex(-1)
            self.new_book_publisher.setCurrentIndex(-1)
            self.new_book_price.setText('')
            self.display_all_books()

    def search_book(self):
        book_title = self.book_title_search.text()
        # print("Entered: ", book_title)

        with MySQLdb.connect(**self._DB) as db_conn:
            cur = db_conn.cursor()
            sql = """ SELECT b.book_id, b.name, b.description, b.code, c.name, a.name, p.name, b.price
                FROM book AS b
                INNER JOIN category AS c ON c.id = b.category_id
                INNER JOIN author AS a ON a.id = b.author_id 
                INNER JOIN publisher AS p ON p.id = b.publisher_id
                WHERE b.name=%s
                ORDER BY b.name
            """ 
            cur.execute(sql, [(book_title)])
            data = cur.fetchone()
            print("found: ", data)
            if data:
                self.edit_book_title.setText(data[1])
                self.edit_book_description.setText(data[2])
                self.edit_book_code.setText(data[3])
                self.edit_book_category.setCurrentText(data[4])
                self.edit_book_author.setCurrentText(data[5])
                self.edit_book_publisher.setCurrentText(data[6])
                self.edit_book_price.setText(str(data[7]))
                self.edit_book_id.setText(str(data[0]))             # Book id
                self.statusBar().showMessage(f"Book found.")
            else:
                self.statusBar().showMessage(f"Book NOT found.")

    def edit_book_save(self):
        with MySQLdb.connect(**self._DB) as db_conn:
            cur = db_conn.cursor()

            title           = self.edit_book_title.text()
            decription      = self.edit_book_description.toPlainText()
            code            = self.edit_book_code.text()
            category_id     = self._categories[self.edit_book_category.currentText()]
            author_id       = self._authors[self.edit_book_author.currentText()]
            publisher_id    = self._publishers[self.edit_book_publisher.currentText()]
            price           = self.edit_book_price.text()
            book_id         = self.edit_book_id.text()

            sql = """UPDATE book SET name=%s, description=%s, code=%s, category_id=%s, author_id=%s, publisher_id=%s, price=%s
                WHERE book_id=%s"""
            cur.execute(sql, (title, decription, code, category_id, author_id, publisher_id, price, book_id))
            db_conn.commit()

            self.edit_book_title.setText('')
            self.edit_book_description.setText('')
            self.edit_book_code.setText('')
            self.edit_book_category.setCurrentIndex(-1)
            self.edit_book_author.setCurrentIndex(-1)
            self.edit_book_publisher.setCurrentIndex(-1)
            self.edit_book_price.setText('')
            self.edit_book_id.setText('')             # Book id
            self.book_title_search.setText('')
            self.statusBar().showMessage(f"Book updated.")
        self.display_all_books()

    def edit_book_delete(self):
        warning = QMessageBox.warning(self, 
            "Delete Book", 
            "Deleting this book from database?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if warning == QMessageBox.StandardButton.Yes:
            with MySQLdb.connect(**self._DB) as db_conn:
                cur = db_conn.cursor()

                book_id = self.edit_book_id.text()
                sql = f"DELETE FROM book WHERE book_id={book_id}"
                cur.execute(sql)
                db_conn.commit()

                self.edit_book_title.setText('')
                self.edit_book_description.setText('')
                self.edit_book_code.setText('')
                self.edit_book_category.setCurrentIndex(-1)
                self.edit_book_author.setCurrentIndex(-1)
                self.edit_book_publisher.setCurrentIndex(-1)
                self.edit_book_price.setText('')
                self.edit_book_id.setText('')             # Book id
                self.book_title_search.setText('')
                self.statusBar().showMessage(f"Book deleted.")
            self.display_all_books()
        else:
            self.statusBar().showMessage(f"Deleting book aborted")

    ###############################################
    ## Clients
    ###############################################
    def display_all_clients(self):
        with MySQLdb.connect(**self._DB) as db_conn:
            cur = db_conn.cursor()
            sql = "SELECT name, email, national_id FROM client ORDER BY name"
            cur.execute(sql)
            clients = cur.fetchall()

            if clients:
                self.table_all_clients.setRowCount(0)   # Clear up the table
                for row, client in enumerate(clients):
                    row_pos = self.table_all_clients.rowCount()
                    self.table_all_clients.insertRow(row_pos)
                    for column, item in enumerate(client):
                        self.table_all_clients.setItem(row, column, QTableWidgetItem(str(item)))
            else:
                self.statusBar().showMessage("No clients found.")


    def add_new_client(self):
        with MySQLdb.connect(**self._DB) as db_conn:
            cur = db_conn.cursor()

            name        = self.new_client_name.text()
            email       = self.new_client_email.text()
            natuonal_id = self.new_client_national_id.text()

            cur.execute("INSERT INTO client (name, email, national_id) VALUES (%s, %s, %s)", (name, email, natuonal_id))
            db_conn.commit()

            self.new_client_name.setText('')
            self.new_client_email.setText('')
            self.new_client_national_id.setText('')
            self.statusBar().showMessage("New client added.")
        self.display_all_clients()

    def search_client_national_id(self):
        client_national_id = self.client_national_id_search.text()

        with MySQLdb.connect(**self._DB) as db_conn:
            cur = db_conn.cursor()
            sql = "SELECT client_id, name, email, national_id FROM client where national_id= %s"
            cur.execute(sql, [(client_national_id)])
            data = cur.fetchone()
            # print("found: ", data)
            if data:
                self.edit_client_name.setText(data[1])
                self.edit_client_email.setText(data[2])
                self.edit_client_national_id.setText(data[3])
                self.edit_client_id.setText(str(data[0]))             # Client id
                self.statusBar().showMessage(f"Client found.")
            else:
                self.statusBar().showMessage(f"Client NOT found.")

    def update_client(self):
        with MySQLdb.connect(**self._DB) as db_conn:
            cur = db_conn.cursor()

            name = self.edit_client_name.text()
            email = self.edit_client_email.text()
            national_id = self.edit_client_national_id.text()
            client_id = self.edit_client_id.text()

            sql = "UPDATE client SET name=%s, email=%s, national_id=%s WHERE client_id=%s"
            cur.execute(sql, (name, email, national_id, client_id))
            db_conn.commit()

            self.edit_client_name.setText('')
            self.edit_client_email.setText('')
            self.edit_client_national_id.setText('')
            self.edit_book_id.setText('')             # Client id
            self.client_national_id_search.setText('')
            self.statusBar().showMessage(f"Client updated.")
        self.display_all_clients()

    def delete_client(self):
        warning = QMessageBox.warning(self, 
            "Delete Client", 
            "Deleting this client from database?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if warning == QMessageBox.StandardButton.Yes:
            with MySQLdb.connect(**self._DB) as db_conn:
                cur = db_conn.cursor()

                book_id = self.edit_client_id.text()
                sql = f"DELETE FROM client WHERE client_id={book_id}"
                cur.execute(sql)
                db_conn.commit()

                self.edit_client_name.setText('')
                self.edit_client_email.setText('')
                self.edit_client_national_id.setText('')
                self.edit_book_id.setText('')             # Client id
                self.client_national_id_search.setText('')
                self.statusBar().showMessage(f"Client deleted.")
            self.display_all_clients()
        else:
            self.statusBar().showMessage(f"Deleting client aborted")

    ###############################################
    ## Users
    ###############################################
    def add_new_user(self):
        password = self.new_user_password.text()
        password2 = self.new_user_password2.text()
        if password and password == password2:
            with MySQLdb.connect(**self._DB) as db_conn:
                cur = db_conn.cursor()

                name = self.new_user_name.text()
                email = self.new_user_email.text()
                sql = "INSERT INTO user (name, email, password) VALUES(%s, %s, %s)"
                cur.execute(sql, (name, email, password))
                db_conn.commit()
    
                self.statusBar().showMessage(f"New user added.")
        else:
            self.new_user_password_warning.setText("Passwords are incorrect!")

    def user_login(self):
        user_name = self.login_user_name.text()
        password = self.login_user_password.text()

        if user_name and password:
            with MySQLdb.connect(**self._DB) as db_conn:
                cur = db_conn.cursor()

                sql = "SELECT user_id, name, email, password FROM user WHERE name=%s and password=%s"
                cur.execute(sql, (user_name, password))
                data = cur.fetchone()

                if data:
                    self.edit_user_id = data[0]
                    self.edit_user_name.setText(data[1])
                    self.edit_user_email.setText(data[2])
                    self.edit_user_password.setText(data[3])

                    self.login_user_name.setText('')
                    self.login_user_password.setText('')

                    self.edit_user_groupbox.setEnabled(True)
                    self.statusBar().showMessage("Valid user name and password.")
                else:
                    self.statusBar().showMessage("Invalid user name and/or password.")

    def update_user_data(self):
        print("edit user data")

        password = self.edit_user_password.text()
        password2 = self.edit_user_password2.text()

        if password and password == password2:
            with MySQLdb.connect(**self._DB) as db_conn:
                cur = db_conn.cursor()

                name = self.edit_user_name.text()
                email = self.edit_user_email.text()

                sql = "UPDATE user SET name=%s, email=%s, password=%s WHERE user_id=%s"
                cur.execute(sql, (name, email, password, self.edit_user_id))
                db_conn.commit()

                self.edit_user_name.setText('')
                self.edit_user_email.setText('')
                self.edit_user_password.setText('')
                self.edit_user_password2.setText('')
                self.statusBar().showMessage("User updated.")
                self.edit_user_groupbox.setEnabled(False)
        else:
            self.statusBar().showMessage("Passwords are incorrect.")


    ###############################################
    ## Settings
    ###############################################
    def add_category(self):
        db_conn = MySQLdb.connect(**self._DB)
        cur = db_conn.cursor()

        category_name = self.new_category_name.text()
        cur.execute("INSERT INTO category (name) VALUES (%s)", (category_name,))
        db_conn.commit()
        db_conn.close()

        self.new_category_name.setText('')
        self.display_categories()
        self.statusBar().showMessage(f"New categoty: {category_name} added.")

    def display_categories(self):
        db_conn = MySQLdb.connect(**self._DB)
        cur = db_conn.cursor()

        cur.execute("SELECT name FROM category")
        data = cur.fetchall()
        db_conn.close()

        if data:
            self.table_categories.setRowCount(0)   # Clear up the table
            for row, items in enumerate(data):
                row_pos = self.table_categories.rowCount()
                self.table_categories.insertRow(row_pos)
                for column, item in enumerate(items):
                    self.table_categories.setItem(row, column, QTableWidgetItem(str(item)))

    def add_author(self):
        db_conn = MySQLdb.connect(**self._DB)
        cur = db_conn.cursor()

        author_name = self.new_author_name.text()
        cur.execute("INSERT INTO author (name) VALUES (%s)", (author_name,))
        db_conn.commit()
        db_conn.close()
        
        self.new_author_name.setText('')
        self.display_authors()
        self.statusBar().showMessage(f"New author: {author_name} added.")

    def display_authors(self):
        db_conn = MySQLdb.connect(**self._DB)
        cur = db_conn.cursor()

        cur.execute("SELECT name FROM author")
        data = cur.fetchall()
        db_conn.close()

        if data:
            self.table_authors.setRowCount(0)   # Clear up the table
            for row, items in enumerate(data):
                row_pos = self.table_authors.rowCount()
                self.table_authors.insertRow(row_pos)
                for column, item in enumerate(items):
                    self.table_authors.setItem(row, column, QTableWidgetItem(str(item)))

    def add_publisher(self):
        with MySQLdb.connect(**self._DB) as db_conn:
            cur = db_conn.cursor()

            publisher_name = self.new_publisher_name.text()
            cur.execute("INSERT INTO publisher (name) VALUES (%s)", (publisher_name,))
            db_conn.commit()
            
            self.new_publisher_name.setText('')
            self.display_publishers()
            self.statusBar().showMessage(f"New publisher: {publisher_name} added.")

    def display_publishers(self):
        with MySQLdb.connect(**self._DB) as db_conn:
            cur = db_conn.cursor()

            cur.execute("SELECT name FROM publisher")
            data = cur.fetchall()

            if data:
                self.table_publishers.setRowCount(0)   # Clear up the table
                for row, items in enumerate(data):
                    row_pos = self.table_publishers.rowCount()
                    self.table_publishers.insertRow(row_pos)
                    for column, item in enumerate(items):
                        self.table_publishers.setItem(row, column, QTableWidgetItem(str(item)))

    ###############################################
    ## Show settings in UI
    ###############################################
    def get_items_book_combobox(self):
        with MySQLdb.connect(**self._DB) as db_conn:
            cur = db_conn.cursor()

            # Categories
            cur.execute("SELECT id, name FROM category ORDER BY name")
            data = cur.fetchall()
            self.new_book_category.clear()
            self._categories = {}
            for category in data:
                self.new_book_category.addItem(category[1])
                self.edit_book_category.addItem(category[1])
                self._categories[category[1]] = category[0]

            # Authors
            cur.execute("SELECT id, name FROM author ORDER BY name")
            data = cur.fetchall()
            self.new_book_author.clear()
            self._authors = {}
            for author in data:
                self.new_book_author.addItem(author[1])
                self.edit_book_author.addItem(author[1])
                self._authors[author[1]] = author[0]

            # Publishers
            cur.execute("SELECT id, name FROM publisher ORDER BY name")
            data = cur.fetchall()
            self.new_book_publisher.clear()
            self._publishers = {}
            for publisher in data:
                self.new_book_publisher.addItem(publisher[1])
                self.edit_book_publisher.addItem(publisher[1])
                self._publishers[publisher[1]] = publisher[0]

    ###############################################
    ## Themes
    ###############################################
    def show_themes(self, show_flag=True):
        """Display all available theme choices"""
        self.btn_hide_themes.resize(QSize(20, 40));
        if show_flag:
            self.themes_box.show()
        else:
            self.themes_box.hide()

    def set_theme(self, theme='light'):
        """set to the selected theme"""
        if theme == 'light':
            print('light theme')
            self.setStyleSheet("")
        else:
            style_qss = f"themes/{theme}.qss"
            print(style_qss)
            with open(style_qss) as f_style:
                style = f_style.read()
                self.setStyleSheet(style)


def app_main():
    app = QApplication(sys.argv)
    # Force the style to be the same on all OSs:
    app.setStyle("Fusion")
    window = MainApp()
    window.show()
    app.exec()


if __name__ == "__main__":
    app_main()

