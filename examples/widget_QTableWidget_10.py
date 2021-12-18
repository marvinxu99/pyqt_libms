from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *


class Dlg(QDialog):

    def __init__(self):
        QDialog.__init__(self)
        self.layout = QGridLayout(self)

        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()

        self.tabs.addTab(self.tab1,"Tab1")
        self.tabs.addTab(self.tab2,"Tab2")
        self.tabs.addTab(self.tab3,"Tab3")

        layer = iface.activeLayer()

        nf = layer.fields().names()

        feats = [ feat for feat in layer.getFeatures() ]

        data = [ [] for i in range(len(feats)) ]

        nb_row = len(feats)
        nb_col = len(nf)

        for i, feat in enumerate(feats):
            for j in range(nb_col):
                data[i].append(feat.attribute(nf[j]))

        self.tab1.layout = QVBoxLayout(self)

        self.table1 = QTableWidget()
        self.table1.setRowCount(nb_row)
        self.table1.setColumnCount(nb_col)
        self.table1.setHorizontalHeaderLabels(nf)

        for row in range (nb_row):
            for col in range(nb_col):
                item = QTableWidgetItem(str(data[row][col]))
                self.table1.setItem(row, col, item)

        self.tab1.layout.addWidget(self.table1)
        self.tab1.setLayout(self.tab1.layout)

        self.layout.addWidget(self.tabs, 0, 0)

w = Dlg()
w.resize(350,300)
w.setWindowTitle('Example with QTableWidget')
w.setWindowFlags(Qt.WindowStaysOnTopHint)
w.show()
