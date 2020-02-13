import os, sys, subprocess
sys.path.append('/home/pi/PrayerTimes')
from Models import Model, CityStateModel, TimesModel, MethodModel
from APIs import Aladhan, GoogleMaps, WPA
from PyQt4 import QtGui, QtCore
from Widgets import CustomIconButton, CustomForm, AdhanCountdownTimer

class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 800, 480)
        self.setWindowTitle('Adhan')
        self.CreateTimer()
        self.CreateImage()
        self.CreateButtons()
        self.showFullScreen()

    def CreateTimer(self):
        self.Label = QtGui.QLabel(self)
        self.Label.setText('Next Adhan:')        
        self.Label.setFont(QtGui.QFont("Times", 24, QtGui.QFont.Bold))
        self.Label.setGeometry(300, 50, 200, 190)
        self.Clock = AdhanCountdownTimer(self, 475, 110)

    def CreateImage(self):
        pixmap = QtGui.QPixmap('/home/pi/PrayerTimes/ui/mosque.jpg')
        pixmap.scaled(self.size())
        
        label = QtGui.QLabel(self)
        label.setGeometry(60, 120, pixmap.width(), pixmap.height())
        label.resize(pixmap.width(), pixmap.height())
        label.setPixmap(pixmap)

    def CreateButtons(self):
        self.btnLocation = CustomIconButton(self, 270, 210, 'map-location.png')
        self.btnLocation.SetClick(self.ChangeLocation)

        self.btnWifi = CustomIconButton(self, 380, 210, 'wifi.png')
        self.btnWifi.SetClick(self.ChangeWifi)

        self.btnSettings = CustomIconButton(self, 490, 210, 'settings-6.png')
        self.btnSettings.SetClick(self.ChangeSettings)
        
    def ChangeLocation(self):
        self.LocationWindow = CityStateForm()
        self.LocationWindow.OnSave.connect(self.Clock.Refresh)

    def ChangeWifi(self):
        self.WifiWindow = WiFiForm()

    def ChangeSettings(self):
        self.SettingsWindow = SettingsForm()
        self.SettingsWindow.OnSave.connect(self.Clock.Refresh)        
    
    
class CityStateForm(CustomForm):
    
    def __init__(self):        
        self.Model = CityStateModel()
        CustomForm.__init__(self)
    
    def CreateFields(self):
        self.AddField('city', 'City')
        self.AddField('state', 'State')

    def CreateButtons(self):
        self.Buttons['save'] = CustomIconButton(self, 100, 100, 'save.png')
        self.Buttons['save'].SetClick(self.Validation)
        self.Buttons['cancel'] = CustomIconButton(self, 300, 100, 'close.png')
        self.Buttons['cancel'].SetClick(self.Cancel)

    def Validation(self):
        address = self.Fields['city'].displayText() + ', ' + self.Fields['state'].displayText()
        coords = GoogleMaps.GetCoordsByAddress(address)
        if (coords is False):
            QtGui.QMessageBox.information(self, 'ERROR', 'City and State not found.')
            return
        self.Save(coords)

    def Save(self, coords):
        method = MethodModel()
        newTimes = Aladhan.GetTimes(coords['lat'], coords['lng'], method.GetValue('method'))        
        times = TimesModel()
        times.Load(newTimes)
        times.Save()        
        CustomForm.Save(self)
        

