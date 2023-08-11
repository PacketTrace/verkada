import requests
import os
import time

#Netcat
netcatBaseTCP = 'nc -z -w 3 '
netcatBaseUDP = 'nc -z -u -w 3 '
ntpBase = 'sntp '
#URLs
camerasUrl = 'https://pastebin.com/raw/1aSY0jLj'
acUrl = 'https://pastebin.com/raw/RtHkkwmW'
alarmsUrl = 'https://pastebin.com/raw/AJJqZ2LV'
ntpUrl = 'https://pastebin.com/raw/VH65zZFu'
intercomUrl = 'https://pastebin.com/raw/b0gUybbw'
allUrls = []


print('Gathering FQDN endpoints...')
time.sleep(1)
#Convert text response to a list of domains
allUrls = requests.get(camerasUrl).text.split('\r\n')
acUrl = requests.get(acUrl).text.split('\r\n')
allUrls = allUrls + acUrl
allUrls = allUrls + requests.get(alarmsUrl).text.split('\r\n')
#Test TCP/UDP 443
for fqdns in allUrls:
    netCatTCP = netcatBaseTCP + fqdns + ' 443'
    netCatUDP = netcatBaseUDP + fqdns + ' 443'
    captured = os.popen(netCatTCP).read()
    captured = os.popen(netCatUDP).read()

#Test Intercom
print('')
print('Testing SIP endpoints...')
time.sleep(1)
intercomUrls =requests.get(intercomUrl).text.split('\r\n')
for fqdns in intercomUrls:
    netCatTCP_5061 = netcatBaseTCP + fqdns + ' 5061'
    netCatUDP_5061 = netcatBaseUDP + fqdns + ' 5061'
    netCatTCP_5060 = netcatBaseTCP + fqdns + ' 5060'
    netCatUDP_5060 = netcatBaseUDP + fqdns + ' 5060'
    captured = os.popen(netCatTCP_5061).read()
    captured = os.popen(netCatUDP_5061).read()
    captured = os.popen(netCatTCP_5060).read()
    captured = os.popen(netCatUDP_5060).read()
#Test NTP
print('')
print('Testing NTP...')
ntpUrls = requests.get(ntpUrl).text.split('\r\n')

print(ntpUrls)
for fqdns in ntpUrls:
    print('Testing NTP server: ' +fqdns)
    captured = os.popen(ntpBase + fqdns).read()
    print(captured)
    

time.sleep(1)
