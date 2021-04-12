###############################################################
# wifi
###############################################################

# wifi is in this module, so that wifi.disconnect() is available. avoid reconnect issues
# connect to multiple networks
# static IP
def wifi_connect(ssid, psk):
    import network
    from time import sleep_ms
    i=0
    ok = True
    sta_if = network.WLAN(network.STA_IF)
    
    sta_if.active(True)
    sta_if.ifconfig(('192.168.1.6', '255.255.255.0','192.168.1.1', '8.8.8.8'))
    sta_if.connect(ssid, psk)

    while not sta_if.isconnected():
      sleep_ms(300)
      i = i + 1
      if i >=10:
        ok=False
        break
         
    if ok == True:   
      print('connected. network config:', sta_if.ifconfig())
      print ('status: ', sta_if.status())
      print('ssid: ', ssid)
      return (sta_if)
    else:
      print('cannot connect to %s' %(ssid))
      return(None)
    

"""
net = [
['ssid', 'passwd'] , \
['ssid', 'passwd'] , \
['est', 'p'] , \
['ouest', 'p']
]
"""

wifi_ok = False

print('import wifi definition')
import mynet

# try to connect to all wifi in sequence
for i in range(len(mynet.net)):

  print("connecting to wifi %s ..." %(mynet.net[i][0]))
  wifi = wifi_connect(mynet.net[i][0], mynet.net[i][1])
  if wifi != None:
    print('wifi connected !!!!')
    print ('rssi: ', wifi.status('rssi'))
    wifi_ok = True
    break

# can access wifi_ok and wifi from this module