import sys
from configparser import ConfigParser
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.uic.load_ui import loadUi, loadUiType

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
        self.show_themes(False)
        self.main_tab_widget.tabBar().setVisible(False)

        tbl_header_style = "::section { background-color: #efeeea; }"
        self.table_categories.horizontalHeader().setStyleSheet(tbl_header_style)
        self.table_authors.horizontalHeader().setStyleSheet(tbl_header_style)
        self.table_publishers.horizontalHeader().setStyleSheet(tbl_header_style)

        self.table_categories.verticalHeader().setVisible(True)
        self.table_categories.verticalHeader().setStyleSheet(tbl_header_style)
        self.table_authors.verticalHeader().setVisible(True)
        self.table_authors.verticalHeader().setStyleSheet(tbl_header_style)
        self.table_publishers.verticalHeader().setVisible(True)
        self.table_publishers.verticalHeader().setStyleSheet(tbl_header_style)

    def handle_buttons(self):

        # Main tabs
        self.btn_daily_operations.clicked.connect(self.open_daily_operations_tab)
        self.btn_books.clicked.connect(self.open_books_tab)
        self.btn_users.clicked.connect(self.open_users_tab)
        self.btn_settings.clicked.connect(self.open_settings_tab)

        # Themes
        self.btn_show_themes.clicked.connect(lambda: self.show_themes(True))
        self.btn_hide_themes.clicked.connect(lambda: self.show_themes(False))

        # Books
        self.btn_add_new_book.clicked.connect(self.add_new_book)
        self.btn_book_search.clicked.connect(self.search_book)
        self.btn_edit_book_save.clicked.connect(self.edit_book_save)
        self.btn_edit_book_delete.clicked.connect(self.edit_book_delete)

        # Settings
        self.btn_add_category.clicked.connect(self.add_category)
        self.btn_add_author.clicked.connect(self.add_author)
        self.btn_add_publisher.clicked.connect(self.add_publisher)

    

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

    def show_themes(self, show_flag=True):
        if show_flag:
            self.themes_box.show()
        else:
            self.themes_box.hide()

    ###############################################
    ## Open Tabs
    ###############################################
    def open_daily_operations_tab(self):
        self.main_tab_widget.setCurrentIndex(0)

    def open_books_tab(self):
        self.main_tab_widget.setCurrentIndex(1)
        self.get_items_book_combobox()

    def open_users_tab(self):
        self.main_tab_widget.setCurrentIndex(2)

    def open_settings_tab(self):
        self.main_tab_widget.setCurrentIndex(3)
        self.display_categories()
        self.display_authors()
        self.display_publishers()


    ###############################################
    ## Books
    ###############################################
    def add_new_book(self):
        with MySQLdb.connect(**self._DB) as db_conn:
            cur = db_conn.cursor()

            title       = self.new_book_title.text()
            description = self.new_book_description.toPlainText()
            code        = self.new_book_code.text()
            category    = self.new_book_category.currentIndex()
            author      = self.new_book_author.currentIndex()
            publisher   = self.new_book_publisher.currentIndex()
            price       = self.new_book_price.text()

            cur.execute("""
                INSERT INTO BOOK (name, description, code, category_id, author_id, publisher_id, price)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (title, description, code, category, author, publisher, price))
            db_conn.commit()

            self.statusBar().showMessage("New book added.")

            self.new_book_title.setText('')
            self.new_book_description.setText('')
            self.new_book_code.setText('')
            self.new_book_category.setCurrentIndex(-1)
            self.new_book_author.setCurrentIndex(-1)
            self.new_book_publisher.setCurrentIndex(-1)
            self.new_book_price.setText('')

    def search_book(self):
        book_title = self.book_title_search.text()
        print("Entered: ", book_title)

        with MySQLdb.connect(**self._DB) as db_conn:
            cur = db_conn.cursor()
            # sql = """SELECT * FROM book WHERE name = 'space travel 1' """
            sql = "SELECT * FROM book where name= %s"
            cur.execute(sql, [(book_title)])
            data = cur.fetchone()
            print("found: ", data)


    def edit_book_save(self):
        pass

    def edit_book_delete(self):
        pass


    ###############################################
    ## Users
    ###############################################
    def add_new_user(self):
        pass


    def user_login(self):
        pass


    def edit_user_data(self):
        pass


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
            cur.execute("SELECT name FROM category")
            data = cur.fetchall()
            self.new_book_category.clear()
            for category in data:
                self.new_book_category.addItem(category[0])

            # Authors
            cur.execute("SELECT name FROM author")
            data = cur.fetchall()
            self.new_book_author.clear()
            for author in data:
                self.new_book_author.addItem(author[0])

            # Publishers
            cur.execute("SELECT name FROM publisher")
            data = cur.fetchall()
            self.new_book_publisher.clear()
            for publisher in data:
                self.new_book_publisher.addItem(publisher[0])


def app_main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec()


if __name__ == "__main__":
    app_main()