class WiFiForm(CustomForm):
    
    def __init__(self):
        self.WPA = WPA('wlan0')
        CustomForm.__init__(self)

    def CreateFields(self):
        self.CreateList()
        self.AddField('connected', 'Connected Network')
        self.AddField('password', 'Password')

    def CreateButtons(self):
        self.Buttons['connect'] = CustomIconButton(self, 400, 100, 'add-1.png')
        self.Buttons['connect'].SetClick(self.Validation)

        self.Buttons['disconnect'] = CustomIconButton(self, 550, 100, 'forbidden.png')
        self.Buttons['disconnect'].SetClick(self.Disconnect)

        self.Buttons['cancel'] = CustomIconButton(self, 550, 250, 'close.png')
        self.Buttons['cancel'].SetClick(self.Cancel)

        self.Buttons['refresh'] = CustomIconButton(self, 400, 250, 'repeat-1.png')
        self.Buttons['refresh'].SetClick(self.RefreshList)

    def SetFields(self):
        network = self.WPA.GetCurrentNetwork()
        if network and self.WPA.GetStatus() == 'COMPLETED':
            self.Fields['connected'].setText(network[0]['ssid'])
        self.Fields['connected'].setEnabled(False)
        
    def CreateList(self):
        self.List = QtGui.QListWidget(self)
        self.List.setGeometry(40, 100, 350, 250)
        self.List.currentItemChanged.connect(self.SelectSSID)
        for network in self.WPA.Scan():
            self.List.addItem(network)

    def SelectSSID(self, current, previous):
        self.SelectedSSID = current.text()

    def Validation(self):
        if (self.Fields['password'].displayText() is ''):
            QtGui.QMessageBox.information(self, 'ERROR', 'You must enter a password to connect')
            return
        self.Save()

    def Save(self):
        network = self.WPA.GetNetworkBySSID(self.SelectedSSID)
        if not network:
            self.WPA.AddNetwork(self.SelectedSSID, self.Fields['password'].displayText())
        else:
            self.WPA.SetPSKByID(network[0]['id'], self.Fields['password'].displayText())

        response = self.WPA.ConnectByID(self.WPA.GetNetworkBySSID(self.SelectedSSID)[0]['id'])
            
        if self.WPA.ConnectByID(self.WPA.GetNetworkBySSID(self.SelectedSSID)[0]['id']) == 'COMPLETED':
            self.Fields['connected'].setText(self.SelectedSSID)
            self.Fields['password'].setText('')
        else:
            QtGui.QMessageBox.information(self, 'ERROR', 'Failed to connect')        

    def Disconnect(self):
        network = self.WPA.GetCurrentNetwork()
        if network and self.WPA.GetStatus() == 'COMPLETED':
            self.WPA.DropNetworkByID(network[0]['id'])
            self.Fields['connected'].setText('')

    def RefreshList(self):
        self.List.clear()
        for network in self.WPA.Scan():
            self.List.addItem(network)

class SettingsForm(CustomForm):

    def __init__(self):        
        self.Model = MethodModel()
        self.Method = self.Model.GetValue('method')
        CustomForm.__init__(self)

    def CreateFields(self):
        self.Label = QtGui.QLabel(self)
        self.Label.setText('Calculation Method')     
        self.Label.setFont(QtGui.QFont("Times", 16, QtGui.QFont.Bold))
        self.Label.setGeometry(40, 0, 200, 100)
        self.CreateList()        

    def CreateList(self):
        self.List = QtGui.QListWidget(self)
        self.List.setGeometry(40, 60, 350, 250)
        self.List.currentItemChanged.connect(self.SelectMethod)
        for method in MethodModel.METHODS:
            self.List.addItem(MethodModel.METHODS[method])

    def SelectMethod(self, current, previous):
        self.Method = MethodModel.GetMethodByValue(current.text())

    def CreateButtons(self):
        self.Buttons['save'] = CustomIconButton(self, 400, 60, 'save.png')
        self.Buttons['save'].SetClick(self.Validation)
        self.Buttons['cancel'] = CustomIconButton(self, 400, 210, 'close.png')
        self.Buttons['cancel'].SetClick(self.Cancel)

    def Save(self):
        self.Model.SetValue('method', self.Method)
        self.Model.Save()
        self.AfterSave()

    def AfterSave(self):
        cs = CityStateModel()
        address = cs.GetValue('city') + ', ' + cs.GetValue('state')
        coords = GoogleMaps.GetCoordsByAddress(address)
        newTimes = Aladhan.GetTimes(coords['lat'], coords['lng'], self.Method)        
        times = TimesModel()
        times.Load(newTimes)
        times.Save()
        CustomForm.AfterSave(self)


app = QtGui.QApplication(sys.argv)
GUI = Window()
sys.exit(app.exec_())

