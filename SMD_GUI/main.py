

# Globals: Programın farklı kısımlarında kullanılacak global değişkenler

# Animasyon ilerlemesi için sayaç
counter = 0
# Ekran büyük mü küçük mü anlamamıza yardımcı olacak değişken
window_size = 0


# Ana pencere

        # self.ui.scan_button.setEnabled(False)
        # Butonun ilk başta inaktif olma kısmı baud rate ve port seçiminden sonra aktifleşecek

        # QMovie ile GIF'i yükleme
from PyQt5.QtWidgets import QApplication
from functions import MainWindow



app = QApplication([])
pencere = MainWindow()
pencere.show()
app.exec_()

