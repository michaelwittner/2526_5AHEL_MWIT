from machine import Pin, I2C
import uasyncio as asyncio
import network, time, math, json, os, socket

# ================= WLAN =================
SSID = "Tralalero"
PASSWORD = "187691234"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    time.sleep(0.5)

print("IP:", wlan.ifconfig()[0])

# ================= MPU6050 =================
MPU_ADDR = 0x68
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
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

# ================= Maxima =================
max_vals = {
    "ax": 0.0,
    "ay": 0.0,
    "az": 0.0,
    "roll_left": 0.0,   # negativ
    "roll_right": 0.0,  # positiv
    "temp": 0.0
}

sensor_data = {"ax":0,"ay":0,"az":0,"roll":0,"temp":0}

# ================= Logging =================
log_interval = 0.05  # 20 Hz
last_log = time.ticks_ms()
try:
    log = open("fahrt.csv", "a")
except:
    log = open("fahrt.csv", "w")
    log.write("t,ax,ay,az,roll,temp\n")

start_time = time.ticks_ms()

# ================= Sensor Task =================
async def sensor_loop():
    global sensor_data, max_vals, last_log
    while True:
        ax, ay, az = accel_g()
        roll = roll_angle(ax, ay, az)
        temp = temperature()
        
        sensor_data.update({"ax":ax,"ay":ay,"az":az,"roll":roll,"temp":temp})
        
        # Maxima 200Hz
        max_vals["ax"] = max(max_vals["ax"], abs(ax))
        max_vals["ay"] = max(max_vals["ay"], abs(ay))
        max_vals["az"] = max(max_vals["az"], abs(az))
        if roll > 0:
            max_vals["roll_right"] = max(max_vals["roll_right"], roll)
        else:
            max_vals["roll_left"] = min(max_vals["roll_left"], roll)

        max_vals["temp"] = max(max_vals["temp"], temp)
        
        # Logging 20Hz
        now = time.ticks_ms()
        if time.ticks_diff(now, last_log) >= log_interval*1000:
            t = time.ticks_diff(now, start_time)
            log.write("{},{:.3f},{:.3f},{:.3f},{:.2f},{:.2f}\n".format(
                t, ax, ay, az, roll, temp))
            log.flush()
            last_log = now
        
        await asyncio.sleep_ms(1)  # ~200 Hz

# ================= Webserver Task =================
async def handle_client(reader, writer):
    try:
        request_line = await reader.readline()
        if not request_line:
            await writer.aclose()
            return
        request = request_line.decode()
        
        # Read and ignore rest of headers
        while True:
            h = await reader.readline()
            if h == b"\r\n" or h == b"": break

        if "/data" in request:
            payload_dict = sensor_data.copy()  # erst sensor_data kopieren
            payload_dict["max"] = max_vals     # dann max_vals einfügen
            payload = json.dumps(payload_dict)

            await writer.awrite("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
            await writer.awrite(payload)

        elif "/reset" in request:
            if "roll_left" in request:
                max_vals["roll_left"] = 0.0
            elif "roll_right" in request:
                max_vals["roll_right"] = 0.0
            elif "roll" in request:
                max_vals["roll_left"] = 0.0
                max_vals["roll_right"] = 0.0
            elif "ax" in request:
                max_vals["ax"] = 0.0
            elif "ay" in request:
                max_vals["ay"] = 0.0
            elif "az" in request:
                max_vals["az"] = 0.0
            elif "temp" in request:
                max_vals["temp"] = 0.0

            await writer.awrite("HTTP/1.1 200 OK\r\n\r\nOK")

        else:
            if "index.html" in os.listdir():
                with open("index.html") as f:
                    html = f.read()
                await writer.awrite("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
                await writer.awrite(html)
            else:
                await writer.awrite("HTTP/1.1 404 Not Found\r\n\r\nPage not found")

    except Exception as e:
        print("Client error:", e)

    await writer.aclose()

async def http_server():
    server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
    print("Webserver läuft")
    await server.wait_closed()

# ================= Main =================
async def main():
    await asyncio.gather(sensor_loop(), http_server())

asyncio.run(main())
