from ui import MyMainWindow
from PySide6.QtWidgets import QApplication

app = QApplication([])
mainwindow = MyMainWindow()
mainwindow.show()
app.aboutToQuit.connect(mainwindow.roll.window.close)
app.exec()