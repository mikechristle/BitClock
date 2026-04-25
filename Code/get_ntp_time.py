# ---------------------------------------------------------------------
# Bit Clock
# Get time from internet
# Mike Christle Mar 2026
# ---------------------------------------------------------------------

import socket

from time import gmtime
from struct import unpack
from machine import RTC

NTP_DELTA = 2208988800
HOST = "pool.ntp.org"


# ---------------------------------------------------------------------
def get_ntp_time(offset):
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(HOST, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.settimeout(2)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    except OSError as e:
        print(e)
        with open('errors.txt', 'a') as ofp:
            ofp.write("SetTime: ")
            ofp.write(str(e))
            ofp.write("\n")
            return
    finally:
        s.close()

    val = unpack("!I", msg[40:44])[0]
    tm = gmtime(val - NTP_DELTA)
    RTC().datetime((tm[0], tm[1], tm[2],           # Y/M/D
                    tm[6] + 1,                     # Day of Week 
                    tm[3] + offset, tm[4], tm[5],  # H:M:S
                    0))                            # Day of Year
