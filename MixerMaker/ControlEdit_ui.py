# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ControlEdit.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(498, 400)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 5, 0, 1, 1)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.tableView_ControlsInStrip = QtWidgets.QTableView(Dialog)
        self.tableView_ControlsInStrip.setObjectName("tableView_ControlsInStrip")
        self.gridLayout.addWidget(self.tableView_ControlsInStrip, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.lineEdit_CommandString = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_CommandString.setObjectName("lineEdit_CommandString")
        self.gridLayout.addWidget(self.lineEdit_CommandString, 3, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 6, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.lineEdit_DefaultValue = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_DefaultValue.setObjectName("lineEdit_DefaultValue")
        self.gridLayout.addWidget(self.lineEdit_DefaultValue, 6, 1, 1, 1)
        self.comboBox_ControlType = QtWidgets.QComboBox(Dialog)
        self.comboBox_ControlType.setObjectName("comboBox_ControlType")
        self.comboBox_ControlType.addItem("")
        self.comboBox_ControlType.addItem("")
        self.comboBox_ControlType.addItem("")
        self.gridLayout.addWidget(self.comboBox_ControlType, 2, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)
        self.lineEdit_Range = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_Range.setObjectName("lineEdit_Range")
        self.gridLayout.addWidget(self.lineEdit_Range, 5, 1, 1, 1)
        self.comboBox_CommandType = QtWidgets.QComboBox(Dialog)
        self.comboBox_CommandType.setObjectName("comboBox_CommandType")
        self.comboBox_CommandType.addItem("")
        self.comboBox_CommandType.addItem("")
        self.comboBox_CommandType.addItem("")
        self.gridLayout.addWidget(self.comboBox_CommandType, 4, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 7, 0, 1, 1)
        self.lineEdit_Anomalies = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_Anomalies.setObjectName("lineEdit_Anomalies")
        self.gridLayout.addWidget(self.lineEdit_Anomalies, 7, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.label_5.setBuddy(self.lineEdit_Range)
        self.label.setBuddy(self.tableView_ControlsInStrip)
        self.label_4.setBuddy(self.comboBox_CommandType)
        self.label_6.setBuddy(self.lineEdit_DefaultValue)
        self.label_3.setBuddy(self.lineEdit_CommandString)
        self.label_2.setBuddy(self.comboBox_ControlType)
        self.label_7.setBuddy(self.lineEdit_Anomalies)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Controls"))
        self.label_5.setText(_translate("Dialog", "Range"))
        self.label.setText(_translate("Dialog", "Controls In Strip"))
        self.label_4.setText(_translate("Dialog", "Command Type"))
        self.label_6.setText(_translate("Dialog", "Default Value"))
        self.label_3.setText(_translate("Dialog", "Command String"))
        self.label_2.setText(_translate("Dialog", "Control Type"))
        self.comboBox_ControlType.setItemText(0, _translate("Dialog", "fader"))
        self.comboBox_ControlType.setItemText(1, _translate("Dialog", "mute"))
        self.comboBox_ControlType.setItemText(2, _translate("Dialog", "scribble"))
        self.comboBox_CommandType.setItemText(0, _translate("Dialog", "level"))
        self.comboBox_CommandType.setItemText(1, _translate("Dialog", "enum"))
        self.comboBox_CommandType.setItemText(2, _translate("Dialog", "string"))
        self.label_7.setText(_translate("Dialog", "Anomalies"))

