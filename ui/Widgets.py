from env import ROOT_APPLICATION_PATH
import os, sys, subprocess, datetime, math
sys.path.append('..')
from PyQt4 import QtGui, QtCore
from Models import TimesModel

class CustomIconButton(QtGui.QPushButton):

    ICON_PATH = ROOT_APPLICATION_PATH + '/assets/icons/'
    
    def __init__(self, parent, left, top, icon):
        super(QtGui.QPushButton, self).__init__('', parent)

        path = self.ICON_PATH + icon
        
        self.setGeometry(left, top, 100, 100)
        self.setIcon(QtGui.QIcon(path))
        self.setIconSize(QtCore.QSize(50, 50))

    def SetClick(self, event):
        self.clicked.connect(event)

class CustomForm(QtGui.QWidget):

    OnSave = QtCore.pyqtSignal()
    
    def __init__(self):
        self.Fields = {}
        self.Buttons = {}
        super(QtGui.QWidget, self).__init__()    
        self.Layout = QtGui.QFormLayout()        
        self.CreateFields()
        self.SetFields()
        self.CreateButtons()
        self.setLayout(self.Layout)        
        self.showFullScreen()

    def CreateFields(self):
        pass

    def CreateButtons(self):
        pass

    def SetFields(self):
        for key in self.Fields:
            self.Fields[key].setText(self.Model.GetValue(key))
        
    def AddField(self, key, label):
        self.Fields[key] = CustomTextBox(self, label)
        self.Layout.addRow(label, self.Fields[key])

    def Validation(self):
        self.Save()

    def Save(self):
        for key in self.Fields:
            self.Model.SetValue(key, self.Fields[key].displayText())
        self.Model.Save()
        self.AfterSave()

    def AfterSave(self):
        self.OnSave.emit()
        self.close()       

    def Cancel(self):
        self.close()

class CustomTextBox(QtGui.QLineEdit):    

    def __init__(self, parent = None, label = None):
        self.Label = label
        self.Parent = parent
        super(CustomTextBox, self).__init__(parent)
    
    def mousePressEvent(self, event):        
        super().mousePressEvent(event)
        self.OpenKeyboard()

    def OpenKeyboard(self):
        self.Keyboard = Keyboard(self, self.displayText(), self.Label)

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

    def Refresh(self):
        self.Times.LoadFileData()
        self.UpdateClock()


class Keyboard(QtGui.QWidget):

    KEYS = [
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.']
    ]

    def __init__(self, parent, text, label):
        super(QtGui.QWidget, self).__init__()
        self.Parent = parent
        self.CapsLock = False
        self.Keys = {}
        self.Layout = QtGui.QFormLayout()
        self.Field = QtGui.QLineEdit()
        self.Field.setText(text)
        self.Layout.addRow(label, self.Field)
        self.setLayout(self.Layout)
        self.CreateKeys()
        self.CreateBottomRow()
        self.showFullScreen()

    def CreateKeys(self):
        r = 1
        for row in Keyboard.KEYS:
            c = 1
            for key in row:
                self.Keys[key] = Key(self, 50 * c, 50 * r, key)
                c += 1
            r += 1

    def KeyPressed(self, letter):
        if self.CapsLock:
            self.Field.insert(letter)
        else:
            self.Field.insert(letter.lower())

    def CreateBottomRow(self):
        self.Keys['CAPSLOCK'] = CapsLock(self, 50, 250)
        self.Keys['SPACEBAR'] = SpaceBar(self, 150, 250)
        self.Keys['RETURN'] = Return(self, 400, 250)
        self.Keys['BACKSPACE'] = BackSpace(self, 500, 150)

    def ReturnFunction(self):
        self.Parent.setText(self.Field.displayText())
        self.close()        
        
class Key(QtGui.QPushButton):
    def __init__(self, parent, left, top, letter):
        super(QtGui.QPushButton, self).__init__(letter, parent)
        self.Letter = letter
        self.Parent = parent
        self.setGeometry(left, top, 50, 50)
        self.clicked.connect(self.KeyPressed)

    def KeyPressed(self):
        if self.Parent.CapsLock:
            self.Parent.Field.insert(self.Letter)
        else:
            self.Parent.Field.insert(self.Letter.lower())

class CapsLock(QtGui.QPushButton):
    def __init__(self, parent, left, top):
        super(QtGui.QPushButton, self).__init__('CAPS LOCK', parent)
        self.Parent = parent
        self.setGeometry(left, top, 100, 50)
        self.clicked.connect(self.KeyPressed)

    def KeyPressed(self):
        if self.Parent.CapsLock:
            self.Parent.CapsLock = False
            self.setStyleSheet('QPushButton {color: black;}')
        else:
            self.Parent.CapsLock = True
            self.setStyleSheet('QPushButton {color: red;}')

class SpaceBar(QtGui.QPushButton):
    def __init__(self, parent, left, top):
        super(QtGui.QPushButton, self).__init__(' ', parent)
        self.Parent = parent
        self.setGeometry(left, top, 250, 50)
        self.clicked.connect(self.KeyPressed)

    def KeyPressed(self):
        self.Parent.Field.insert(' ')

class Return(QtGui.QPushButton):
    def __init__(self, parent, left, top):
        super(QtGui.QPushButton, self).__init__('RETURN', parent)
        self.Parent = parent
        self.setGeometry(left, top, 100, 50)
        self.clicked.connect(self.KeyPressed)

    def KeyPressed(self):
        self.Parent.ReturnFunction()

class BackSpace(QtGui.QPushButton):
    ICON_PATH = ROOT_APPLICATION_PATH + '/assets/icons/'
    
    def __init__(self, parent, left, top):
        super(QtGui.QPushButton, self).__init__('', parent)
        path = self.ICON_PATH + 'back.png'
        self.setIcon(QtGui.QIcon(path))
        self.Parent = parent
        self.setGeometry(left, top, 50, 150)
        self.clicked.connect(self.KeyPressed)

    def KeyPressed(self):
        self.Parent.Field.backspace()