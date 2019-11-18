# import necessary packages
import logging
logging.basicConfig(filename='logs.log'+'', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
import vision.yolov3_object_detection as vision
from vision.yolov3_object_detection import draw_bbox
import sys, cv2, config
from speech.tts import TextToSpeech
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt



class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class Thread(QtCore.QThread):
    changePixmap = pyqtSignal(QtGui.QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                # detectObject(frame)
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QtGui.QImage(rgbImage.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)
 

    


class Assistant(QtWidgets.QDialog, QtWidgets.QPlainTextEdit):
    def __init__(self, tts, parent=None, ):
        super().__init__(parent)
        self.tts = tts

        logTextBox = QTextEditLogger(self)
        # You can format what is printed to text box
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.DEBUG)

        self._button = QtWidgets.QPushButton(self)
        self._button.setText('Detect')

        layout = QtWidgets.QVBoxLayout()
        # Add the new logging box widget to the layout
        layout.addWidget(logTextBox.widget)
        layout.addWidget(self._button)
        self.setLayout(layout)

        # Connect signal to slot
        self._button.clicked.connect(self.test)
        self.initUI()

    def speak(self, frame, object, distance):
        self.tts.synthesize(object + " is " + distance + " away " + "from you")


    def detectObject(self, frame):
        # apply object detection
        bbox, label, conf = vision.detect_common_objects(frame)

        logging.info(str(bbox) + str(label) + str(conf))

        # draw bounding box over detected objects
        out = draw_bbox(frame, bbox, label, conf)

    @pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        self.label.setPixmap(QtGui.QPixmap.fromImage(image))

    def initUI(self):
        # self.setWindowTitle(self.title)
        # self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(800, 600)
        # create a label
        self.label = QtWidgets.QLabel(self)
        self.label.move(280, 120)
        self.label.resize(640, 480)
        th = Thread(self)
        th.changePixmap.connect(self.setImage)
        th.start()



if __name__ == '__main__':
    tts = TextToSpeech(config.AZURE_SPEECH_SERVICE_API_KEY)
    app = QtWidgets.QApplication(sys.argv)
    dlg = Assistant(tts=tts)
    dlg.show()
    dlg.raise_()
    sys.exit(app.exec_())

