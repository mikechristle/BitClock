# ---------------------------------------------------------------------------
# Music Player
# Mike Christle 2024
# ---------------------------------------------------------------------------

from micropython import const
from machine import mem32, Pin, PWM, Timer
from time import sleep


# Duration
SN = 1   # Sixteenth Note
EN = 2   # Eighth Note
QN = 4   # Quarter Note
HN = 8   # Half Note
WN = 16  # Whole Note

# Pitch
C3  = 287, 53273
C3S = 545, 26479
D3  = 665, 20483
D3S = 237, 54248
E3  = 274, 44289
F3  = 175, 65452
F3S = 170, 63593
G3  = 259, 39398
G3S = 223, 43191
A3  = 219, 41511
A3S = 148, 57978
B3  = 227, 35679
C4  = 2573, 2971
C4S = 769, 9383
D4  = 281, 24237
D4S = 201, 31981
E4  = 148, 40996
F4  = 95, 60283
F3S = 851, 6352
G4  = 259, 19699
G4S = 133, 36209
A4  = 281, 16176
A4S = 74, 57978
B4  = 1163, 3482
C5  = 3623, 1055
C5S = 1709, 2111
D5  = 83, 41027
D5S = 62, 51841
E5  = 74, 40996
F5  = 347, 8252
F5S = 111, 24349
G5  = 62, 41146
G5S = 193, 12476
A5  = 281, 8088
A5S = 46, 46634
B5  = 193, 10491

# Register Base Addresses
REG_BASE = const(0x40050000)
IO_BASE  = const(0x40014004)


class MusicPlayer:

    def __init__(self, gpio):
        pin_cntl = IO_BASE + (gpio * 8)
        mem32[pin_cntl] = 0x04

        self.shift = 0 if (gpio & 1) == 0 else 16
        gpio = (gpio & 15) >> 1
        self.reg_csr = REG_BASE + (gpio * 0x14)
        self.reg_div = REG_BASE + (gpio * 0x14) + 4
        self.reg_cc  = REG_BASE + (gpio * 0x14) + 12
        self.reg_top = REG_BASE + (gpio * 0x14) + 16

        self.timer = Timer()
        self.tune = None
        self.tune_idx = 0
        self.loop_cntr = 0
        self.beat_cntr = 0
        self.done = True

    def play(self, tune, bpm, beat_note, loops = 1):
        self.done = False
        beat_time = (60 / bpm / beat_note) * 1000

        self.tune = tune
        self.tune_idx = 0
        self.beat_cntr = 0
        self.loop_cntr = loops
        self.timer.init(mode=Timer.PERIODIC,
                        period=int(beat_time),
                        callback=self.worker)

    def worker(self, _):

        if self.beat_cntr > 0:
            self.beat_cntr -= 1
            return

        mem32[self.reg_csr] = 0
        if self.tune_idx >= len(self.tune):
            self.loop_cntr -= 1
            if self.loop_cntr == 0:
                self.timer.deinit()
                self.done = True
                return
            else:
                self.tune_idx = 0

        note, self.beat_cntr = self.tune[self.tune_idx]
        div, top = note
        mem32[self.reg_div] = div
        mem32[self.reg_top] = top
        mem32[self.reg_cc] = (top // 2) << self.shift
        mem32[self.reg_csr] = 1
        self.tune_idx += 1


if __name__ == "__main__":
    DO_RA_ME = ((C4, QN), (D4, QN), (E4, QN), (F4, QN), (G4, QN), (A4, QN), (B4, QN), (C5, QN))
    mp = MusicPlayer(0)
    mp.play(DO_RA_ME, 192, QN, 2)
    while not mp.done:
        pass
