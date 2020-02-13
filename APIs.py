import requests, json, urllib, os, sys, subprocess, time

class Aladhan:
    URL = 'http://api.aladhan.com/timings/1398332113?'

    @staticmethod
    def GetTimes(latitude, longitude, method = '1', timezone = 'UTC'):
        params = { 'latitude' : latitude, 'longitude' : longitude, 'timezonestring' : timezone, 'method' : method }
        url = Aladhan.URL + urllib.parse.urlencode(params)
        req = requests.get(url)
        response = req.json()
        return response['data']['timings']

class GoogleMaps:
    URL = 'https://maps.googleapis.com/maps/api/geocode/json?'

    @staticmethod
    def GetCoordsByAddress(address):
        params = { 'address' : address }
        url = GoogleMaps.URL + urllib.parse.urlencode(params)
        req = requests.get(url)
        response = req.json()

        if (response['status'] == 'ZERO_RESULTS'):
            return False
        else:
            return response['results'][0]['geometry']['location']

class WPA:
    
    def __init__(self, interface):
        self.Interface = interface
        self.GetNetworks()

    def GetNetworks(self):
        self.Networks = []
        results = self.Command(['list_networks']).decode().split('\n')[1:]
        results = [x.split('\t') for x in results if x != '']
        for result in results:
            self.Networks.append({'id': result[0], 'ssid': result[1], 'status': result[3]})
        return self.Networks

    def GetNetworkBySSID(self, ssid):
        return [x for x in self.Networks if x['ssid'] == ssid]

    def GetNetworkByID(self, networkId):
        return [x for x in self.Networks if x['id'] == networkId]

    def GetCurrentNetwork(self):
        return [x for x in self.Networks if x['status'] == '[CURRENT]']

    def DropNetworkBySSID(self, ssid):
        for x in self.GetNetworkBySSID(ssid):
            self.Command(['remove_network', x['id']])
        self.GetNetworks()

    def DropNetworkByID(self, networkId):
        for x in self.GetNetworkByID(networkId):
            self.Command(['remove_network', networkId])
        self.GetNetworks()

    def ConnectBySSID(self, ssid):
        for x in self.GetNetworkBySSID(ssid):
            if self.Result(self.Command(['enable_network', x['id']])):
                break
        self.GetNetworks()
        return self.GetStatus()

    def Disconnect(self):
        network = self.GetCurrentNetwork()
        if network:
            self.Command(['disable_network', network[0]['id']])
        self.GetNetworks()
        return self.GetStatus()

    def ConnectByID(self, networkId):
        self.Result(self.Command(['enable_network', networkId]))
        self.GetNetworks()
        time.sleep(1)
        return self.GetStatus()

    def AddNetwork(self, ssid, psk):
        networkId = self.Command(['add_network']).decode().split('\n')[-2]
        ssid = '"' + ssid + '"'
        psk = '"' + psk + '"'
        self.Command(['set_network', networkId, 'ssid', ssid])
        self.GetNetworks()
        return self.Result(self.Command(['set_network', networkId, 'psk', psk]))

    def SetPSKByID(self, networkId, psk):
        return self.Result(self.Command(['set_network', networkId, 'psk', psk]))

    def Scan(self):
        self.Command(['scan'])
        results = [x.split('\t') for x in self.Command(['scan_results']).decode().split('\n')][1:]
        return [x[-1] for x in results if x[-1] is not '']

    def Command(self, args):
        command = ['wpa_cli', '-i', self.Interface] + args
        return subprocess.check_output(command)

    def Result(self, output):
        if output.decode().translate({ord('\n'): None}) == 'OK':
            return True
        else:
            return False

    def GetStatus(self):
        return [x.split('=') for x in self.Command(['status']).decode().split('\n') if 'wpa_state' in x][0][1]        
        
