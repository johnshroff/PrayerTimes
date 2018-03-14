from datetime import datetime, time
from Models import Model, TimesModel, LockModel
import pygame
import sys

lock = LockModel()
if not lock.GetValue('lock'):
    now = datetime.now().time()
    times = TimesModel()
    for key in times.GetData():
        ranges = times.GetTimeRange(key)
        if now >= time(ranges['sh'], ranges['sm']) and now <= time(ranges['eh'], ranges['em']):
            
            lock.SetValue('lock', True)
            lock.Save()
            
            pygame.init()
            pygame.mixer.init()
            pygame.mixer.music.load('/home/pi/PrayerTimes/Abdul-Basit.mp3')
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy(): 
                pygame.time.Clock().tick(10)
            
            lock.SetValue('lock', False)
            lock.Save()
            sys.exit()
