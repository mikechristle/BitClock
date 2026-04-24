# ---------------------------------------------------------------------
# Bit Clock Controller
# Mike Christle 2024
# ---------------------------------------------------------------------

import socket
import tkinter as tk

from sys import exit

LABEL_FONT = 'arial 12'
TEXT_FONT = 'arial 16'
TIME_FONT = 'arial 32'


# Edit this IP address to match the address of the clock.
host = '192.168.1.152'
port = 23
soc = socket.socket()

try:
    soc.connect((host, port))
except Exception as e:
    print(e)
    input('Press enter to proceed')
    exit(-1)


# ---------------------------------------------------------------------
def b1_cmnd(event):
    msg = 'b1' + event
    soc.send(msg.encode())
    data = soc.recv(64).decode()
    txt_box.insert(tk.END, f'{data}\n')


# ---------------------------------------------------------------------
def b0_cmnd(event):
    msg = 'b0' + event
    soc.send(msg.encode())
    data = soc.recv(64).decode()
    txt_box.insert(tk.END, f'{data}\n')


# ---------------------------------------------------------------------
def get_alarm():
    soc.send('ga'.encode())
    data = soc.recv(64).decode()
    txt_box.insert(tk.END, f'Alarm {data}\n')
    tb_alarm.delete(0, tk.END)
    idx = data.find(':')
    hr = int(data[:idx])
    mn = int(data[idx + 1:])
    if hr < 0 or mn < 0:
        tb_alarm.insert(0, 'OFF')
    else:
        tb_alarm.insert(0, data)


# ---------------------------------------------------------------------
def set_alarm(_):

    val = tb_alarm.get()
    txt_box.insert(tk.END, f'Set Alarm {val}\n')
    lb_error['text'] = ''
    idx = val.find(':')
    if idx < 1 or idx > 3:
        lb_error['text'] = 'Invalid Time'
        return

    hour = int(val[:idx])
    minute = int(val[idx + 1:])
    if hour < -1 or hour > 23 or minute < 0 or minute > 59:
        lb_error['text'] = 'Invalid Time'
        return

    val = f'sa{hour}:{minute}'
    soc.send(val.encode())
    data = soc.recv(64).decode()
    txt_box.insert(tk.END, f'{data}\n')
    get_alarm()


# ---------------------------------------------------------------------
def get_zone():
    soc.send('gz'.encode())
    data = soc.recv(64).decode()
    tb_zone.delete(0, tk.END)
    tb_zone.insert(0, data)


# ---------------------------------------------------------------------
def set_zone(_):
    msg = f'sz{tb_zone.get()}'
    soc.send(msg.encode())
    data = soc.recv(64).decode()
    txt_box.insert(tk.END, f'{data}\n')
    get_zone()
    get_time()


# ---------------------------------------------------------------------
def get_time():
    soc.send('gt'.encode())
    data = soc.recv(64).decode()
    txt_box.insert(tk.END, f'Time {data}\n')
    lb_time['text'] = data


# ---------------------------------------------------------------------
win = tk.Tk()
win.title('Bit Clock Controller')
win.geometry('400x500')

# - - - - - - - - - - - - - - - - - - - - - - - -
frm0 = tk.Frame(win)

lb_time = tk.Label(frm0,
                   text='__:__',
                   font=TIME_FONT)
lb_time.pack(padx=20, pady=20)

lb_zone_msg = tk.Label(frm0,
                       text='Time Zone Offset',
                       font=LABEL_FONT)
lb_zone_msg.pack()

tb_zone = tk.Entry(frm0,
                   font=TEXT_FONT,
                   width=5)
tb_zone.bind('<Return>', set_zone)
tb_zone.pack(padx=5, pady=5)

lb_alarm = tk.Label(frm0,
                    text='Alarm Time',
                    font=LABEL_FONT)
lb_alarm.pack(padx=5, pady=5)

tb_alarm = tk.Entry(frm0,
                    font=TEXT_FONT,
                    width=5)
tb_alarm.bind('<Return>', set_alarm)
tb_alarm.pack(padx=5, pady=5)

lb_error = tk.Label(frm0, fg='RED', font=TEXT_FONT)
lb_error.pack(padx=5, pady=5)

frm0.grid(row=0, column=0,
          padx=20, pady=20)

# - - - - - - - - - - - - - - - - - - - - - - - -
frm1 = tk.Frame(win)

# One Brightness Slider
b1 = tk.Scale(frm1,
              from_=0, to=100,
              orient=tk.HORIZONTAL,
              command=b1_cmnd)
b1.pack()
lb_b1 = tk.Label(frm1,
                 text='One Brightness',
                 font=LABEL_FONT)
lb_b1.pack()

# Zero Brightness Slider
b0 = tk.Scale(frm1,
              from_=0, to=100,
              orient=tk.HORIZONTAL,
              command=b0_cmnd)
b0.pack()
lb_b0 = tk.Label(frm1,
                 text='Zero Brightness',
                 font=LABEL_FONT)
lb_b0.pack()

frm1.grid(row=0, column=1,
          padx=20, pady=5)

frm2 = tk.Frame(win)

txt_box = tk.Text(frm2,
                  width=30, height=7,
                  font='arial 16')
txt_box.pack(side="left", fill="both", expand=True)

# Create the Scrollbar widget
sbar = tk.Scrollbar(frm2, command=txt_box.yview)
sbar.pack(side="right", fill="y")

# Configure the Text widget to use the Scrollbar
txt_box.config(yscrollcommand=sbar.set)

frm2.grid(row=1, column=0,
          columnspan=2,
          padx=5, pady=5)

# - - - - - - - - - - - - - - - - - - - - - - - -
get_alarm()
get_time()
get_zone()
# update_tz('tz')

win.mainloop()
soc.send('bye'.encode())
soc.close()
