from APIs import Aladhan
from Models import Model, LocationModel, TimesModel

location = LocationModel()
data = Aladhan.GetTimes(location.GetValue('lat'), location.GetValue('lng'))

times = TimesModel()
times.Load(data)
times.Save()
