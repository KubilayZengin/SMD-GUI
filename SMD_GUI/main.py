import sys
import serial.tools.list_ports

from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
from PyQt5.QtWidgets import QDesktopWidget, QMessageBox, QSizeGrip
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QMovie, QMouseEvent

# Import Main Window UI
from SMD import Ui_MainWindow
from logo import Ui_SplashScreen

# Globals: Programın farklı kısımlarında kullanılacak global değişkenler

# Animasyon ilerlemesi için sayaç
counter = 0
# Ekran büyük mü küçük mü anlamamıza yardımcı olacak değişken
window_size = 0


# Ana pencere
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # self.ui.scan_button.setEnabled(False)
        # Butonun ilk başta inaktif olma kısmı baud rate ve port seçiminden sonra aktifleşecek

        # QMovie ile GIF'i yükleme
        self.movie = QMovie("images/gif.gif")
        self.ui.gif_label.setMovie(self.movie)
        self.ui.scan_button.enterEvent = self.start_gif
        self.ui.scan_ports_button.clicked.connect(self.find_ports)

        # Sağ üstteki butonlara fonksiyon ataması
        self.ui.minimizeButton.clicked.connect(lambda: self.showMinimized())
        self.ui.restoreButton.clicked.connect(lambda: self.restore_or_maximize_window())
        self.ui.closeButton.clicked.connect(lambda: self.close())

        # Tree büyüme küçülme animasyon ataması
        self.ui.open_tree_Button.clicked.connect(self.slideTreeMenu)

        # Arayüz büyütme küçültme kısmı
        self.sizegrip = QSizeGrip(self.ui.resize_label)
        self.sizegrip.setStyleSheet("width: 10px; height: 10px; margin 0px; padding: 0px;")

        # Başlık çubuğu sürükleme için kullanılan değişkenler
        self.dragging = False
        self.oldPos = self.pos()

        # Pencere boyutlandırma için kullanılan değişkenler
        self.resizing = False
        self.resize_start_pos = None
        self.resize_start_geometry = None

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.dragging = True
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.dragging = False
            self.resizing = False

    def mouseMoveEvent(self, event):
        if self.dragging and event.pos().y() < self.ui.upper_frame.height():
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

        if self.resizing:
            delta = event.globalPos() - self.resize_start_pos
            new_width = self.resize_start_geometry.width() + delta.x()
            new_height = self.resize_start_geometry.height() + delta.y()
            self.setGeometry(self.resize_start_geometry.x(), self.resize_start_geometry.y(), new_width, new_height)

    def isResizingArea(self, pos):
        # Köşelerdeki belli bir alanı boyutlandırma alanı olarak tanımlayabilirsiniz
        resizing_area = 10  # Köşelerdeki 10 piksel alanı boyutlandırma alanı olarak kabul edin
        rect = self.rect()
        return (
            (pos.x() > rect.width() - resizing_area) and
            (pos.y() > rect.height() - resizing_area)
        )

    def slideTreeMenu(self):
        width = self.ui.menubar_frame.width()

        if width == 150:
            newWidth = 300
        else:
            newWidth = 150

        self.animation = QtCore.QPropertyAnimation(self.ui.menubar_frame, b"minimumWidth")
        self.animation.setDuration(250)
        self.animation.setStartValue(width)
        self.animation.setEndValue(newWidth)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()

    def find_ports(self):
        # Kullanılabilir COM portlarını bul
        com_list = serial.tools.list_ports.comports()
        available_coms = []
        if len(com_list) == 0:
            available_coms.append("None")
        else:
            for element in com_list:
                available_coms.append(element.device)
        self.ui.ports_comboBox.addItems(available_coms)

    def start_gif(self, event):
        self.movie.start()

    def restore_or_maximize_window(self):
        global window_size  # Default değer 0
        win_status = window_size

        if win_status == 0:
            # Eğer ekran büyük değilse
            window_size = 1  # Ekranın büyütüldüğünü göster
            self.showMaximized()
        else:
            # Eğer ekran büyükse
            window_size = 0  # Ekranın küçültüldüğünü göster
            self.showNormal()


