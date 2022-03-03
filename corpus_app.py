import sys
from PyQt5.QtWidgets import QApplication
from corpus_tool import Corpus_tool

if __name__ == '__main__':
    app = QApplication(sys.argv)    
    demo = Corpus_tool()
    sys.exit(app.exec_())