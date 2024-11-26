# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'test.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1280, 720)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton1 = QPushButton(self.centralwidget)
        self.pushButton1.setObjectName(u"pushButton1")

        self.gridLayout.addWidget(self.pushButton1, 0, 0, 1, 1)

        self.pushButton2 = QPushButton(self.centralwidget)
        self.pushButton2.setObjectName(u"pushButton2")

        self.gridLayout.addWidget(self.pushButton2, 0, 1, 1, 1)

        self.pushButton3 = QPushButton(self.centralwidget)
        self.pushButton3.setObjectName(u"pushButton3")

        self.gridLayout.addWidget(self.pushButton3, 0, 2, 1, 1)

        self.pushButton4 = QPushButton(self.centralwidget)
        self.pushButton4.setObjectName(u"pushButton4")

        self.gridLayout.addWidget(self.pushButton4, 1, 0, 1, 1)

        self.pushButton5 = QPushButton(self.centralwidget)
        self.pushButton5.setObjectName(u"pushButton5")

        self.gridLayout.addWidget(self.pushButton5, 1, 1, 1, 1)

        self.spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.spacer, 1, 2, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1280, 33))
        self.menutest = QMenu(self.menubar)
        self.menutest.setObjectName(u"menutest")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menutest.menuAction())

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pushButton1.setText(QCoreApplication.translate("MainWindow", u"Button 1", None))
        self.pushButton2.setText(QCoreApplication.translate("MainWindow", u"Button 2", None))
        self.pushButton3.setText(QCoreApplication.translate("MainWindow", u"Button 3", None))
        self.pushButton4.setText(QCoreApplication.translate("MainWindow", u"Button 4", None))
        self.pushButton5.setText(QCoreApplication.translate("MainWindow", u"Button 5", None))
        self.menutest.setTitle(QCoreApplication.translate("MainWindow", u"main", None))
    # retranslateUi

