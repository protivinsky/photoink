import os
import random
import time
import alarm
import busio
import board
import digitalio
import adafruit_max1704x


spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
while not spi.try_lock():
    pass
spi.configure(baudrate=1000000)


PIN_DC = digitalio.DigitalInOut(board.D9)
PIN_DC.direction = digitalio.Direction.OUTPUT
PIN_RES = digitalio.DigitalInOut(board.D6)
PIN_RES.direction = digitalio.Direction.OUTPUT
PIN_CS = digitalio.DigitalInOut(board.D10)
PIN_CS.direction = digitalio.Direction.OUTPUT
PIN_BUSY = digitalio.DigitalInOut(board.D5)
PIN_BUSY.direction = digitalio.Direction.INPUT

# 8bit
Black = 0x00    # 000
White = 0x11    # 001
Green = 0x22    # 010
Blue = 0x33     # 011
Red = 0x44      # 100
Yellow = 0x55   # 101
Orange = 0x66   # 110
Clean = 0x77    # 111

# 4bit
black = 0x00    # 000
white = 0x01    # 001
green = 0x02    # 010
blue = 0x03     # 011
red = 0x04      # 100
yellow = 0x05   # 101
orange = 0x06   # 110
clean = 0x07    # 111

# control vars
PSR = 0x00
PWRR = 0x01
POF = 0x02
POFS = 0x03
PON = 0x04
BTST1 = 0x05
BTST2 = 0x06
DSLP = 0x07
BTST3 = 0x08
DTM = 0x10
DRF = 0x12
PLL = 0x30
CDI = 0x50
TCON = 0x60
TRES = 0x61
REV = 0x70
VDCS = 0x82
T_VDCS = 0x84
PWS = 0xE3


def set_pin(pin, value):
    pin.value = value


def set_cs(value):
    pass
    # set_pin(PIN_CS, value)


EPD_W21_RST_0 = lambda: set_pin(PIN_RES, False)
EPD_W21_RST_1 = lambda: set_pin(PIN_RES, True)
EPD_W21_DC_0 = lambda: set_pin(PIN_DC, False)
EPD_W21_DC_1 = lambda: set_pin(PIN_DC, True)


def wait_for_display():
    while (not PIN_BUSY.value):
        ...

def write_cmd(command):
    set_cs(False)
    PIN_DC.value = False
    spi.write(bytes([command]))
    set_cs(True)


def write_data(data):
    set_cs(False)
    PIN_DC.value = True
    data = data if isinstance(data, list) else [data]
    spi.write(bytes(data))
    set_cs(True)


def init():
    set_cs(False)
    PIN_RES.value = False
    time.sleep(0.01)
    PIN_RES.value = True
    time.sleep(0.01)
    set_cs(True)


def display_init():
    init()
    write_cmd(0xaa)
    write_data([0x49, 0x55, 0x20, 0x08, 0x09, 0x18])
    write_cmd(PWRR)
    write_data([0x3F, 0x00, 0x32, 0x2A, 0x0E, 0x2A])
    write_cmd(PSR)
    write_data([0x5F, 0x69])
    write_cmd(POFS)
    write_data([0x00, 0x54, 0x00, 0x44])
    write_cmd(BTST1)
    write_data([0x40, 0x1F, 0x1F, 0x2C])
    write_cmd(BTST2)
    write_data([0x6F, 0x1F, 0x16, 0x25])
    write_cmd(BTST3)
    write_data([0x6F, 0x1F, 0x1F, 0x22])
    write_cmd(0x13)  # IPC
    write_data([0x00, 0x04])
    write_cmd(PLL)
    write_data(0x02)
    write_cmd(0x41)  # TSE
    write_data(0x00)
    write_cmd(CDI)
    write_data(0x3F)
    write_cmd(TCON)
    write_data([0x02, 0x00])
    write_cmd(TRES)
    write_data([0x03, 0x20, 0x01, 0xE0])
    write_cmd(VDCS)
    write_data(0x1E)
    write_cmd(T_VDCS)
    write_data(0x00)
    write_cmd(0x86)  # AGID
    write_data(0x00)
    write_cmd(PWS)
    write_data(0x2F)
    write_cmd(0xE0)  # CCSET
    write_data(0x00)
    write_cmd(0xE6)  # TSSET
    write_data(0x00)
    write_cmd(0x04)  # PWR ON
    time.sleep(0.1)
    wait_for_display()


def acep_color(color):
    write_cmd(0x10)
    for i in range(480):
        for _ in range(400):
            write_data(color)
    write_cmd(0x12)
    write_data(0x00)
    time.sleep(0.001)
    wait_for_display()


def display_sleep():
    write_cmd(0x02)
    write_data(0x00)
    wait_for_display()


def load_image_data(path):
    with open(path, 'rb') as f:
        image_data = f.read()
    return image_data


def write_bytes(bytes_data):
    set_cs(False)
    PIN_DC.value = True
    spi.write(bytes_data)
    set_cs(True)


def show_image_data(image_data):
    write_cmd(0x10)
    write_bytes(image_data)
    write_cmd(0x12)
    write_data(0x00)
    time.sleep(0.001)
    wait_for_display()


if __name__ == '__main__':

    folder = 'img'
    files = os.listdir(folder)
    file = random.choice(files)

    monitor = adafruit_max1704x.MAX17048(board.I2C())
    time.sleep(0.1)
    cell_percent = max(min(monitor.cell_percent, 100.0), 0.0)

    display_init()
    image_data = load_image_data(f'{folder}/{file}')

    battery_data_width = 400 - round(4 * cell_percent)
    battery_data = bytes([0x00] * battery_data_width)
    image_data = (image_data[:-1200] +
                battery_data + image_data[-1200 + battery_data_width:-800] +
                battery_data + image_data[-800 + battery_data_width:-400] +
                battery_data + image_data[-400 + battery_data_width:])

    show_image_data(image_data)
    display_sleep()

    # deep sleep
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 3600)
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)

