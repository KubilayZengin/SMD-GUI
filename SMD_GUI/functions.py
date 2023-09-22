import sys
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
from PyQt5.QtWidgets import QDesktopWidget, QMessageBox, QSizeGrip
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QMovie, QMouseEvent
from SMD import Ui_MainWindow
from logo import Ui_SplashScreen
import typing
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QTimer, Qt, QThread
from PyQt5.QtGui import QIcon, QPixmap
from serial.tools.list_ports_linux import comports
import subprocess
from smd.red import *

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
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
        #self.sizegrip = QSizeGrip(self.ui.resize_label)
        #self.sizegrip.setStyleSheet("width: 10px; height: 10px; margin 0px; padding: 0px;")

        # Başlık çubuğu sürükleme için kullanılan değişkenler
        self.dragging = False
        self.oldPos = self.pos()

        # Pencere boyutlandırma için kullanılan değişkenler
        self.resizing = False
        self.resize_start_pos = None
        self.resize_start_geometry = None
        self.ui.widget_4.hide()
        self.ui.menubar_frame.hide()
        self.current_id = 0
        #self.ui.actionSave_as.triggered.connect(self.save_as)
        #self.ui.actionOpen.triggered.connect(self.open_file)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_comboBox)
        self.timer.start(500)
        self.pos_timer= QTimer(self)
        self.pos_timer.timeout.connect(lambda: self.get_position(int(self.current_id)))
        
        self.vel_timer = QTimer(self)
        self.vel_timer.timeout.connect(lambda: self.get_position(int(self.current_id)))
        self.tor_timer = QTimer(self)
        self.tor_timer.timeout.connect(lambda: self.get_torque(int(self.current_id)))
        self.ui.ports_comboBox.activated.connect(self.activatedComboBox)
        self.ui.comboBox.activated.connect(self.activatedBaudrate)
        self.ui.lineEdit_4.returnPressed.connect(self.update_id)
        #self.ui.comboBox_3.activated.connect(lambda : self.configuration_operation(int(self.current_id)))
        self.ui.pushButton_3.clicked.connect(lambda : self.torque_enable(int(self.current_id)))
        self.ui.spinBox_3.editingFinished.connect(lambda: self.set_position(int(self.current_id)))
        self.ui.spinBox_6.editingFinished.connect(lambda: self.set_velocity(int(self.current_id)))
        self.ui.spinBox_9.editingFinished.connect(lambda: self.set_torque(int(self.current_id)))
        self.ui.spinBox.editingFinished.connect(lambda : self.cpr(int(self.current_id)))
        self.ui.spinBox_2.editingFinished.connect(lambda: self.rpm(int(self.current_id)))
        self.ui.pushButton.clicked.connect(lambda: self.autotuner(int(self.current_id)))
        self.ui.doubleSpinBox.editingFinished.connect(lambda: self.p_position(int(self.current_id)))
        self.ui.doubleSpinBox_2.editingFinished.connect(lambda: self.i_position(int(self.current_id)))
        self.ui.doubleSpinBox_3.editingFinished.connect(lambda: self.d_position(int(self.current_id)))
        self.ui.doubleSpinBox_5.editingFinished.connect(lambda: self.p_velocity(int(self.current_id)))
        self.ui.doubleSpinBox_4.editingFinished.connect(lambda: self.i_velocity(int(self.current_id)))
        self.ui.doubleSpinBox_6.editingFinished.connect(lambda: self.d_velocity(int(self.current_id)))
        self.ui.doubleSpinBox_8.editingFinished.connect(lambda: self.p_torque(int(self.current_id)))
        self.ui.doubleSpinBox_7.editingFinished.connect(lambda: self.i_torque(int(self.current_id)))
        self.ui.doubleSpinBox_9.editingFinished.connect(lambda: self.d_torque(int(self.current_id)))
        self.ui.doubleSpinBox_10.editingFinished.connect(lambda: self.pwm(int(self.current_id)))
        self.ui.doubleSpinBox_10.editingFinished.connect(self.update_slider)
        self.ui.treeWidget.itemClicked.connect(self.motor_page)
        self.ui.pwm_slider.valueChanged.connect(self.update_dutyCycle)
        self.ui.pwm_slider.valueChanged.connect(lambda: self.pwm(int(self.current_id)))
        self.checkBoxes = [self.ui.checkBox, self.ui.checkBox_2, self.ui.checkBox_3, 
                           self.ui.checkBox_4, self.ui.checkBox_5, self.ui.checkBox_6]
        self.ui.scan_button.clicked.connect(self.scan_smd)
        self.ui.homeButton.clicked.connect(self.turn_scan_page)
        self.ui.treeWidget.itemClicked.connect(self.control_page)
        self.ui.tabWidget.tabBarClicked.connect(self.set_operation)
        #self.ui.comboBox_2.currentIndexChanged.connect(self.get_id)
        self.file_path = None
        self.torque_enabled = False
        self.smd_id = []
        self.sensor_id = []
        self.childeren = []
        self.operation_modes = {"PWM": 0, "Position":1, "Velocity": 2, "Torque": 3}

    def save_as(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save As", "", "Metin Dosyaları (*.txt);;Tüm Dosyalar (*)")

        if file_name:
            try:
                with open(file_name, "w") as dosya:
                    dosya.write(self.ui.textEdit.toPlainText())
                    self.file_path = file_name
            except Exception as e:
                print("Bir hata oluştu:", str(e))

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open", "", "Metin Dosyaları (*.txt);;Tüm Dosyalar (*)")
        if file_name:
            try:
                with open(file_name, "r") as dosya:
                    veri = dosya.read()
                    self.ui.textEdit.setPlainText(veri)
            except Exception as e:
                print("Bir hata oluştu:", str(e))
    
    def update_comboBox(self):
        for port in comports():
            self.port = port.device
            if self.port is not None:
                self.ui.ports_comboBox.addItem(self.port)
                self.timer.stop()
            else:
                self.ui.ports_comboBox.removeItem(self.port)
    def turn_scan_page(self):
        self.ui.treeWidget.clear()
        self.smd_id.clear()
        self.ui.stackedWidget.setCurrentIndex(0)
    def activatedComboBox(self):
        self.selected_port = self.ui.ports_comboBox.currentText()
                
    def scan_smd(self):
        self.ui.scan_button.setStyleSheet("border-image: url(:/newPrefix/ScanClicked.png);")
        self.selected_baudrate = [checkBox.text() for checkBox in self.checkBoxes if checkBox.isChecked ()]
        print(self.selected_baudrate)
        self.master = Master(portname=self.selected_port)
        for baudrate in self.selected_baudrate:
            self.master.update_master_baudrate(int(baudrate))
            self.master.scan()
            self.smd_id = self.smd_id + self.master.attached()
            print(self.smd_id)
        if not self.smd_id:
            self.ui.widget_4.show()
            self.ui.label_2.setText("smd bulunamadı")
        else:
            try:
                self.ui.widget_4.show()
                self.ui.menubar_frame.show()
                self.sensor_scan()
                self.ui.label_2.setText("scanned")
            except:
                self.ui.label_2.setText("sensor bulunamadı")
                self.ui.menubar_frame.show()
            
    def sensor_scan(self):
        sensors = {"Buzzer Sensor": [Index.Buzzer_1, Index.Buzzer_2, Index.Buzzer_3, Index.Buzzer_4, Index.Buzzer_5], "Button": [Index.Button_1, Index.Button_2, Index.Button_3, Index.Button_4, Index.Button_5],"Light": [Index.Light_1, Index.Light_2, Index.Light_3, Index.Light_4, Index.Light_5], "Joystick": [Index.Joystick_1, Index.Joystick_2, Index.Joystick_3, Index.Joystick_4, Index.Joystick_5], "Distance": [Index.Distance_1, Index.Distance_2, Index.Distance_3, Index.Distance_4, Index.Distance_5], "QTR": [Index.QTR_1, Index.QTR_2, Index.QTR_3, Index.QTR_4, Index.QTR_5], "Potentiometer": [Index.Pot_1, Index.Pot_2, Index.Pot_3, Index.Pot_4, Index.Pot_5], "IMU": [Index.IMU_1, Index.IMU_2, Index.IMU_3, Index.IMU_4, Index.IMU_5]}
        if self.smd_id:
            for i, id in enumerate(self.smd_id):
                topLevelItem = QTreeWidgetItem(self.ui.treeWidget)
                childItem = QTreeWidgetItem(topLevelItem, ["Motor Page"])
                self.ui.treeWidget.topLevelItem(i).setText(0,f"SMD ID: {id}")
                self.sensor_id = self.master.scan_sensors(id)
                addonsItem =QTreeWidgetItem(topLevelItem, ["Add ons:"])
                print(self.sensor_id)
                if self.sensor_id:
                    for _id in self.sensor_id:
                        for j in range(5):
                            if _id == sensors["Buzzer Sensor"][j]:
                                buzzeritem = QTreeWidgetItem(addonsItem, ["Buzzer Sensor"])
                            elif _id == sensors["Button"][j]:
                                buttonitem = QTreeWidgetItem(addonsItem, ["Button"])
                            elif _id == sensors["Light"][j]:
                                lightitem = QTreeWidgetItem(addonsItem, ["Light"])
                            elif _id == sensors["Joystick"][j]:
                                joystickitem = QTreeWidgetItem(addonsItem, ["Joystick"])
                            elif _id == sensors["Distance"][j]:
                                distanceitem = QTreeWidgetItem(addonsItem, ["Distance"])
                            elif _id == sensors["QTR"][j]:
                                qtritem = QTreeWidgetItem(addonsItem, ["QTR"])
                            elif _id == sensors["Potentiometer"][j]:
                                potitem = QTreeWidgetItem(addonsItem, ["Potentiometer"])
                            elif _id == sensors["IMU"][j]:
                                imuitem = QTreeWidgetItem(addonsItem, ["IMU"])

    def control_clicked(self, item):
        top_level_item_count = self.ui.treeWidget.topLevelItemCount()
        for i in range(top_level_item_count):
            self.top_level_item = self.ui.treeWidget.topLevelItem(i)
            if self.top_level_item is not None and self.top_level_item.isSelected():
                current_index = self.ui.stackedWidget.currentIndex()
                if current_index == 0 or current_index == 2:
                    self.ui.stackedWidget.setCurrentIndex(1)
            elif self.top_level_item is not None and self.top_level_item.child(0).isSelected():
                current_index = self.ui.stackedWidget.currentIndex()
                if current_index == 1 or current_index == 0: 
                    self.ui.stackedWidget.setCurrentIndex(2)
            elif self.top_level_item.child(1).child(0).isSelected():
                current_index = self.ui.stackedWidget.currentIndex()
                if current_index == 1 or current_index == 0 or current_index == 2:
                    self.ui.stackedWidget.setCurrentIndex(3)
                    
    def control_page(self, item):
        if item.text(0) == "Motor Page":
            current_index = self.ui.stackedWidget.currentIndex()
            self.ui.stackedWidget.setCurrentIndex(2)
            self.ui.spinBox.clear()
            self.ui.spinBox_2.clear()
            self.ui.spinBox_3.clear()
            self.ui.spinBox_4.clear()
            self.ui.spinBox_6.clear()
            self.ui.spinBox_7.clear()
            self.ui.spinBox_9.clear()
            self.ui.doubleSpinBox.clear()
            self.ui.doubleSpinBox_2.clear()
            self.ui.doubleSpinBox_3.clear()
            self.ui.doubleSpinBox_4.clear()
            self.ui.doubleSpinBox_5.clear()
            self.ui.doubleSpinBox_6.clear()
            self.ui.doubleSpinBox_7.clear()
            self.ui.doubleSpinBox_8.clear()
            self.ui.doubleSpinBox_9.clear()
            self.ui.doubleSpinBox_10.clear()
        else:
            current_index = self.ui.stackedWidget.currentIndex()
            self.ui.stackedWidget.setCurrentIndex(1)
        
    def update_id(self):
        text = self.ui.lineEdit_4.text()
        selected_item = self.ui.treeWidget.currentItem()
        current_id = selected_item.text(0)[-1]
        new_id = text
        if selected_item is not None:
            selected_item.setText(0, f"SMD ID: {text}")
            self.master.update_driver_id(int(current_id), int(new_id))
            self.ui.lineEdit_4.clear()
    def motor_page(self, item, column):
        parent_item = item.parent()
        if parent_item is not None:
            self.current_id = parent_item.text(0)[-1]
            self.master.attach(Red(int(self.current_id)))
    def activatedBaudrate(self):
        self.driverBaudrate = self.ui.comboBox.currentText()                                 
        self.master.update_driver_baudrate(int(self.new_id), int(self.driverBaudrate))
        
    def configuration_operation(self, id):
        self.operation_mode = self.ui.comboBox_3.currentText()
        print(self.operation_mode)
        for mode in self.operation_modes:
            if self.operation_mode == mode:
                print(self.master.set_operation_mode(id, self.operation_modes[mode]))
    def torque_enable(self, id):
        self.torque_enabled = not self.torque_enabled
        if self.torque_enabled:
            self.master.enable_torque(id, True)
        else:
            self.master.enable_torque(id, False)
    def cpr(self, id):
        cpr = self.ui.spinBox.value()
        self.master.set_shaft_cpr(id, cpr)

    def rpm(self, id):
        rpm = self.ui.spinBox_2.value()
        self.master.set_shaft_rpm(id, rpm)
    
    def set_operation(self, index):
        id = int(self.current_id)
        if index == 1:
            self.master.set_operation_mode(id, 1)
        elif index == 2:
            self.master.set_operation_mode(id, 2)
        elif index == 3:
            self.master.set_operation_mode(id, 3)
        elif index == 4:
            self.master.set_operation_mode(id, 0)
        
    def set_pos(self, id):
        self.master.set_operation_mode(id, 1)
    def set_vel(self, id):
        self.master.set_operation_mode(id, 2)
    def set_tor(self, id):
        self.master.set_operation_mode(id, 3)
    def set_pwm(self, id):
        self.master.set_operation_mode(id, 0)
    def set_position(self, id):
        set_point_position = self.ui.spinBox_3.value()
        print(set_point_position)
        self.master.set_position(id, int(set_point_position))
        self.pos_timer.start(500)
        print(id)
    def set_velocity(self, id):
        set_point_velocity = self.ui.spinBox_6.value()
        self.master.set_velocity(id, set_point_velocity)
        self.vel_timer.start(500)
    def set_torque(self, id):
        set_point_torque = self.ui.spinBox_9.value()
        self.master.set_torque(id, set_point_torque)
        self.tor_timer.start(500)

    def get_position(self, id):
        self.ui.lineEdit.setText(str(self.master.get_position(id)))
        
    def get_velocity(self, id):
        self.ui.lineEdit_2.setText(str(self.master.get_velocity(id)))
        
    def get_torque(self, id):
        self.ui.lineEdit_3.setText(str(self.master.get_torque(id)))
        
    def autotuner(self, id):
        self.master.pid_tuner(id)
        pid_p = []
        pid_p = self.master.get_control_parameters_position(id)
        self.ui.doubleSpinBox.setValue(pid_p[0])
        self.ui.doubleSpinBox_2.setValue(pid_p[1])
        self.ui.doubleSpinBox_3.setValue(pid_p[2])
        pid_v = []
        pid_v = self.master.get_control_parameters_velocity(id)
        self.ui.doubleSpinBox_5.setValue(pid_v[0])
        self.ui.doubleSpinBox_4.setValue(pid_v[1])
        self.ui.doubleSpinBox_6.setValue(pid_v[2])
        pid_t = []
        pid_t = self.master.get_control_parameters_torque(id)
        self.ui.doubleSpinBox_8.setValue(pid_t[0])
        self.ui.doubleSpinBox_7.setValue(pid_t[1])
        self.ui.doubleSpinBox_9.setValue(pid_t[2])
        
    def p_position(self,id):
        p = self.ui.doubleSpinBox.value()
        self.master.set_control_parameters_position(id, p)
    def i_position(self, id):
        i = self.ui.doubleSpinBox_2.value()
        self.master.set_control_parameters_position(id, i)
    def d_position(self, id):
        d = self.ui.doubleSpinBox_3.value()
        self.master.set_control_parameters_position(id, d)
        
    def p_velocity(self, id):
        p = self.ui.doubleSpinBox_5.value()
        self.master.set_control_parameters_velocity(id, p)
    def i_velocity(self, id):
        i = self.ui.doubleSpinBox_4.value()
        self.master.set_control_parameters_velocity(id, i)
    def d_velocity(self, id):
        d = self.ui.doubleSpinBox_6.value()
        self.master.set_control_parameters_velocity(id, d)
        
    def p_torque(self, id):
        p = self.ui.doubleSpinBox_8.value()
        self.master.set_control_parameters_torque(id, p)
    def i_torque(self, id):
        i = self.ui.doubleSpinBox_7.value()
        self.master.set_control_parameters_torque(id, i)
    def d_torque(self, id):
        d = self.ui.doubleSpinBox_9.value()
        self.master.set_control_parameters_torque(id, d)
        
    def pwm(self, id):
        duty_cycle = self.ui.doubleSpinBox_10.value()
        self.master.set_duty_cycle(id, duty_cycle)
        
    def update_slider(self):
        value = self.ui.doubleSpinBox_10.value()
        self.ui.pwm_slider.setValue(value* 10)
    def update_dutyCycle(self, value):
        self.ui.doubleSpinBox_10.setValue(value/10)
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


class SplashScreen(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
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