class SplashScreen(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)

        # Başlık çubuğunu kaldır
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Qtimer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        self.timer.start(25)  # Timer'ı başlat

        self.center_to_screen()
        self.ui.background.setVisible(False)

        # Animasyonları başlat
        self.logo_animation()
        self.ui.triangle2_animation_triggered = False

        # Ses efekti
        self.sound_effect = QtMultimedia.QSoundEffect()
        self.sound_effect.setSource(QtCore.QUrl.fromLocalFile("other-files/sound.wav"))
        self.start_animation()

    # Logo animasyonunu oluştur
    def logo_animation(self):
        opacity_effect = QtWidgets.QGraphicsOpacityEffect(self.ui.triangle1)
        self.ui.triangle1.setGraphicsEffect(opacity_effect)

        self.logo_opacity_animation = QtCore.QPropertyAnimation(
            opacity_effect, b'opacity', duration=880, startValue=0, endValue=1)
        self.logo_opacity_animation.setEasingCurve(QtCore.QEasingCurve.InOutCubic)

        opacity_effect2 = QtWidgets.QGraphicsOpacityEffect(self.ui.triangle2)
        self.ui.triangle2.setGraphicsEffect(opacity_effect2)

        self.logo_opacity_animation2 = QtCore.QPropertyAnimation(
            opacity_effect2, b'opacity', duration=880, startValue=0, endValue=1)
        self.logo_opacity_animation2.setEasingCurve(QtCore.QEasingCurve.InOutCubic)

        opacity_effect3 = QtWidgets.QGraphicsOpacityEffect(self.ui.triangle3)
        self.ui.triangle3.setGraphicsEffect(opacity_effect3)

        self.logo_opacity_animation3 = QtCore.QPropertyAnimation(
            opacity_effect3, b'opacity', duration=880, startValue=0, endValue=1)
        self.logo_opacity_animation3.setEasingCurve(QtCore.QEasingCurve.InOutCubic)

        opacity_effect4 = QtWidgets.QGraphicsOpacityEffect(self.ui.background)
        self.ui.background.setGraphicsEffect(opacity_effect4)

        self.logo_opacity_animation4 = QtCore.QPropertyAnimation(
            opacity_effect4, b'opacity', duration=1500, startValue=0, endValue=1)
        self.logo_opacity_animation4.setEasingCurve(QtCore.QEasingCurve.InOutCubic)

        # Animasyonları başlat

    def start_animation(self):
        self.sound_effect.play()
        self.anim_group = QtCore.QSequentialAnimationGroup()
        self.anim_group.addAnimation(self.logo_opacity_animation)
        self.anim_group.addAnimation(self.logo_opacity_animation2)
        self.anim_group.addAnimation(self.logo_opacity_animation3)

        self.anim_group.finished.connect(self.animation_finished)  # Animasyon tamamlandığında
        self.anim_group.start()

    def animation_finished(self):
        # Animasyon tamamlandığında background görünür yap
        self.ui.background.setVisible(True)
        self.ui.anim_group2 = QtCore.QSequentialAnimationGroup()
        self.ui.anim_group2.addAnimation(self.logo_opacity_animation4)
        self.ui.anim_group2.start()

    def center_to_screen(self):
        frame_geometry = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())  # Pencereyi ekranda merkeze taşı

    def progress(self):
        global counter
        # print(counter)
        if counter >= 100:  # İlerleme 100'e ulaştığında
            self.timer.stop()  # Zamanlayıcıyı durdur
            self.main = MainWindow()  # Ana pencereyi oluştur
            self.main.show()  # Ana pencereyi göster
            self.close()  # Splash penceresini kapat
        counter += 0.5  # Sayaç değerini artır (arttırılabilir ya da azaltılabilir)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SplashScreen()
    window.show()
    sys.exit(app.exec_())
