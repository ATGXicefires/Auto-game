from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QFileDialog, QLabel, QPushButton
from PIL import Image, ImageFilter, ImageQt
from PySide6.QtCore    import Qt
from PySide6.QtGui     import QPixmap
 

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):
        self.Button = QPushButton("點我導入圖像")
        self.Button.clicked.connect(self.getImage)
        
        self.LabelShowImage = QLabel()
        
        self.Slider = QSlider(Qt.Orientation.Horizontal)
        self.Slider.setRange(0, 20)
        self.Slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.Slider.setTickInterval(3)
        self.Slider.valueChanged.connect(self.SliderValueChanged)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.Button)
        self.mainLayout.addWidget(self.LabelShowImage)
        self.mainLayout.addWidget(self.Slider)
        

        self.setLayout(self.mainLayout)

    def getImage(self):
        self.image = Image.open(QFileDialog.getOpenFileName(self, '選擇圖像', './', '圖像文件(*.png *.jpg)')[0])
        self.LabelShowImage.setPixmap(ImageQt.toqpixmap(self.image))

    def SliderValueChanged(self, Value):
        self.blurredImage = self.image.filter(ImageFilter.GaussianBlur(Value))
        self.LabelShowImage.setPixmap(ImageQt.toqpixmap(self.blurredImage))


if __name__ == '__main__' :
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()