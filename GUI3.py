import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox,
                             QHBoxLayout, QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QFrame, QSplitter,
                             QTextEdit,QVBoxLayout, QMainWindow, QWidget, QDesktopWidget, QAction, qApp,
                             QRadioButton, QProgressBar, QMessageBox, QFileDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (pyqtSlot, Qt, QTimer)

from PyQt5.QtCore import QThread, pyqtSignal


import time
import os
import CLI
import Brocade
import Cisco


class MyThread(QThread):
    def __init__(self, parent=None):
        super(MyThread, self).__init__(parent)

    def __del__(self):
        self.wait()

    def pass_parameters(self, path2, ip2, username2, password2):
        print(path2)
        self.file = open(path2, "w")
        print("opened file")
        time.sleep(30)
        self.txt = CLI.connection(ip2, username2, password2)
        time.sleep(30)
        for x in range(len(self.txt)):
            self.file.write(self.txt[x])
        self.file.close()
        print("wrote")


class progressThread(QThread):

    progress_update = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super(progressThread, self).__init__(parent)

    def __del__(self):
        self.wait()

    def run(self):
        while 1:
            maxVal = 100
            self.progress_update.emit(maxVal)
            time.sleep(1)

    def updateProgressBar(self, maxVal):
        FormWidget.progressBar.setValue(FormWidget.progressBar.value() + maxVal)
        if maxVal == 0:
            FormWidget.progressBar.setValue(100)


