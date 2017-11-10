#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
    PyQt4 conversion of Qt Basic Sort/Filter Example

        The Basic Sort/Filter Model example illustrates how to use
        QSortFilterProxyModel to perform basic sorting and filtering.

    BEHAVIOUR:
    =========
    Filter options are implemented. Try different regular expressions,
    change the filter column or the sort column.

    NOTES:
    =====
    Implemented private slots:
        _filterRegExpChanged()
        _filterColumnChanged()
        _sortChanged()

    Redefined filterSyntaxComboBox, filterCaseSensitivityCheckBox,
    sortCaseSensitivityCheckBox, filterSyntaxComboBox and
    filterPatternLineEdit as attributes.

last modified: 2012-01-30 jg
ref:
    http://developer.qt.nokia.com/doc/qt-4.8/itemviews-basicsortfiltermodel.html

'''
# from PyQt5.QtGui import (QApplication, QWidget, QGroupBox, QHBoxLayout, QLabel,
#                          QVBoxLayout, QGridLayout, QTreeView, QSortFilterProxyModel,
#                          QCheckBox, QLineEdit, QComboBox, QStandardItemModel)
# from PyQt4.QtCore import (Qt, pyqtSlot, QRegExp, QDateTime, QDate, QTime)

from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class Window(QWidget):
    def __init__(self, parent=None):  # initialise base class
        super(Window, self).__init__(parent)

        layout = QVBoxLayout()
        layout.addWidget(self._createSourcePanel())
        layout.addWidget(self._createProxyPanel())
        self.setLayout(layout)

        # set initial filter column and regexp
        self._filterColumnComboBox.setCurrentIndex(1)
        self._filterPatternLineEdit.setText("Grace|Andy")

    # public methods ----------------------------------------------------------
    def setSourceModel(self, model):
        self._proxyModel.setSourceModel(model)
        self._sourceView.setModel(model)

    # private methods ---------------------------------------------------------
    def _createSourcePanel(self):
        sourceGroupBox = QGroupBox(self.tr("Original Model"))
        self._sourceView = QTreeView()
        self._sourceView.setRootIsDecorated(False)
        self._sourceView.setAlternatingRowColors(True)

        sourceLayout = QHBoxLayout()
        sourceLayout.addWidget(self._sourceView)
        sourceGroupBox.setLayout(sourceLayout)

        return sourceGroupBox

    def _createProxyPanel(self):
        proxyGroupBox = QGroupBox(self.tr("Sorted/Filter Model"))
        proxyView = QTreeView()
        proxyView.setRootIsDecorated(False)
        proxyView.setAlternatingRowColors(True)
        proxyView.sortByColumn(1, Qt.AscendingOrder)

        self._proxyModel = QSortFilterProxyModel()
        self._proxyModel.setDynamicSortFilter(True)
        proxyView.setModel(self._proxyModel)
        proxyView.setSortingEnabled(True)  # click col hdr to sort

        proxyLayout = QVBoxLayout()
        proxyLayout.addWidget(proxyView)
        proxyLayout.addLayout(self._createProxyFilterPanel())
        proxyGroupBox.setLayout(proxyLayout)

        return proxyGroupBox

    def _createProxyFilterPanel(self):

        self._sortCaseSensitivityCheckBox = QCheckBox(self.tr("Case sensitive sorting"));
        self._filterCaseSensitivityCheckBox = QCheckBox(self.tr("Case sensitive filter"));

        # default for case sensitivity is true so check boxes
        self._sortCaseSensitivityCheckBox.setChecked(True)
        self._filterCaseSensitivityCheckBox.setChecked(True)

        self._filterPatternLineEdit = QLineEdit();
        filterPatternLabel = QLabel(self.tr("&Filter pattern:"));
        filterPatternLabel.setBuddy(self._filterPatternLineEdit);

        self._filterSyntaxComboBox = QComboBox();
        self._filterSyntaxComboBox.addItem(self.tr("Regular expression"), QRegExp.RegExp);
        self._filterSyntaxComboBox.addItem(self.tr("Wildcard"), QRegExp.Wildcard);
        self._filterSyntaxComboBox.addItem(self.tr("Fixed string"), QRegExp.FixedString);
        filterSyntaxLabel = QLabel(self.tr("Filter &syntax:"));
        filterSyntaxLabel.setBuddy(self._filterSyntaxComboBox);

        self._filterColumnComboBox = QComboBox();
        self._filterColumnComboBox.addItem(self.tr("Subject"));
        self._filterColumnComboBox.addItem(self.tr("Sender"));
        self._filterColumnComboBox.addItem(self.tr("Date"));
        filterColumnLabel = QLabel(self.tr("Filter &column:"));
        filterColumnLabel.setBuddy(self._filterColumnComboBox);

        # connect signals/slots for event handling
        self._filterPatternLineEdit.textChanged.connect(self._filterRegExpChanged)
        self._filterSyntaxComboBox.currentIndexChanged.connect(self._filterRegExpChanged)
        self._filterColumnComboBox.currentIndexChanged.connect(self._filterColumnChanged)
        self._filterCaseSensitivityCheckBox.toggled.connect(self._filterRegExpChanged)
        self._sortCaseSensitivityCheckBox.toggled.connect(self._sortChanged)

        grid = QGridLayout()
        grid.addWidget(filterPatternLabel, 0, 0)
        grid.addWidget(self._filterPatternLineEdit, 0, 1)
        grid.addWidget(filterSyntaxLabel, 1, 0)
        grid.addWidget(self._filterSyntaxComboBox, 1, 1)
        grid.addWidget(filterColumnLabel, 2, 0)
        grid.addWidget(self._filterColumnComboBox, 2, 1)
        grid.addWidget(self._filterCaseSensitivityCheckBox, 3, 0)
        grid.addWidget(self._sortCaseSensitivityCheckBox, 3, 1, Qt.AlignRight)

        return grid

    # private slots -----------------------------------------------------------
    @pyqtSlot()
    def _filterRegExpChanged(self):
        # get the QRegEx.PatternSyntax enum value
        # 0 - Regular Expression
        # 1 - Wildcard
        # 2 - Fixed String
        syntax = self._filterSyntaxComboBox.itemData(
            self._filterSyntaxComboBox.currentIndex())

        # get case sensitivity
        cs = Qt.CaseInsensitive
        if self._filterCaseSensitivityCheckBox.isChecked():
            cs = Qt.CaseSensitive

        # get user regex pattern
        pattern = self._filterPatternLineEdit.text()

        # build filter and update proxy model
        regExp = QRegExp(pattern, cs, syntax)
        self._proxyModel.setFilterRegExp(regExp)

    @pyqtSlot()
    def _filterColumnChanged(self):
        self._proxyModel.setFilterKeyColumn(
            self._filterColumnComboBox.currentIndex())

    @pyqtSlot()
    def _sortChanged(self):
        cs = Qt.CaseInsensitive

        if self._sortCaseSensitivityCheckBox.isChecked():
            cs = Qt.CaseSensitive

        self._proxyModel.setSortCaseSensitivity(cs)


# createMailModel() ==========================================================
def createMailModel(parent):
    # create, populate and return a 'QStandardItemModel' object
    model = QStandardItemModel(0, 3, parent)

    model.setHeaderData(0, Qt.Horizontal, parent.tr("Subject"))
    model.setHeaderData(1, Qt.Horizontal, parent.tr("Sender"))
    model.setHeaderData(2, Qt.Horizontal, parent.tr("Date"))

    addMail(model, "Happy New Year!", "Grace K. ",
            QDateTime(QDate(2006, 12, 31), QTime(17, 3)))
    addMail(model, "Radically new concept", "Grace K. ",
            QDateTime(QDate(2006, 12, 22), QTime(9, 44)))
    addMail(model, "Accounts", "pascale@nospam.com",
            QDateTime(QDate(2006, 12, 31), QTime(12, 50)))
    addMail(model, "Expenses", "Joe Bloggs ",
            QDateTime(QDate(2006, 12, 25), QTime(11, 39)))
    addMail(model, "Re: Expenses", "Andy ",
            QDateTime(QDate(2007, 1, 2), QTime(16, 5)))
    addMail(model, "Re: Accounts", "Joe Bloggs ",
            QDateTime(QDate(2007, 1, 3), QTime(14, 18)))
    addMail(model, "Re: Accounts", "Andy ",
            QDateTime(QDate(2007, 1, 3), QTime(14, 26)))
    addMail(model, "Sports", "Linda Smith ",
            QDateTime(QDate(2007, 1, 5), QTime(11, 33)))
    addMail(model, "AW: Sports", "Rolf Newschweinstein ",
            QDateTime(QDate(2007, 1, 5), QTime(12, 0)))
    addMail(model, "RE: Sports", "Petra Schmidt ",
            QDateTime(QDate(2007, 1, 5), QTime(12, 1)))

    return model


# addMail() ==================================================================
def addMail(model, subject, sender, date):
    # insert a row of data into the given model
    model.insertRow(0)
    model.setData(model.index(0, 0), subject)
    model.setData(model.index(0, 1), sender)
    model.setData(model.index(0, 2), date)


# main ========================================================================
def main():
    import sys

    app = QApplication(sys.argv)
    mw = Window()
    mw.setSourceModel(createMailModel(mw))
    mw.setWindowTitle("Basic Sort/Filter Model - Part 3")
    mw.resize(500, 450)
    mw.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()