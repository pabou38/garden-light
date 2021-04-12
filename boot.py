# This file is executed on every boot (including wake-boot from deepsleep)
################################
# ESP8266
# Wemos D1 
# power via USB, run esptool and reset using on board button
################################

flash_512 = False

print('\n\nESP8266 micropython LED 2.1 boot')
print('512K memory is: %d' %(flash_512))
# will print a size and md5 

import esp
esp.check_fw()
print('\nflash size in Mbytes: ', esp.flash_size()/(1024.0*1024.0))

#esp.osdebug(None)
# to display flash size
#import port_diag


if flash_512 == False:
  import uos
  # do not include for 512k port, no file system
  # free file system
  i= uos.statvfs('/')
  fs = i[1]*i[2]/(1024.0*1024.0)
  free= i[0]*i[4]/(1024.0*1024.0)
  per = (float(free)/float(fs))
  print('file system size %0.1f, free %0.1f, used in percent %0.1f' %(fs, free, per))

import gc
gc.collect()

from micropython import mem_info, const, stack_use
# heap vs stack
#https://www.guru99.com/stack-vs-heap.html

# heap is 37952 bytes. note: stack is fixed 8192 / 1024 = 8Kio
print("gc mem free: %d , alloc %d , total (heap) %d" %(gc.mem_free(), gc.mem_alloc(), gc.mem_free() + gc.mem_alloc()))
gc.collect() # force garbage collection
print("gc mem free: %d , alloc %d , total (heap) %d" %(gc.mem_free(), gc.mem_alloc(), gc.mem_free() + gc.mem_alloc()))

# garbage collection can be executed manually, if alloc fails, or if 25% of 
# currently free heap becomes occupied
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

print("stack used: ", stack_use())
print("mem info: ", mem_info()) # (1) verbose



#uos.dupterm(None, 1) # disable REPL on UART(0)

#import gc
#gc.collect()

  
# do not start REPL, as will be in sleep mode

# start webrepl after wifi. will be on 192.168.1.4:8266 (connect to wemos ssid) 
# and on local IP on home router as well
#WebREPL daemon started on ws://192.168.4.1:8266
#WebREPL daemon started on ws://192.168.1.5:8266
#Started webrepl in normal mode

# does not work on 512K, no file system ?
# need to import once webrepl_setup from a usb/ttl connection to set password
# creates webrepl_cfg.py (not visible in uPyCraft, visible w: os.listdir()
# cannot just browse to IP with http, need client http://micropython.org/webrepl/
#  or use websocket url

# spend time in deep sleep. do not start webrepl

"""
if flash_512 == False:
  import webrepl 
  print('import webrepl_setup once to set password')
  print('start webrepl: use http://micropython.org/webrepl/ to access or use local webrepl.html')
  print('ws://192.168.1.5:8266/')
  # ws web socket
  webrepl.start()
"""




