class App(QMainWindow):

    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.title = 'TC Automation Tool'
        self.setWindowIcon(QIcon('icon.ico'))
        self.form_wid = FormWidget(self)
        self.setCentralWidget(self.form_wid)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.toolbar = self.addToolBar('Save')
        save_action = QAction(QIcon('save.ico'), '&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip("Save the output")

        exit_action = QAction(QIcon('exit2.ico'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip("Exit the Tool")
        exit_action.triggered.connect(qApp.quit)

        self.toolbar.addAction(save_action)
        self.toolbar.addAction(exit_action)

        self.setGeometry(160, 100, 900, 800)


class FormWidget(QWidget):

    def __init__(self, parent):
        super(FormWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.progressBar = QProgressBar()

        self.SN = QLabel('Serial Number: ')
        self.SN.setFont(QtGui.QFont('Times New Roman', 11))
        self.SN_num = QLineEdit(self)
        self.SN_num.textChanged.connect(self.text_SN)
        self.SN_num.setFont(QtGui.QFont('Times New Roman', 11))
        self.SN_num_label = QLabel(self)

        self.type = QLabel('Choose Type:')
        self.type.setFont(QtGui.QFont('Times New Roman', 11))
        self.cisco = QRadioButton('Cisco')
        self.cisco.setFont(QtGui.QFont('Times New Roman', 11))
        self.brocade = QRadioButton('Brocade')
        self.brocade.setFont(QtGui.QFont('Times New Roman', 11))

        self.h_box1 = QHBoxLayout(self)
        self.h_box1.addWidget(self.type)
        self.h_box1.addWidget(self.cisco)
        self.h_box1.addWidget(self.brocade)
        self.h_box1.addStretch()
        self.h_box1.setAlignment(Qt.AlignHCenter)

        self.current = QLabel('Target Code: ')
        self.current.setFont(QtGui.QFont('Times New Roman', 11))
        self.comboBox = QComboBox()
        self.comboBox.setFont(QtGui.QFont('Times New Roman', 11))
        self.brocade.toggled.connect(self.onClicked)
        self.cisco.toggled.connect(self.onClicked)
        self.comboBox.activated.connect(self.handleActivated)

        self.comboBox2 = QComboBox()
        self.comboBox2.setFont(QtGui.QFont('Times New Roman', 11))
        self.comboBox2.activated.connect(self.handleActivated2)

        self.h_box2 = QHBoxLayout()
        self.h_box2.addWidget(self.current)
        self.h_box2.addWidget(self.comboBox)
        self.h_box2.addWidget(self.comboBox2)
        self.h_box2.addStretch()

        self.h_box0 = QHBoxLayout()
        self.h_box0.addWidget(self.SN)
        self.h_box0.addWidget(self.SN_num)
        self.h_box0.addWidget(self.SN_num_label)
        self.h_box0.addStretch()

        self.ip = QLabel('IP address')
        self.ip.setFont(QtGui.QFont('Times New Roman', 11))
        self.ip_inp = QLineEdit(self)
        self.ip_inp.setFont(QtGui.QFont('Times New Roman', 11))

        self.h_box3 = QHBoxLayout()
        self.h_box3.addWidget(self.ip)
        self.h_box3.addWidget(self.ip_inp)
        self.h_box3.addStretch()

        self.username = QLabel('Username')
        self.username.setFont(QtGui.QFont('Times New Roman', 11))
        self.username_inp = QLineEdit(self)
        self.username_inp.setFont(QtGui.QFont('Times New Roman', 11))

        self.h_box4 = QHBoxLayout()
        self.h_box4.addWidget(self.username)
        self.h_box4.addWidget(self.username_inp)
        self.h_box4.addStretch()

        self.password = QLabel('Password')
        self.password.setFont(QtGui.QFont('Times New Roman', 11))
        self.password_inp = QLineEdit(self)
        self.password_inp.setFont(QtGui.QFont('Times New Roman', 11))

        self.h_box5 = QHBoxLayout()
        self.h_box5.addWidget(self.password)
        self.h_box5.addWidget(self.password_inp)
        self.h_box5.addStretch()

        self.submit_btn = QPushButton('Submit')
        self.submit_btn.setFixedWidth(120)
        self.submit_btn.clicked.connect(self.connection)

        self.browse_btn = QPushButton('Browse')
        self.browse_btn.setFixedWidth(120)
        self.browse_btn.clicked.connect(self.browse_connection)

        self.layout.addLayout(self.h_box0)
        self.layout.addLayout(self.h_box1)
        self.layout.addLayout(self.h_box2)
        self.layout.addLayout(self.h_box3)
        self.layout.addLayout(self.h_box4)
        self.layout.addLayout(self.h_box5)
        self.layout.addWidget(self.submit_btn)
        #self.layout.addWidget(self.browse_btn)
        self.layout.addWidget(self.progressBar)

        self.layout.addStretch()

        self.layout.setAlignment(Qt.AlignHCenter)
        self.setLayout(self.layout)
        self.show()

    def onClicked(self):
        if self.brocade.isChecked():
            self.comboBox.clear()
            self.comboBox.addItem('6.4.x')
            self.comboBox.addItem('7.0.x')
            self.comboBox.addItem('7.1.x')
            self.comboBox.addItem('7.2.x')
            self.comboBox.addItem('7.3.x')
            self.comboBox.addItem('7.4.x')
            self.comboBox.addItem('8.0.x')
            self.comboBox.addItem('8.1.x')
            self.comboBox.addItem('8.2.x')

        elif self.cisco.isChecked():
            self.comboBox.clear()
            self.comboBox.addItem('5.0x')
            self.comboBox.addItem('5.2x')
            self.comboBox.addItem('6.2x')
            self.comboBox.addItem('7.3x')
            self.comboBox.addItem('8.1x')
            self.comboBox.addItem('8.2x')
            self.comboBox.addItem('8.3x')

    def handleActivated(self, index):
        print(self.comboBox.itemText(index))
        if '6.4.x' in self.comboBox.itemText(index):
            self.comboBox2.clear()
            self.comboBox2.addItem('6.4.3g')

        if '7.0.x' in self.comboBox.itemText(index):
            self.comboBox2.clear()
            self.comboBox2.addItem('EOPS')

        if '7.1.x' in self.comboBox.itemText(index):
            self.comboBox2.clear()
            self.comboBox2.addItem('7.1.0c')
            self.comboBox2.addItem('7.4.1e')
            self.comboBox2.addItem('7.4.2')
            self.comboBox2.addItem('7.4.2a')
            self.comboBox2.addItem('7.4.2b')
            self.comboBox2.addItem('7.4.2c')
            self.comboBox2.addItem('7.4.2d')

        if '7.2.x' in self.comboBox.itemText(index):
            self.comboBox2.clear()
            self.comboBox2.addItem('7.2.1d')

        if '7.3.x' in self.comboBox.itemText(index):
            self.comboBox2.clear()
            self.comboBox2.addItem('7.3.0b')
            self.comboBox2.addItem('7.3.1c')
            self.comboBox2.addItem('7.3.1e')
            self.comboBox2.addItem('7.3.2b')

        if '7.4.x' in self.comboBox.itemText(index):
            self.comboBox2.clear()
            self.comboBox2.addItem('7.4.1d')
            self.comboBox2.addItem('7.4.1e')
            self.comboBox2.addItem('7.4.2')
            self.comboBox2.addItem('7.4.2a')
            self.comboBox2.addItem('7.4.2b')
            self.comboBox2.addItem('7.4.2c')
            self.comboBox2.addItem('7.4.2d')

        if '8.0.x' in self.comboBox.itemText(index):
            self.comboBox2.clear()
            self.comboBox2.addItem('8.0.1b')
            self.comboBox2.addItem('8.0.2b')
            self.comboBox2.addItem('8.0.2c')
            self.comboBox2.addItem('8.0.2d')
            self.comboBox2.addItem('8.0.2f')

        if '8.1.x' in self.comboBox.itemText(index):
            self.comboBox2.clear()
            self.comboBox2.addItem('8.1.0a')
            self.comboBox2.addItem('8.1.0c')
            self.comboBox2.addItem('8.1.1a')
            self.comboBox2.addItem('8.1.2a')
            self.comboBox2.addItem('8.1.2b')
            self.comboBox2.addItem('8.1.2d')
            self.comboBox2.addItem('8.1.2f')

        if '5.0x' in self.comboBox.itemText(index):
            self.comboBox2.clear()
            self.comboBox2.addItem('5.0(8a)')

        if '5.2x' in self.comboBox.itemText(index):
            self.comboBox2.clear()
            self.comboBox2.addItem('5.2(2)')
            self.comboBox2.addItem('5.2(8b)')
            self.comboBox2.addItem('5.2(8c)')
            self.comboBox2.addItem('5.2(8d)')
            self.comboBox2.addItem('5.2(8e)')
            self.comboBox2.addItem('5.2(8f)')
            self.comboBox2.addItem('5.2(8h)')
            self.comboBox2.addItem('5.2(8i)')

        if '6.2x' in self.comboBox.itemText(index):
            self.comboBox2.clear()
            self.comboBox2.addItem('6.2(1)')
            self.comboBox2.addItem('6.2(3)')
            self.comboBox2.addItem('6.2(5)')
            self.comboBox2.addItem('6.2(5a)')
            self.comboBox2.addItem('6.2(7)')
            self.comboBox2.addItem('6.2(9)')
            self.comboBox2.addItem('6.2(9a)')
            self.comboBox2.addItem('6.2(11)')
            self.comboBox2.addItem('6.2(11b)')
            self.comboBox2.addItem('6.2(11c)')
            self.comboBox2.addItem('6.2(11e)')
            self.comboBox2.addItem('6.2(13)')
            self.comboBox2.addItem('6.2(13a)')
            self.comboBox2.addItem('6.2(17)')
            self.comboBox2.addItem('6.2(19)')
            self.comboBox2.addItem('6.2(21)')
            self.comboBox2.addItem('6.2(23)')
            self.comboBox2.addItem('6.2(25)')

        if '8.1.x' in self.comboBox.itemText(index):
            self.comboBox2.clear()
            self.comboBox2.addItem('8.1(1)')
            self.comboBox2.addItem('8.1(1a)')
            self.comboBox2.addItem('8.1(1b)')

        if '8.2.x' in self.comboBox.itemText(index):
            self.comboBox2.clear()
            self.comboBox2.addItem('8.2.0a')
            self.comboBox2.addItem('8.2.0b')
            self.comboBox2.addItem('8.2.1a')

        if '7.3x' in self.comboBox.itemText(index):
            self.comboBox2.clear()
            self.comboBox2.addItem('7.3(0)D1(1)')
            self.comboBox2.addItem('7.3(0)DY(1)')
            self.comboBox2.addItem('7.3(1)D1(1)')
            self.comboBox2.addItem('7.3(1)DY(1)')

        if '8.1x' in self.comboBox.itemText(index):
            self.comboBox2.clear()
            self.comboBox2.addItem('8.1(1)')
            self.comboBox2.addItem('8.1(1a)')
            self.comboBox2.addItem('8.1(1b)')

        if '8.2x' in self.comboBox.itemText(index):
            self.comboBox2.clear()
            self.comboBox2.addItem('8.2(1)')
            self.comboBox2.addItem('8.2(2)')

        if '8.3x' in self.comboBox.itemText(index):
            self.comboBox2.clear()
            self.comboBox2.addItem('8.3(1)')

    def handleActivated2(self, index):
        print(self.comboBox2.itemText(index))
        self.target = self.comboBox2.itemText(index)
        return self.target

    def text_SN(self):
        self.SN_num_label.setText('SN number => ' + self.SN_num.text())

    def browse_connection(self):
        self.fileName = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()",  "", "Text Files (*.txt)")
        self.file = open(os.path.join(r'' + self.fileName[0]), "w")
        print("done")

    def connection(self, index):
        self.fileName = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()",  "", "Text Files (*.txt)")
        self.basepath = os.path.join(r'' + self.fileName[0])
        #self.file = open(self.basepath, "w")
        con_thread = MyThread()
        print("MyThread")
        #progress_thread = progressThread()
        #progress_thread.start(self)
        print("started")
        #self.progress_thread.progress_update(value)
        #print("connected")
        print(self.basepath)
        tmp = self.basepath
        tmp2 = self.ip_inp.text()
        tmp3 = self.username_inp.text()
        tmp4 = self.password_inp.text()
        con_thread.pass_parameters(tmp, tmp2, tmp3, tmp4)
        print("mythread started")
        #self.txt = (CLI.connection(self.ip_inp.text(), self.username_inp.text(), self.password_inp.text()))

        """for x in range(len(self.txt)):
            self.file.write(self.txt[x])
        self.file.close()
        print("wrote")
        if self.brocade.isChecked():
            Brocade.main(self.SN_num.text(), self.target, (os.path.dirname(self.basepath)), self.basepath)
            print(self.basepath)
        elif self.cisco.isChecked():
            Cisco.main(self.SN_num.text(), self.target, (os.path.dirname(self.basepath)), self.basepath)
            print(self.basepath)
            """
    def onCountChanged(self, value):
        self.progressBar.setValue(value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())


