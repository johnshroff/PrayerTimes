import os, sys, subprocess, datetime
from time import gmtime, strftime
sys.path.append('..')
from PyQt4 import QtGui, QtCore
from Models import TimesModel

class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 800, 480)
        self.setWindowTitle('Adhan')
        self.CreateTimer()
        self.CreateImage()        
        self.showFullScreen()

    def CreateImage(self):
        pixmap = QtGui.QPixmap('/home/pi/PrayerTimes/ui/mosque.jpg')
        pixmap.scaled(self.size())
        
        label = QtGui.QLabel(self)
        label.setGeometry(60, 120, pixmap.width(), pixmap.height())
        label.resize(pixmap.width(), pixmap.height())
        label.setPixmap(pixmap)

    def CreateTimer(self):
        self.Label = QtGui.QLabel(self)
        self.Label.setText('Next Adhan:')        
        self.Label.setFont(QtGui.QFont("Times", 24, QtGui.QFont.Bold))
        self.Label.setGeometry(0, 50, 200, 50)
        self.Clock = AdhanCountdownTimer(self, 175, 40)

class AdhanCountdownTimer(QtGui.QLCDNumber):

    def __init__(self, parent, left, top):
        super(QtGui.QLCDNumber, self).__init__(parent)
        self.setDigitCount(8)
        self.setGeometry(left, top, 200, 75)
        self.Times = TimesModel()
        self.UpdateClock()
        self.Timer = QtCore.QTimer(self)
        self.Timer.start(1000)
        self.Timer.timeout.connect(self.UpdateClock)

    def GetNextPrayerTime(self):
        nextPrayer = None
        times = self.Times.GetData()
        for key in times:
            if (self.PrayerDate(times[key]) > self.CurrentDate()):                
                if (nextPrayer is None or self.PrayerDateOrdered(times[key]) < self.PrayerDateOrdered(times[nextPrayer])):
                    nextPrayer = key
        timeLeft = self.PrayerDate(self.Times.GetValue(nextPrayer)) - self.CurrentDate()
        timeLeft = timeLeft - datetime.timedelta(microseconds=timeLeft.microseconds)
        return str(timeLeft)

    def CurrentDate(self):
        return datetime.datetime.now()

    def PrayerDateOrdered(self, time):
        fajr = datetime.datetime.strptime(self.Times.GetValue('Fajr'), '%H:%M')
        fajr = datetime.datetime.combine(self.CurrentDate(), fajr.time())

        prayer = datetime.datetime.strptime(time, '%H:%M')

        if (fajr > prayer):
            prayerDate = datetime.date.today() + datetime.timedelta(days=1)
        else:
            prayerDate = datetime.date.today()

        return datetime.datetime.combine(prayerDate, prayer.time())

    def PrayerDate(self, time):
        fajr = datetime.datetime.strptime(self.Times.GetValue('Fajr'), '%H:%M')
        fajr = datetime.datetime.combine(self.CurrentDate(), fajr.time())           
        
        prayer = datetime.datetime.strptime(time, '%H:%M')
        return datetime.datetime.combine(datetime.datetime.now(), prayer.time())

    def UpdateClock(self):
        self.display(self.GetNextPrayerTime())

    

app = QtGui.QApplication(sys.argv)
GUI = Window()
sys.exit(app.exec_())
