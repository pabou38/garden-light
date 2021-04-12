
print("\nESP8266 led12V.py starting. deep sleep mode")

from machine import Pin
from time import sleep_ms, sleep

import blynklib_mp as  blynklib# no .mpy
import blynktimer  # Timer exists here and in machine
"""
import BlynkLib # import mpy . .py creates memory alloc error
old lib https://github.com/vshymanskyy/blynk-library-python

# new lib
#https://github.com/blynkkk/lib-python
#https://pypi.org/project/blynklib/ Feb 2020 0.2.6
# use uPyLoader to transfert .mpy file, cross compiled with mpy_cross
"""

# module path . /lib /
# optimize heap
#https://www.beningo.com/5-tips-for-optimizing-the-heap-in-micropython/

import sys
import esp
#from micropython import mem_info, stack_use
from micropython import const
from machine import idle, Timer, RTC, reset_cause, DEEPSLEEP_RESET, DEEPSLEEP, deepsleep
#from machine import lightsleep, deepsleep

import uos # for random
#import urandom # build in, in help('modules'), ie list of module that can be imported
# u means micropython ified. subset of Cpython
# correspond to micropython-random in pypi.org/projects/micropython-random
# note almost empty library. there to avoid import errors

# uos.random is also available uos.urandom(2) returns 2 bytes b'\xf4\xe8'


import gc
gc.collect()

# avoid wifi reconnect issue
sleep_milli = 1 * 60 * 1000 # 
max_slider = 9 # defined when creating slider widget. 0 always off, max always on


# GPIO for MOSFET
# save bytecode thus RAM _ , not visible ouside. no mem
# Wemos D1 mini Lite (1MB) or mini (4MB)
# blue D5, gpio 14
# red D6, gpio 12
# green D7, gpio 13
# fluo D1,  gpio 5
# test D2, gpio 4

# D1 gpio 5, rx gpio 3


# fluo on D8 GPIO 15, problem at boot
# fluo on D2 gpio 4, seems to stay on while deep sleep
# fluo on D4 gpio 2, blue led on



_redled = const(12) 
red_led = _redled
_greenled = const(13) 
green_led = _greenled
_blueled = const(14) 
blue_led = _blueled

#value is valid only for Pin.OUT and Pin.OPEN_DRAIN modes and specifies initial output pin value if given, otherwise the state of the pin peripheral remains unchanged.
pin_red = Pin(red_led, Pin.OUT, value=0)
pin_green = Pin(green_led, Pin.OUT, value=0)
pin_blue = Pin(blue_led, Pin.OUT, value=0)

fluo = const(5)
pin_fluo = Pin(fluo, Pin.OUT, value=0)

# D2, gpio 4
# test GPIO , input
test_pin = Pin(4, Pin.IN, Pin.PULL_UP)

pin_red.off()
pin_blue.off() # this pin seems to be ON at boot
pin_green.off()
pin_fluo.off()

"""
# i2c not used
_sda= const(4)
sda = _sda # D2
_scl = const(5)
scl=_scl # D1
"""


# pulse each led to signal boot started
print('pulse led at start')
pin_red.on()
sleep(1)
pin_red.off()

pin_green.on()
sleep(1)
pin_green.off()

pin_blue.on()
sleep(1)
pin_blue.off()

pin_fluo.on()
sleep(1)
pin_fluo.off()

# separate module. inline in main created memory allocation issues
# also more modular
import mywifi

# will be used in wifi.disconnect()
wifi = mywifi.wifi

if (mywifi.wifi_ok == False):
  print('could not connect to any wifi. long pulse red led')
  pin_red.on()
  sleep(3)
  pin_red.off()
  
  from machine import idle, Timer, RTC, reset_cause, DEEPSLEEP_RESET, DEEPSLEEP, deepsleep
  from time import sleep
  
  # configure RTC.ALARM0 to be able to wake the device
  rtc = RTC()
  rtc.irq(trigger=rtc.ALARM0, wake=DEEPSLEEP)

  # set RTC.ALARM0 to fire after x seconds (waking the device)
  rtc.alarm(rtc.ALARM0, 3 * 60 * 1000) # enough time to avoid wifi reconnection problem 
  print('wifi connect issue. enter deep sleep 3m')
  # put the device to sleep
  deepsleep()
