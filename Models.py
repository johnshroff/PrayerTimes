from ui.env import ROOT_APPLICATION_PATH
import json
class Model():
    DATA_DIR = ROOT_APPLICATION_PATH + '/data/'
    FILE = 'abstract'
    Data = None

    def __init__(self):
        self.LoadFileData()

    def Save(self):
        with open(self.FilePath(), 'w') as file:
            json.dump(self.Data, file)
            file.close()
            
    def FilePath(self):
        return self.DATA_DIR + self.FILE

    def SetValue(self, key, value):
        self.Data[key] = value

    def GetValue(self, key):
        return self.Data[key]

    def Load(self, data):
        self.Data = data

    def GetData(self):
        return self.Data

    def LoadFileData(self):
        with open(self.FilePath()) as fileData:
            self.Data = json.load(fileData)
            fileData.close()
    
class TimesModel(Model):
    FILE = 'times.data'

    def GetTimeRange(self, key):
        hours, minutes = map(int, self.Data[key].split(':'))
        
        if minutes - 2 < 0:
            startHours = hours - 1
            startMinutes = 60 + minutes - 2
        else:
            startHours = hours
            startMinutes = minutes - 1

        if minutes + 2 > 59:
            endHours = hours + 1
            endMinutes = minutes + 2 - 60
        else:
            endHours = hours
            endMinutes = minutes + 2

        return {'sh' : startHours, 'sm' : startMinutes, 'eh' : endHours, 'em' : endMinutes}    

class LocationModel(Model):
    FILE = 'location.data'

class CityStateModel(Model):
    FILE = 'citystate.data'

class LockModel(Model):
    FILE = 'lock.data'

class MethodModel(Model):
    FILE = 'method.data'

    METHODS = {
        '0': 'Shia Ithna-Ashari',
        '1': 'University of Islamic Sciences',
        '2': 'Islamic Society of North America',
        '3': 'Muslim World League',
        '4': 'Umm al-Qura, Makkah',
        '5': 'Egyptian General Authority of Survey',
        '7': 'Institute of Geophysics, University of Tehran'
    }

    @classmethod
    def GetMethodByValue(cls, value):
        return list(cls.METHODS.keys())[list(cls.METHODS.values()).index(value)]
    
        
        
