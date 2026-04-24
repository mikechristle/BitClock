# ---------------------------------------------------------------------
# Bit Clock
# Mike Christle 2024
# ---------------------------------------------------------------------

from network import WLAN, STA_IF
from socket import socket
from machine import Timer, PWM, Pin, RTC
from time import sleep, localtime, gmtime
from get_ntp_time import get_ntp_time

import music_player as mp


PATTERNS = (
    (0xFFF, 0x000),
    (0x333, 0xCCC),
    (0xFFF, 0x000),
    (0x333, 0xCCC),
    (0xFFF, 0x000),
    (0x333, 0xCCC),
    (0xFFF, 0x000),
    (0x333, 0xCCC),
)

SONG = (
    (mp.G4, mp.QN), (mp.G4, mp.QN), (mp.G4, mp.QN), (mp.A4, mp.QN),
    (mp.B4, mp.HN), (mp.G4, mp.HN),
    (mp.D5, mp.QN), (mp.D5, mp.QN), (mp.D5, mp.QN), (mp.E5, mp.QN),
    (mp.D5, mp.WN),
    (mp.D5, mp.QN), (mp.E5, mp.QN), (mp.D5, mp.QN), (mp.C5, mp.QN),
    (mp.B4, mp.HN), (mp.G4, mp.HN),
    (mp.A4, mp.QN), (mp.C5, mp.QN), (mp.B4, mp.QN), (mp.A4, mp.QN),
    (mp.G4, mp.WN),
)

player = mp.MusicPlayer(15)

minute = -1
hour = -1

alarm_hr = -1
alarm_mn = 0
alarm_state = 0

bright0 = 600
bright1 = 32000

clock_timer = Timer()
anima_timer = Timer()

h0 = PWM(Pin(2), freq=500, duty_u16=0)
h1 = PWM(Pin(5), freq=500, duty_u16=0)
h2 = PWM(Pin(9), freq=500, duty_u16=0)
h3 = PWM(Pin(13), freq=500, duty_u16=0)
t0 = PWM(Pin(1), freq=500, duty_u16=0)
t1 = PWM(Pin(4), freq=500, duty_u16=0)
t2 = PWM(Pin(8), freq=500, duty_u16=0)
t3 = PWM(Pin(12), freq=500, duty_u16=0)
m0 = PWM(Pin(0), freq=500, duty_u16=0)
m1 = PWM(Pin(3), freq=500, duty_u16=0)
m2 = PWM(Pin(7), freq=500, duty_u16=0)
m3 = PWM(Pin(11), freq=500, duty_u16=0)

# ---------------------------------------------------------------------
# Update the time
# ---------------------------------------------------------------------
def check_time(timer):
    global hour, minute, alarm_state, alarm_hr, alarm_mn

    t = localtime()
    if t[4] != minute:
        if hour == 3 and minute == 41:
            set_time()
            t = localtime()

        hour = t[3]
        minute = t[4]
        update_display(hour, minute)

        if hour == alarm_hr and minute == alarm_mn:
            animation_init()
            player.play(SONG, 192, mp.QN, 3)
            alarm_hr = alarm_mn = -1


# ---------------------------------------------------------------------
def animation_init():
    global pats_idx, pat_idx, pat_cnt

    pats_idx = 0
    pat_idx = 0
    pat_cnt = 0
    anima_timer.init(period=200, callback=animation)


# ---------------------------------------------------------------------
def animation(_):
    global pats_idx, pat_idx, pat_cnt

    pats = PATTERNS[pats_idx]
    pat = pats[pat_idx]
    h = pat >> 8
    t = (pat >> 4) & 15
    m = pat & 15
    write_display(h, t, m)
    pat_idx += 1
    if pat_idx >= len(pats):
        pat_idx = 0
        pat_cnt += 1
        if pat_cnt >= 10:
            pat_cnt = 0
            pats_idx += 1
            if pats_idx >= len(PATTERNS):
                anima_timer.deinit()
                update_display(hour, minute)


# ---------------------------------------------------------------------
def update_display(h, m):

#     print(f'{h:02}:{m:02}')
    t = m // 10
    m = m % 10
    h = h - 12 if h > 12 else h
    h = 12 if h == 0 else h
    write_display(h, t, m)