# cannot connect to any wifi

else:
  # signal wifi OK with short pulse
  print('wifi OK. short pulse green led')
  pin_green.on()
  sleep(0.5)
  pin_green.off()


# read test pin (pull up)
# connect D1 to gnd to avoid any deep sleep. allow to reflash in peace
# can also use START button in blynk, but depend on availablity of Blynk private server
if test_pin.value() == 0:
  print('==== > test pin is pulled LOW. short pulse blue, start webrepl, and just sit there and idle. will not run app. can CTRL C or reboots')

  # signal not deep sleeping with short blue pulse
  pin_blue.on()
  sleep(0.5)
  pin_blue.off()
  
  import webrepl 
  print('start webrepl: use http://micropython.org/webrepl/ to access or use local webrepl.html')
  print('client uses websocket url ws://192.168.1.6:8266/') # url scheme not allowed in browser
  webrepl.start()
  # can send updated files while in that state.
  # cannot use blynk notify. use may just ping the IP address to validate the system is running
  while True:
    sleep(10)
else:
  print('==== > test pin is HIGH. keep going. short green pulse')
  pin_green.on()
  sleep(0.5)
  pin_green.off()



#####################################
# enter deep sleep if
#  wifi connect error
#  blynk run error
#  blynk connect error
#  start button is OFF
####################################

##################################
# toggle green led at start of script

# long pulse red led if wifi connect error
# short pulse green led if wifi OK

# short blue pulse if not deep sleeping, else short green pulse

# toggle blue led if blynk connect ok 
# toggle red led if blynk connect fails
##################################

###################################
# wakeup, if start is OFF, sleep
# else, pulse led based on sliders, until start is OFF
# essentially, start is on ON/OFF button. ON is delayed until next deep sleep wakeup
###################################

"""
WARNING. GPIO 14 seems to be low at run time. led up during sleep

"""

# check if the device woke from a deep sleep
if reset_cause() == DEEPSLEEP_RESET:
  print('woke from a deep sleep')
  from_deep = True
else:
  print('woke from a fresh boot')
  from_deep = False
  

###############################################
# deep sleep
###############################################
def enter_deep_sleep(ms): # milli 30000 is 30 sec
  global wifi
  # configure RTC.ALARM0 to be able to wake the device
  rtc = RTC()
  rtc.irq(trigger=rtc.ALARM0, wake=DEEPSLEEP)

  # set RTC.ALARM0 to fire after x seconds (waking the device)
  rtc.alarm(rtc.ALARM0, ms) # enough time 

  print('disconnect wifi to avoid reconnect issues')
  wifi.disconnect() # global var

  print('set all pin to low to make sure')
  pin_blue.off()
  pin_fluo.off()
  pin_red.off()
  pin_green.off()

  print('enter deep sleep %d ms' %ms)
  # put the device to sleep
  deepsleep()


"""
# use blynk timer to upate led
# create timers dispatcher instance
# disable exception raise if all all timers were stopped
blynk_timer = blynktimer.Timer(no_timers_err=False)
@blynk_timer.register(interval=1, run_once=False)
"""

##############################
# pulse_led, called by RTOS timer every x ms
# increment ticks (global) at each run
# when tick = slider value (global) , toggle led based on status
# slider value = 0 mean always off

