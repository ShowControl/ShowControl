# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CueEdit-3.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dlgEditCue(object):
    def setupUi(self, dlgEditCue):
        dlgEditCue.setObjectName("dlgEditCue")
        dlgEditCue.setWindowModality(QtCore.Qt.ApplicationModal)
        dlgEditCue.resize(767, 803)
        dlgEditCue.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(dlgEditCue)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setHorizontalSpacing(2)
        self.gridLayout.setObjectName("gridLayout")
        self.lblCue = QtWidgets.QLabel(dlgEditCue)
        self.lblCue.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblCue.setIndent(0)
        self.lblCue.setObjectName("lblCue")
        self.gridLayout.addWidget(self.lblCue, 0, 0, 1, 1)
        self.plainTextEditTitle = QtWidgets.QPlainTextEdit(dlgEditCue)
        self.plainTextEditTitle.setMaximumSize(QtCore.QSize(16777215, 20))
        self.plainTextEditTitle.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.plainTextEditTitle.setTabChangesFocus(True)
        self.plainTextEditTitle.setObjectName("plainTextEditTitle")
        self.gridLayout.addWidget(self.plainTextEditTitle, 6, 1, 1, 1)
        self.plainTextEditCueNum = QtWidgets.QPlainTextEdit(dlgEditCue)
        self.plainTextEditCueNum.setMinimumSize(QtCore.QSize(0, 0))
        self.plainTextEditCueNum.setMaximumSize(QtCore.QSize(60, 20))
        self.plainTextEditCueNum.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.plainTextEditCueNum.setTabChangesFocus(True)
        self.plainTextEditCueNum.setReadOnly(True)
        self.plainTextEditCueNum.setObjectName("plainTextEditCueNum")
        self.gridLayout.addWidget(self.plainTextEditCueNum, 0, 1, 1, 1)
        self.lblTitle = QtWidgets.QLabel(dlgEditCue)
        self.lblTitle.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblTitle.setIndent(0)
        self.lblTitle.setObjectName("lblTitle")
        self.gridLayout.addWidget(self.lblTitle, 6, 0, 1, 1)
        self.llblId = QtWidgets.QLabel(dlgEditCue)
        self.llblId.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.llblId.setIndent(0)
        self.llblId.setObjectName("llblId")
        self.gridLayout.addWidget(self.llblId, 5, 0, 1, 1)
        self.plainTextEditPage = QtWidgets.QPlainTextEdit(dlgEditCue)
        self.plainTextEditPage.setMaximumSize(QtCore.QSize(60, 20))
        self.plainTextEditPage.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.plainTextEditPage.setTabChangesFocus(True)
        self.plainTextEditPage.setObjectName("plainTextEditPage")
        self.gridLayout.addWidget(self.plainTextEditPage, 4, 1, 1, 1)
        self.plainTextEditAct = QtWidgets.QPlainTextEdit(dlgEditCue)
        self.plainTextEditAct.setMaximumSize(QtCore.QSize(60, 20))
        self.plainTextEditAct.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.plainTextEditAct.setTabChangesFocus(True)
        self.plainTextEditAct.setObjectName("plainTextEditAct")
        self.gridLayout.addWidget(self.plainTextEditAct, 2, 1, 1, 1)
        self.lblPage = QtWidgets.QLabel(dlgEditCue)
        self.lblPage.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblPage.setIndent(0)
        self.lblPage.setObjectName("lblPage")
        self.gridLayout.addWidget(self.lblPage, 4, 0, 1, 1)
        self.lblScene = QtWidgets.QLabel(dlgEditCue)
        self.lblScene.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblScene.setIndent(0)
        self.lblScene.setObjectName("lblScene")
        self.gridLayout.addWidget(self.lblScene, 3, 0, 1, 1)
        self.lblAct = QtWidgets.QLabel(dlgEditCue)
        self.lblAct.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblAct.setIndent(0)
        self.lblAct.setObjectName("lblAct")
        self.gridLayout.addWidget(self.lblAct, 2, 0, 1, 1)
        self.plainTextEditScene = QtWidgets.QPlainTextEdit(dlgEditCue)
        self.plainTextEditScene.setMaximumSize(QtCore.QSize(60, 20))
        self.plainTextEditScene.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.plainTextEditScene.setTabChangesFocus(True)
        self.plainTextEditScene.setObjectName("plainTextEditScene")
        self.gridLayout.addWidget(self.plainTextEditScene, 3, 1, 1, 1)
        self.plainTextEditId = QtWidgets.QPlainTextEdit(dlgEditCue)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plainTextEditId.sizePolicy().hasHeightForWidth())
        self.plainTextEditId.setSizePolicy(sizePolicy)
        self.plainTextEditId.setMaximumSize(QtCore.QSize(16777215, 20))
        self.plainTextEditId.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.plainTextEditId.setTabChangesFocus(True)
        self.plainTextEditId.setObjectName("plainTextEditId")
        self.gridLayout.addWidget(self.plainTextEditId, 5, 1, 1, 1)
        self.plainTextEditPrompt = QtWidgets.QPlainTextEdit(dlgEditCue)
        self.plainTextEditPrompt.setMaximumSize(QtCore.QSize(16777215, 20))
        self.plainTextEditPrompt.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.plainTextEditPrompt.setTabChangesFocus(True)
        self.plainTextEditPrompt.setObjectName("plainTextEditPrompt")
        self.gridLayout.addWidget(self.plainTextEditPrompt, 7, 1, 1, 1)
        self.lblPrompt = QtWidgets.QLabel(dlgEditCue)
        self.lblPrompt.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblPrompt.setIndent(0)
        self.lblPrompt.setObjectName("lblPrompt")
        self.gridLayout.addWidget(self.lblPrompt, 7, 0, 1, 1)
        self.lblType = QtWidgets.QLabel(dlgEditCue)
        self.lblType.setMaximumSize(QtCore.QSize(102, 26))
        self.lblType.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblType.setObjectName("lblType")
        self.gridLayout.addWidget(self.lblType, 1, 0, 1, 1)
        self.toolButton = QtWidgets.QToolButton(dlgEditCue)
        self.toolButton.setObjectName("toolButton")
        self.gridLayout.addWidget(self.toolButton, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        spacerItem1 = QtWidgets.QSpacerItem(629, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.buttonBox = QtWidgets.QDialogButtonBox(dlgEditCue)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(dlgEditCue)
        self.buttonBox.accepted.connect(dlgEditCue.accept)
        self.buttonBox.rejected.connect(dlgEditCue.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgEditCue)
        dlgEditCue.setTabOrder(self.plainTextEditCueNum, self.plainTextEditAct)
        dlgEditCue.setTabOrder(self.plainTextEditAct, self.plainTextEditScene)
        dlgEditCue.setTabOrder(self.plainTextEditScene, self.plainTextEditPage)
        dlgEditCue.setTabOrder(self.plainTextEditPage, self.plainTextEditId)
        dlgEditCue.setTabOrder(self.plainTextEditId, self.plainTextEditTitle)
        dlgEditCue.setTabOrder(self.plainTextEditTitle, self.plainTextEditPrompt)
        dlgEditCue.setTabOrder(self.plainTextEditPrompt, self.buttonBox)

    def retranslateUi(self, dlgEditCue):
        _translate = QtCore.QCoreApplication.translate
        dlgEditCue.setWindowTitle(_translate("dlgEditCue", "Edit Cue"))
        self.lblCue.setText(_translate("dlgEditCue", "Cue Number"))
        self.plainTextEditTitle.setDocumentTitle(_translate("dlgEditCue", "Title"))
        self.plainTextEditCueNum.setDocumentTitle(_translate("dlgEditCue", "CueNum"))
        self.lblTitle.setText(_translate("dlgEditCue", "Title"))
        self.llblId.setText(_translate("dlgEditCue", "Id"))
        self.plainTextEditPage.setDocumentTitle(_translate("dlgEditCue", "Page"))
        self.plainTextEditAct.setDocumentTitle(_translate("dlgEditCue", "Act"))
        self.lblPage.setText(_translate("dlgEditCue", "Page"))
        self.lblScene.setText(_translate("dlgEditCue", "Scene"))
        self.lblAct.setText(_translate("dlgEditCue", "Act"))
        self.plainTextEditScene.setDocumentTitle(_translate("dlgEditCue", "Scene"))
        self.plainTextEditId.setDocumentTitle(_translate("dlgEditCue", "Id"))
        self.plainTextEditPrompt.setDocumentTitle(_translate("dlgEditCue", "Prompt"))
        self.lblPrompt.setText(_translate("dlgEditCue", "Dialog/Prompt"))
        self.lblType.setText(_translate("dlgEditCue", "Cue Type"))
        self.toolButton.setText(_translate("dlgEditCue", "..."))

