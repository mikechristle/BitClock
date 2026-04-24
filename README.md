# BitClock
How can I display the time. Let me count the ways.  

Over the years I have built several clock projects to display the time in interesting ways.
Most have had limited success because of the challenge of keeping accurate time.
This clock uses a Raspberry Pi Pico W to get the correct time over the internet.
This is definitely overkill for a clock, but at $6 I said why not.
## Overview
A clock that displays the time in binary.  
  
The display has three rows of four LEDs.
The top row displays the hour, 1 to 12.
The middle row displays the tens of minutes, 0 to 5.
The bottom row displays the ones of minutes, 0 to 9.  

The clock has a buzzer to play a song for an alarm.
To set the alarm time, use the PC Control Program.
## Code
The BitClock is controlled by a Raspberry Pi Pico W.
All the code is written in Micro-Python.
The code will get the current time over the internet using the get_ntp_time library.

The file network.info contains the login credentials for you router.
When the clock powers up, it will use this info to login, 
then display the last byte of the IP address for 10 seconds.
This address is needed in the PS control program to connect to the clock.
## PC Control Program
The control program was written in Python.
It runs on a PC and communicates with the clock with a socket connection.
I tested is on Windows, since it is Python it should run on Apple and Linux.
This program will allow you to set the alarm, set the time zone,
and adjust the LED brightness.
## PCB
The PCB was designed in KiCad version 10.0.1.
It is a two layer board.
All of the symbol and footprints are included in the local definition files.