##############################
def pulse_led(a):
  global tick_red, tick_green, tick_blue, tick_fluo # counter of ticks before toggleing
  global status_red, status_green, status_blue, status_fluo # to toggle
  
  # sanity check
  
  if (blynk.is_server_alive()) == False:
    print('pulse led: Warning Blynk server not alive!!!')

  #print('sliders: red %d, green %d, blue %d' %(slider_red,slider_green,slider_blue))
  #print('tick: red %d, green %d, blue %d' %(tick_red,tick_green,tick_blue))
  print('R%d G%d B%d F%d' %(tick_red, tick_green, tick_blue,tick_fluo))
 
  if slider_red == 0:
    pin_red.off() # to set off

  elif slider_red == max_slider:
    pin_red.on()

  # use slider value to set ticks
  else:
    tick_red = tick_red + 1 # update here to prevent counter from overflow if slider is 0
    # toggle led if ticker count reach slider value
    if tick_red >= slider_red:
      tick_red=0 # reset counter

      # time to toggle based on current led status
      if status_red:
        status_red=False
        pin_red.off()
      else:
        status_red=True
        pin_red.on()
        
        
  if slider_green == 0:
    pin_green.off()
  elif slider_green == max_slider:
    pin_green.on()
  else:
    tick_green = tick_green + 1
    if tick_green >= slider_green:
      tick_green=0
      if status_green:
        status_green=False
        pin_green.off()
      else:
        status_green=True
        pin_green.on() 
     
  
  if slider_blue == 0:
    pin_blue.off()
  elif slider_blue == max_slider:
    pin_blue.on()
  else:
    tick_blue = tick_blue + 1  
    if tick_blue >= slider_blue:
      tick_blue=0
      if status_blue:
        status_blue=False
        pin_blue.off()
      else:
        status_blue=True
        pin_blue.on() 

  if slider_fluo == 0:
    pin_fluo.off()
  elif slider_fluo == max_slider:
    pin_fluo.on()
  else:
    tick_fluo = tick_fluo + 1  
    if tick_fluo >= slider_fluo:
      tick_fluo=0
      if status_fluo:
        status_fluo=False
        pin_fluo.off()
      else:
        status_fluo=True
        pin_fluo.on()

############################################
# pulse a given led, to signal something
############################################
def toggle_led(pin):
  pin_blue.off()
  pin_red.off()
  pin_green.off() # set to off
  pin_fluo.off()

  loop_ms=200
  for i in range(5):
      pin.on()
      sleep_ms(loop_ms)
      pin.off()
      sleep_ms(loop_ms) # end ON to set led strip OFF
      
  pin_blue.off()
  pin_red.off()
  pin_green.off() # set to off
  pin_fluo.off()


    
"""
import BlynkLib # import mpy . .py creates memory alloc error
old lib https://github.com/vshymanskyy/blynk-library-python

# new lib
#https://github.com/blynkkk/lib-python
#https://pypi.org/project/blynklib/ Feb 2020 0.2.6
# use uPyLoader to transfert .mpy file, cross compiled with mpy_cross
"""


################################################
# Blynk private server
# systemctl status blynk_server
# https://IP:9443  (certif may not be valid)
# login admin@blynk.cc  
################################################


# blynk virtual pins
########################
# displays
# defined when creating blynk widget on smartphone
########################

# test led. response to test button
_bled = const(2)
b_led = _bled  

# random value
b_rand = const(7) # value display random int to indicate alive

# feedback on start button
b_start_led = const(8) # led to ack we saw the start button synced to ON after deep sleep

#######################################
# controllers: need write handler
# defined when creating blynk widget on smartphone
#######################################

# test button
_button = const(1)
b_button = _button

# start button
b_start = const(3) # keep running app after wakeup, or go back to deep sleep

# sliders
# slider are Vpin 4,5,6. value hardcoded in call back name
# new slide V9 for fluo
# slider value 0 to 9

