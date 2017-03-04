# -*- coding: utf-8 -*-

# Form implementation originally generated from reading ui file 'CueEdit-3.ui'
# Now maintained by hand as controls are now added by list so they can be iterated
# Originally Created by: PyQt5 UI code generator 5.7
#
# WARNING! No longer associated with CueEdit-3.ui
#
import os, inspect, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
print(currentdir)
syblingdir =  os.path.dirname(currentdir) + '/ShowControl/utils'
print(syblingdir)
parentdir = os.path.dirname(currentdir)
print(parentdir)
sys.path.insert(0,syblingdir)
print(sys.path)


from PyQt5 import QtCore, QtGui, QtWidgets
from Cues import cue_types, cue_subelements, cue_edit_sizes, cue_subelements_tooltips, cue_fields

class Ui_dlgEditPrefs(object):
    def setupUi(self, dlgEditPrefs):
        dlgEditPrefs.setObjectName("dlgEditPrefs")
        dlgEditPrefs.setWindowModality(QtCore.Qt.ApplicationModal)
        dlgEditPrefs.resize(767, 803)
        dlgEditPrefs.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(dlgEditPrefs)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setHorizontalSpacing(2)
        self.gridLayout.setObjectName("gridLayout")

        self.lbl_list = []
        self.edt_list = []
        for i in range(cue_fields.__len__()):
            self.lbl_list.append(QtWidgets.QLabel(dlgEditPrefs))
            self.lbl_list[i].setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
            self.lbl_list[i].setIndent(0)
            self.lbl_list[i].setObjectName('lbl{0}'.format(cue_fields[i]))
            self.gridLayout.addWidget(self.lbl_list[i], i, 0, 1, 1)
            if cue_fields[i] == 'Cue_Type':
                self.edt_list.append(QtWidgets.QToolButton(dlgEditPrefs))
                self.edt_list[i].setObjectName('tbt{0}'.format(cue_fields[i]))
            else:
                self.edt_list.append(QtWidgets.QPlainTextEdit(dlgEditPrefs))
                size_list = cue_edit_sizes[i].split(',')
                self.edt_list[i].setMaximumSize(QtCore.QSize(int(size_list[0]),int(size_list[1])))
                self.edt_list[i].setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
                self.edt_list[i].setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
                self.edt_list[i].setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
                self.edt_list[i].setTabChangesFocus(True)
                self.edt_list[i].setObjectName('pedt{0}'.format(cue_fields[i]))
            self.edt_list[i].setToolTip(cue_subelements_tooltips[i])
            self.gridLayout.addWidget(self.edt_list[i], i, 1, 1, 1)

        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        spacerItem1 = QtWidgets.QSpacerItem(629, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.buttonBox = QtWidgets.QDialogButtonBox(dlgEditPrefs)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(dlgEditPrefs)
        self.buttonBox.accepted.connect(dlgEditPrefs.accept)
        self.buttonBox.rejected.connect(dlgEditPrefs.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgEditPrefs)

    def retranslateUi(self, dlgEditPrefs):
        _translate = QtCore.QCoreApplication.translate
        dlgEditPrefs.setWindowTitle(_translate("dlgEditPrefs", "Edit Cue"))

        for i in range(cue_fields.__len__()):
            self.lbl_list[i].setText(_translate("dlgEditPrefs", cue_fields[i].replace('_', ' ')))
            if cue_fields[i] == 'Cue_Type':
                self.edt_list[i].setText(_translate("dlgEditPrefs", "..."))
            else:
                self.edt_list[i].setDocumentTitle(_translate("dlgEditPrefs", cue_fields[i].replace('_', ' ')))

