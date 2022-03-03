from fileinput import filename
from re import S
import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QButtonGroup, QRadioButton, QTableView, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QMainWindow, QFormLayout
from PyQt5.QtWidgets import QScrollArea, QScrollBar, QAbstractScrollArea, QFileDialog
from PyQt5.QtCore import QThread, Qt, pyqtSignal
import os

"""
1. 无法读取已经标记过的文件
2. 让文件是可选的
3. 对于非O的标记，给予一定的颜色
"""
ner_config = {
    "ui": 1,
    "title": "Corpus Tool",
    "div": ' ',
    "width": 850,
    "word_label_width": 40,
    "label": ["O", "B-PER", "E-PER", "B-LOC", "E-LOC", "B-PRO","E-PRO","B-GEO","E-GEO", "B-ORG","E-ORG"],
    "label_size":[30, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65]
}

wordiv_config = {
    "ui": 2,
    "title": "Wordiv Tool",
    "div": ':',
    "width": 450,
    "word_label_width": 100,
    "label": ['Y', "N"],
    "label_size":[50, 50]
}

ner_label = ["O", "B-PER", "E-PER", "B-LOC", "E-LOC", "B-PRO","E-PRO","B-GEO","E-GEO", "B-ORG","E-ORG"]

class WordFlagWidget(QWidget):
    def __init__(self, word: str, checked: int, param: dict, parent=None) -> None:
        super(WordFlagWidget, self).__init__(parent)
        self.layout = QHBoxLayout()
        self.QWord = QLabel(word, self)
        self.QWord.setStyleSheet('font: 32; font-weight: bold')
        self.QWord.setFixedSize(param["word_label_width"], 18)
        self._word = word
        self.layout.addWidget(self.QWord)
        self.radioGroup = QButtonGroup(self)
        self.radios = []
        radio_size = param["label_size"]
        self.checked = checked
        self.checked_label = ""
        for i in range(len(param["label"])):
            RadioButton = QRadioButton(param["label"][i], self)
            RadioButton.setFixedSize(radio_size[i], 12)
            RadioButton.clicked.connect(self.check_state)
            self.radioGroup.addButton(RadioButton)
            self.radios.append(RadioButton)
            self.layout.addWidget(RadioButton)
        self.radios[self.checked].setChecked(True)
        self.checked_label = self.radios[self.checked].text()
        self.layout.addStretch()
        self.setLayout(self.layout)
        self.show()

    def check_state(self):
        radio = self.sender()
        self.checked_label = radio.text()
        self.setStyleSheet('QWidget{background-color:rgb(170,170,170)}')

    def getValue(self):
        text = self.QWord.text()
        return {"word": text, "label": self.checked_label}

class FilePanelWidget(QWidget):
    def __init__(self, button_name: str, label_name: str) -> None:
        super().__init__()
        self.layout = QHBoxLayout()
        self.Button = QPushButton(button_name, self)
        self.Button.resize(50,20)
        self.Label = QLabel(label_name, self)
        self.layout.addWidget(self.Button)
        self.layout.addWidget(self.Label)
        self.layout.addStretch(1)
        self.setLayout(self.layout)

class ImageWidget(QLabel):
    def setImage(self, image_path: str):
        if os.path.exists(image_path):
            self.setPixmap(QPixmap(image_path))