"""
# heap vs stack
#https://www.guru99.com/stack-vs-heap.html

# heap is 37952 bytes. note: stack is fixed 8192 / 1024 = 8Kio
print("gc mem free: ", gc.mem_free())
print("gc mem alloc: ", gc.mem_alloc())
print ("heap sum: ", gc.mem_free()+gc.mem_alloc())
gc.collect() # force garbage collection
sleep_ms(1000)

print("gc mem free: ", gc.mem_free())
print("gc mem alloc: ", gc.mem_alloc())
print ("heap sum: ", gc.mem_free()+gc.mem_alloc())

# garbage collection can be executed manually, if alloc fails, or if 25% of 
# currently free heap becomes occupied
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

print("stack used: ", stack_use())

print("mem info: ", mem_info()) # (1) verbose
"""

"""
The information that is printed is implementation dependent, 
but currently includes the amount of stack and heap used. 
In verbose mode (1) it prints out the entire heap indicating 
which blocks are used and which are free.  . free block

Each letter represents a single block of memory, a block being 16 bytes. 
So each line of the heap dump represents 0x400 bytes or 1KiB of RAM.

00000: h=hhhhBM.LDSShDhB=.B=Bhh=SB=h====h===hh==h======================
00400: ================================================================

03800: ...........h========h============...............................
(22 lines all free)
09400: ....

15 + 22 lines + 4x16 bytes.  37x1024 + 64 = 37952 . GC: total: 37952, used: 8000, free: 29952

stack: 2128 out of 8192

"""

"""
upip.install
Its best to do this just after doing a gc.collect(). 
Each byte corresponds to 8 bytes of memory. 
To allocate 4084 bytes would require 510 contiguous blocks.
"""

"""
print ("implementation: ",sys.implementation)  # no ()
print ("platform: ", sys.platform)
print ("version: ",sys.version)
print("sys.path: ", sys.path) # list
print("modules imported: ", sys.modules) # dict


# not available in 512K port
print('list files')
s = uos.listdir()
print(type(s))
for x in s:
  print(x)
"""

"""
# save energy, only toggle when initial start vs deep sleep wakeup
if from_deep == False:
  print('toggle green led at initial boot')
  toggle_led(pin_green)
"""

#gc.collect()

# sliders value
slider_red=0
slider_blue=0
slider_green=0
slider_fluo=0

# incremented in timer
tick_red=0
tick_green=0
tick_blue=0
tick_fluo=0

# used to track on off state of led
status_red=False # means OFF
status_blue=False
status_green=False
status_fluo=False

# project meaudre, cloud server
#blynk = BlynkLib.Blynk('128bf199aa8744f88a586beecb6b64d9')

# project led, cloud server
#https://github.com/blynkkk/lib-python
#blynk = blynklib.Blynk('cb0559b1ea7e40328569ebc2ea934327')

print("\nUsing Blynk private server. project led")
blynk = blynklib.Blynk('Q9sbBFieMj3WMrX3G4JKA-qKtHl1feHb',server="192.168.1.204", port=8090)

print ('blynk object created: ' , type(blynk))


# Blynk call backs
####################### BLYNK CALL BACKS ##################################

first_connect = True
@blynk.handle_event("connect")
def connect_handler():
  global first_connect
  print("     in connect handler: blynk connected")
  if first_connect: # avoid connect, disconnect
    # not in case de wake from deep sleep
    #blynk.notify('micropython led starting')
    #blynk.email('pboudalier@gmail.com', 'micropython led', 'starting')
    first_connect=False
  
  print('       sync start button and sliders')
  # start button will should be the first call back to be executed. if run is false, will go to deep sleep
  blynk.virtual_sync(b_start) # start button

  blynk.virtual_sync(4) # green slider
  blynk.virtual_sync(5) # red slider
  blynk.virtual_sync(6) # blue slider
  blynk.virtual_sync(9) # fluo slider
    
@blynk.handle_event("disconnect")
def disconnect_handler():
    print("     blynk disconnected ..")
    

# register handler for Virtual Pin V reading by Blynk App.
# when a widget in Blynk App asks Virtual Pin data from server within given configurable interval (1,2,5,10 sec etc) 
# server automatically sends notification about read virtual pin event to hardware
# this notification captured by current handler 

