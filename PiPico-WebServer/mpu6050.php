from machine import I2C, Pin
import time
import math

MPU_ADDR = 0x68

i2c = I2C(0, scl=Pin(1), sda=Pin(0))

# MPU-6050 aufwecken
i2c.writeto_mem(MPU_ADDR, 0x6B, b'\x00')
time.sleep(0.1)

def read_word(reg):
    high = i2c.readfrom_mem(MPU_ADDR, reg, 1)[0]
    low = i2c.readfrom_mem(MPU_ADDR, reg + 1, 1)[0]
    value = (high << 8) | low
    if value > 32767:
        value -= 65536
    return value

def accel_g():
    ax = read_word(0x3B) / 16384
    ay = read_word(0x3D) / 16384
    az = read_word(0x3F) / 16384
    return ax, ay, az

def temperature():
    raw = read_word(0x41)
    return (raw / 340.0) + 36.53

def roll_angle(ax, ay, az):
    return math.degrees(math.atan2(ax, math.sqrt(ay*ay + az*az)))

# ===== Ausgabe =====
while True:
    ax, ay, az = accel_g()
    roll = roll_angle(ax, ay, az)
    temp = temperature()

    print("Beschleunigung:")
    print("  Links / Rechts (X): {:.2f} g".format(ax))
    print("  Vor / Zurück  (Y): {:.2f} g".format(ay))
    print("  Oben / Unten  (Z): {:.2f} g".format(az))

    print("Neigung:")
    print("  Links / Rechts (Roll): {:.1f} °".format(roll))

    print("Temperatur:")
    print("  {:.1f} °C".format(temp))

    print("-" * 40)
    time.sleep(1)

