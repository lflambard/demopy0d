import sys

from PySide6 import QtCore


class InitialCard(QtGui.QLabel):
    def __init__(self, text, parent):
        super(InitialCard, self).__init__(text, parent)
        self.setAutoFillBackground(True)
        self.setFrameStyle(QtGui.QFrame.WinPanel | QtGui.QFrame.Sunken)
        newFont = QtGui.QFont("MsReferenceSansSerif", 10)
        newFont.setBold(False)
        self.setFont(newFont)
        self.setMinimumSize(90, 25)
        self.setMaximumHeight(30)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.mimeText = self.text()

    def mouseMoveEvent(self, event):
        if not self.text():
            return
        mimeData = QtCore.QMimeData()
        mimeData.setText(self.mimeText)
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction, QtCore.Qt.CopyAction)


class CardsDropWidget(QtGui.QWidget):

    def __init__(self, parent):
        super(CardsDropWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.contentsVLO = QtGui.QVBoxLayout()
        self.contentsVLO.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.contentsVLO)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            cardSource = event.source()
            cardText = cardSource.text()
            if not cardSource in self.children():
                newCard = InitialCard(cardText, self)
                self.contentsVLO.addWidget(newCard)
                cardSource.clear()
            else:
                event.ignore()
        else:
            event.ignore()


class MainDialogue(QtGui.QDialog):
    def __init__(self, parent=None):
        super(MainDialogue, self).__init__(parent)
        self.label = InitialCard("initial", self)
        self.lineEdit = QtGui.QLineEdit("Create a Card Here!!")
        self.lineEdit.selectAll()
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollContent = CardsDropWidget(self.scrollArea)
        self.scrollArea.setMinimumWidth(150)
        self.scrollArea.setWidget(self.scrollContent)
        self.dialogueLayout = QtGui.QHBoxLayout()
        self.labelLayout = QtGui.QVBoxLayout()
        self.labelLayout.addWidget(self.label)
        self.labelLayout.addWidget(self.lineEdit)
        self.labelLayout.addStretch()
        self.dialogueLayout.addWidget(self.scrollArea)
        self.dialogueLayout.addLayout(self.labelLayout)
        self.setLayout(self.dialogueLayout)
        self.setWindowTitle("Drag and Drop")
        self.setMinimumSize(300, 150)
        self.lineEdit.returnPressed.connect(self.createCardTxt_fn)

    def createCardTxt_fn(self):
        cardTxt = unicode(self.lineEdit.text())
        self.label.setText(cardTxt)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainDialogue()
    window.show()
    sys.exit(app.exec_())