# read test button 1 and update test led 2

@blynk.handle_event('write V1')
def write_virtual_pin_handler(pin, value): # value is a list of str
  print('     call back test button: vpin %d test button pushed in app: %s' %(pin, value[0]))
  print("     write to test led")
  if value[0] == '0':
    blynk.virtual_write(b_led,0)
  else:
    blynk.virtual_write(b_led,255)
    
    

# read start button 3. if pushed, will run apps until pushed again, if not pushed, will go to deep sleep immediatly
# communicate with two globals, bolean and int for value of button
# called by sync or if button is pushed and app running, ie a way to stop the app and go to deep sleep

@blynk.handle_event('write V3')
def write_virtual_pin_handler_v3(pin, value): # value is a list of str
  global start_synched # to communicate to main thread that this button has synched
  global start_status # value of button, int
  print('     v3 call back start button: vpin %d start button: %s.' %(pin, value[0]))
  start_status = int(value[0]) # value of button
  
  # update start status led
  if start_status == 1: # button is ON
    start_synched = True # NOT USED ANYMORE main thread waiting for that
    print('     v3 call back: start is ON. keeps running. update start led, notify and email') 
    blynk.virtual_write(b_start_led,255)
    blynk.notify('micropython led not going to deep sleep, keeps running')
    blynk.email('pboudalier@gmail.com', 'micropython led', 'keeps running')

    # do not deep sleep, blynk connect 

  else:
    print('     v3 call back: start button is OFF, will sleep shortly') # button is OFF
    # update led on smartphone
    blynk.virtual_write(b_start_led,0)

    ##############################################
    # enter deep sleep
    ##############################################

    # will trigger disconnect call back
    # disconnect explicitly, otherwize next connect may not work (liggering ?)
    print('     v3 Blynk disconnect before deep sleep')
    blynk.disconnect()

    # WARNING. should disconnect from wifi. seems to create connection issue nexty time (but not next next time)

    # enter deep sleep if OFF at wakeup, or OFF during running
    sleep(3) # time for led off, and random int write ?
    # while sleeping, the timer will still pop up

    print('     v3 deep sleep %d ms' %sleep_milli)
    enter_deep_sleep(sleep_milli)
# end start buttion call back 



# update slider values
# note pin virtual number is hardcoded
# called by sync , or if slider is moved
# set slider_x global variables


@blynk.handle_event('write V5')
def write_virtual_pin_handler_v5(pin, value): # value is a list of str
  global slider_red
  print('     pin %d pushed in app: %s. red' %(pin, value[0]))
  slider_red = int(value[0])

# read green slider
@blynk.handle_event('write V4')
def write_virtual_pin_handler_v4(pin, value): # value is a list of str
  global slider_green
  print('     pin %d pushed in app: %s. green' %(pin, value[0]))
  slider_green = int(value[0])

# read blue slider
@blynk.handle_event('write V6')
def write_virtual_pin_handler_v6(pin, value): # value is a list of str
  global slider_blue
  print('     pin %d pushed in app: %s. blue' %(pin, value[0]))
  slider_blue = int(value[0])

# read fluo slider
@blynk.handle_event('write V9')
def write_virtual_pin_handler_v9(pin, value): # value is a list of str
  global slider_fluo
  print('     pin %d pushed in app: %s. fluo' %(pin, value[0]))
  slider_fluo = int(value[0])

""" 
Read handler:
read handler are for display , eg value displays which wants periodic
update. server will send a read request, handed in read handler
not used if the display widget is in push mode

each N seconds Blynk app widget will do Virtual Pin reading operation.
Blynk Server for App read request will return current pin value
Additionally Blynk server will fire read virtual pin event and send it to hardware
If read pin event was registered on hardware certain handler will be executed
"""

################### end of Blynk call backs ####################################


#####################################################
# blynk connect
# start RTOS timer
# blynk run (endless loop)
#####################################################