# ---------------------------------------------------------------------
def write_display(h, t, m):

    pw = bright0 if (m & 1) == 0 else bright1
    m0.duty_u16(pw)
    pw = bright0 if (m & 2) == 0 else bright1
    m1.duty_u16(pw)
    pw = bright0 if (m & 4) == 0 else bright1
    m2.duty_u16(pw)
    pw = bright0 if (m & 8) == 0 else bright1
    m3.duty_u16(pw)
        
    pw = bright0 if (t & 1) == 0 else bright1
    t0.duty_u16(pw)
    pw = bright0 if (t & 2) == 0 else bright1
    t1.duty_u16(pw)
    pw = bright0 if (t & 4) == 0 else bright1
    t2.duty_u16(pw)
    pw = bright0 if (t & 8) == 0 else bright1
    t3.duty_u16(pw)
    
    pw = bright0 if (h & 1) == 0 else bright1
    h0.duty_u16(pw)
    pw = bright0 if (h & 2) == 0 else bright1
    h1.duty_u16(pw)
    pw = bright0 if (h & 4) == 0 else bright1
    h2.duty_u16(pw)
    pw = bright0 if (h & 8) == 0 else bright1
    h3.duty_u16(pw)


# ---------------------------------------------------------------------
def set_time():
    global hour, minute

    # Get the time zone
    with open('time_zone.txt', 'rt') as ifp:
        offset = ifp.read()

    # Get the current URC time
    get_ntp_time(int(offset))

    # Display Time
    dt = localtime()
    update_display(dt[4], dt[5])
    print(dt)


# ---------------------------------------------------------------------
# Setup internet connection
# ---------------------------------------------------------------------

with open("network.info", "r") as file:
    SSID = file.readline().strip()
    PSWD = file.readline().strip()

wlan = WLAN(STA_IF)
wlan.active(True)
wlan.connect(SSID, PSWD)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    sleep(1)

ip = wlan.ifconfig()[0]
print(ip)

# Display the IP address LSB
idx = ip.rfind('.')
ip3 = int(ip[idx + 1:])
update_display(ip3 // 100, ip3 % 100)
sleep(10.0)

# Open socket receiver
conn = socket()
conn.bind((ip, 23))
conn.listen()

# Get the current time
set_time()

# Start the clock timer
clock_timer.init(freq=0.2, callback=check_time)

# Main loop to wait for input connection
while True:

    try:
        client = conn.accept()[0]
        while True:
            msg = client.recv(1024).decode("utf-8")
            print(msg)

            # Close Connection
            if msg == 'bye':
                break

            # Set One Brightness
            if msg[:2] == 'b1':
                bright1 = int(msg[2:]) * 650
                client.send('OK')
                update_display(hour, minute)

            # Set Zero Brightness
            elif msg[:2] == 'b0':
                bright0 = int(msg[2:]) * 650
                client.send('OK')
                update_display(hour, minute)

            # Get Alarm Time
            elif msg[:2] == 'ga':
                client.send(f'{alarm_hr:02}:{alarm_mn:02}')

            # Get Time
            elif msg[:2] == 'gt':
                client.send(f'{hour:02}:{minute:02}')

            # Get Time Zone Offset
            elif msg[:2] == 'gz':
                with open('time_zone.txt','rt') as ifp:
                    tz = ifp.read()
                client.send(tz)

            # Set Time Zone Offset
            elif msg[:2] == 'sz':
                with open('time_zone.txt','wt') as ofp:
                    ofp.write(msg[2:])
                set_time()
                client.send('OK')

            # Set Alarm Time
            elif msg[:2] == 'sa':
                idx = msg.find(':')
                alarm_hr = int(msg[2:idx])
                alarm_mn = int(msg[idx + 1:])
                client.send('OK')

            # Anything else is an error
            else:
                client.send('ERROR')

        client.close()
        print('here 3')
    except Exception as e:
        ct = localtime()
        ts = f'{ct[0]}/{ct[1]}/{ct[2]}  {ct[3]}:{ct[4]}\n'
        print(f'Error: {e}')
        with open('error.txt', 'a') as ofp:
            ofp.write(f'MainLoop: {e}\n{ts}\n\n')
        client.close()
