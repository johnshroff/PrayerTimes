from APIs import Aladhan
from Models import Model, LocationModel, TimesModel

location = LocationModel()
data = Aladhan.GetTimes(location.GetValue('lat'), location.GetValue('lon'))

times = TimesModel()
times.Load(data)
times.Save()