# connect now to get sync done and read start button   
start_synched = False  # there to avoid race condition

print('blynk.connect() before run endless loop')
# connect default timeout 30sec
if (blynk.connect(timeout=30)): # boolean
  
  print('from deep ? %d: connected to blynk !!!!. toggle blue led' %(from_deep))
  # toggle blue led to signal BLYNK OK
  toggle_led(pin_blue) # means OK
  
    
else:
  # toggle red led in any case to signal Blynk connect error
  print('from deep ? %d: cannot connect to blynk. disconnect wifi, toggle red led and deep sleep %d ms' %(from_deep, sleep_milli))

  # do not go further
  wifi.disconnect()
  toggle_led(pin_red)
  enter_deep_sleep(sleep_milli)

# connected to blynk  
# update random int at each boot to indicate deep sleep is waking up
rand = uos.urandom(1)[0]
print('random int, write to widget: %d' %(rand))
blynk.virtual_write(b_rand,rand)

"""
# cannot wait for callback to execute before Blynk.run 
# need to wait for start button to sync. 
# if on , keep running until button is then set to off
# else go to deep sleep
i=0

while (start_synched == False) and (i<10):
  print("%d %d" %(start_synched, i))
  sleep(2)
  i = i + 1
  
if start_synched:
  # start_status is int button value, set in call back
  print('start button has synched %d' %(start_status))
  
  if start_status == 0: # normally not needed, sleep done in call back to cover all cases
    # ie button OFF at wakeup and OFF while running (ie was ON at wakeup)
    print('start status is OFF, sleep')
    enter_deep_sleep(sleep_milli)
else:
  print('ERROR: start button has NOT synched, enter deep sleep')
  enter_deep_sleep(sleep_milli)
  
# button has synched and start status is ON (else deep sleep) 
# run forever , until start button is pressed OFF (sleep is in button call back)

"""

#################################################################
# Main
#################################################################

# need to call Blynk.run to have callback read start button value
# and as Blynk.run does not return, need to start apps.

####################################
# timer to pulse led
####################################
tim = Timer(-1)
period = 500
# in ms

print ('create micropython virtual timer to pulse led, period = %d ms' %period)
# every 500 ms, so slider = 3 means toggle led every 1.5 sec
tim.init(period=period, mode=Timer.PERIODIC, callback=lambda t:pulse_led(1))

####################################
# timer to reconnect
####################################
tim1 = Timer(-1)
print ('create micropython virtual timer to (re) connnect to blynk in case every so ofter')
# 60 sec
tim1.init(period=60000, mode=Timer.PERIODIC, callback=lambda t:blynk.connect())

# Run blynk in the main thread:
print('run blynk.run endless loop in main thread. should not return')

# blynk.run will makes call back happend
# does no return unless error
try:
  while True:
    blynk.run()
    #blynk_timer.run()
    #idle() # creates connect disconnect ?

except Exception as e:
  print('!!!!blynk run exception %s', str(e))
  print('!!! will notify, email , disconnect blynk and wifi and deep sleep')
  blynk.notify('micropython blynk.run exception: %s ' %(str(e)))
  blynk.email('pboudalier@gmail.com', 'micropython blynk run exception', str(e))
  blynk.disconnect() 
  wifi.disconnect()
  enter_deep_sleep(sleep_milli)
  
"""
machine.idle: Gates the clock to the CPU, useful to reduce power consumption 
at any time during short or long periods. Peripherals continue working 
and execution resumes as soon as any interrupt is triggered 
(on many ports this includes system timer interrupt occurring at 
regular intervals on the order of millisecond).
"""

print('!!!! after blynk.run. should NEVER get there')
print ("exit")

# Or, run blynk in a separate thread (unavailable for esp8266):
#import _thread
#_thread.stack_size(5*1024)
#_thread.start_new_thread(runLoop, ())
# 
# Threads are currently unavailable on some devices like esp8266






































