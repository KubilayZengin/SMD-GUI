"""
Kütüphane indirme komutları:
pip install matplotlib
pip install numpy
"""


import matplotlib.pyplot as plt  # grafik çizdirmek için matplotlib kullanıyoruz
import numpy as np  # array işlemleri için numpy kullanıyoruz
import time  # zamanı tutmak için time kütüphanesini kullanıyoruz


# Gerçek zamanlı veri çizici fonksiyon
def plot():
    xdata = []
    ydata = []
    start_time = time.time()

    fig, ax = plt.subplots()
    line, = ax.plot(xdata, ydata)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 100)  # x ve y ekseni sınırlarını ayarlayabilirsiniz

    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time

        xdata.append(elapsed_time)
        ydata.append(elapsed_time ** 2)

        line.set_xdata(xdata)
        line.set_ydata(ydata)

        plt.draw()
        plt.pause(0.01)

        if elapsed_time > 10:
            break

    plt.show()


# Fonksiyonu çağır
plot()