class NeuScrollArea(QScrollArea):
    def __init__(self, param: dict) -> None:
        super(NeuScrollArea, self).__init__()
        self.param = param
        self.widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.widget)
        self.setLayout(layout)
        # self.widget.setStyleSheet("QWidget{background-color:rgb(255,0,0)}")
        self.vlayout = QVBoxLayout()
        self.widget.setLayout(self.vlayout)
        self.setWidget(self.widget)
        self.word_label = []
    
    def addImage(self, image_path: str):
        widget = ImageWidget()
        widget.setImage(image_path)
        self.vlayout.addWidget(widget)
        self.widget.setLayout(self.vlayout)
        self.setWidget(self.widget)
    
    def setui(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.vlayout.setContentsMargins(0, 0, 0, 0)

    def loadui(self, ui_type, filename):
        self.backthread = ReadFile(filename, ui_type)
        if ui_type == 1:
            self.backthread.word_flag_widget.connect(self.generate_word_label)
        elif ui_type == 2:
            self.backthread.word_div.connect(self.generate_word_div)
        self.backthread.start()
        
    def generate_word_label(self, item: dict):
        w = WordFlagWidget(item["Text"], 0, self.param)
        self.word_label.append(w)
        self.vlayout.addWidget(w)
    
    def generate_word_div(self, item: str):
        w = WordFlagWidget(item, 1, self.param)
        self.word_label.append(w)
        self.vlayout.addWidget(w)
    

class ReadFile(QThread):
    word_flag_widget = pyqtSignal(dict)
    word_div = pyqtSignal(str)
    def __init__(self, file_name: str, event_type=1) -> None:
        super(ReadFile, self).__init__()
        self.filename = file_name
        self.event_type = event_type

    def run(self):
        i = 0
        with open(self.filename, 'r') as r:
            while line := r.readline():
                if self.event_type == 1:
                    self.word_flag_widget.emit(dict(Text=line[0], Label=0))
                elif self.event_type == 2:
                    result = line.split(':')
                    self.word_div.emit(result[0])
                i += 1
                if i == 50:
                    self.sleep(5)
                    i = 0
        
class Corpus_tool(QWidget):
    def __init__(self, param: dict) -> None:
        super(Corpus_tool, self).__init__()
        self.param = param
        title = param["title"]
        window_width = param["width"]
        self.setGeometry(100, 0, window_width, 600)
        self.setFixedWidth(window_width)
        self.setWindowTitle(title)

        self.vLayout = QVBoxLayout()

        self.filepanel = FilePanelWidget("Input", "file path.......................................")
        self.filepanel.Button.clicked.connect(self.openInputFile)
        self.vLayout.addWidget(self.filepanel)
        self.input_file = ''
        
        self.outputfilepanel = FilePanelWidget("Output", "file path.......................")
        self.outputfilepanel.Button.clicked.connect(self.openOutputFile)
        self.vLayout.addWidget(self.outputfilepanel)
        self.output_file = ''

        self.submitpanel = FilePanelWidget("Submit", "")
        self.submitpanel.Button.setEnabled(False)
        if self.param['ui'] == 1:
            self.submitpanel.Button.clicked.connect(lambda: self.submit(self.param['div']))
        elif self.param['ui'] == 2:
            self.submitpanel.Button.clicked.connect(lambda: self.submit2(self.param['div']))
        self.vLayout.addWidget(self.submitpanel)
        
        self.ScrollArea = NeuScrollArea(param)
        self.vLayout.addWidget(self.ScrollArea)
        self.setLayout(self.vLayout)
        
        self.ScrollArea.setui()
        # self.ScrollArea.loadui(param["ui"])
        self.show()

    def openInputFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Input File', '.', 'Text File (*.txt)')
        self.filepanel.Label.setText(file_name)
        self.input_file = file_name
        self.ScrollArea.loadui(self.param["ui"], file_name)
    
    def openOutputFile(self):
        file_name, _ = QFileDialog.getSaveFileName(self, 'Open Output File', '.', 'Text File (*.txt)')
        self.outputfilepanel.Label.setText(file_name)
        self.output_file = file_name
        self.submitpanel.Button.setEnabled(True)

    def submit(self, div=' '):
        # 提交文件，检索所有的word label，然后生成一个表，并存储。
        # 遍历所有的word label， 将word和label分别append进数组
        te = []
        for item in self.ScrollArea.word_label:
            text = item.getValue()
            te.append(text)
        # self.filepanel.Label.setText("Success.")
        # 将数组写进文档
        # file_path = "/home/fred/Documents/dev/corpus_tool/label_file"
        with open(self.output_file, 'w') as f:
            for item in te:
                if item['word']:
                    f.write(f"{item['word']}{div}{item['label']}\n")
        self.submitpanel.Label.setText("Submit success!")
        f.close()

    def submit2(self, div=':'):
        # 提交文件，检索所有的word label，然后生成一个表，并存储。
        # 遍历所有的word label， 将word和label分别append进数组
        te = []
        for item in self.ScrollArea.word_label:
            text = item.getValue()
            te.append(text)
        # self.filepanel.Label.setText("Success.")
        # 将数组写进文档
        # file_path = "/home/fred/Documents/dev/corpus_tool/label_file"
        with open(self.output_file, 'w') as f:
            for item in te:
                if item['word'] and item['label'] == 'Y':
                    f.write(f"{item['word']}{div}{1}\n")
        self.submitpanel.Label.setText("Submit success!")
        f.close()

def article2word():
    p = '/home/fred/Documents/dev/corpus_tool'
    input_file = 'corpus.txt'
    infile = os.path.join(p, input_file)
    outfile = os.path.join(p, 'corpus-2.txt')
    with open(infile, 'r') as f:
        with open(outfile, 'w') as g:
            while line := f.readline():
                for i in range(len(line)):
                    if line[i] != ' ' or line[i] != '\n':
                        g.write(f"{line[i]}\n")

if __name__ == '__main__':
    if sys.argv[1] == 'img':
        app = QApplication(sys.argv)
        p = 'Screenshot from 2021-12-22 13-50-22.png'
        demo = ImageWidget()
        demo.setImage(p)
        demo.show()
        sys.exit(app.exec_())
    elif sys.argv[1] == 'scroll':
        d = {"Text": "1", "Label": 0}
        app = QApplication(sys.argv)    
        demo = NeuScrollArea(ner_config)
        demo.setui()
        demo.loadui()
        demo.show()
        sys.exit(app.exec_())        
    elif sys.argv[1] == 'corpus':
        app = QApplication(sys.argv)    
        demo = Corpus_tool(ner_config)
        sys.exit(app.exec_())
    elif sys.argv[1] == 'test':
        app = QApplication(sys.argv)    
        demo = Corpus_tool(wordiv_config)
        sys.exit(app.exec_())
    elif sys.argv[1] == 'cov':
        article2word()