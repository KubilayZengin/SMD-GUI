import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QMovie
from images_rc import *
class GifUygulamasi(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # QLabel oluştur
        label = QLabel(self)
        
        # QLabel boyutunu ayarla
        label.setGeometry(50, 50, 200, 200)

        # QMovie oluştur ve yolu belirt
        movie = QMovie("/home/bobamosfett/Documents/pythonWorkspace/SMD-GUI/images/ezgif.com-gif-maker (8).gif")
        
        # QMovie'ı QLabel'a ekle
        label.setMovie(movie)
        
        # Animasyonu başlat
        movie.start()

        self.setGeometry(100, 100, 300, 300)
        self.setWindowTitle('GIF Örneği')
        self.show()

def main():
    app = QApplication(sys.argv)
    ex = GifUygulamasi()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()