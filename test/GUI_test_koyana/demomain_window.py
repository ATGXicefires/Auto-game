from PySide6.QtWidgets import QApplication,QMainWindow, QWidget

#from view1 import View
#from view2 import View

class mainWindow(QMainWindow,):
    def __init__(self):
        super().__init__()

        
        
if __name__ == "__main__":
    app = QApplication([])
    main_window = mainWindow()
    main_window.setGeometry(100, 100, 800, 600)
    
    main_window.show()
    
    app.exec()