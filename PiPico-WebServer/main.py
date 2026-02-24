from machine import Pin, I2C, SPI
import uasyncio as asyncio
import network, time, math, json, os, _thread
import sdcard
import ubinascii, hashlib 

# ================= KONFIGURATION =================
SAMPLE_HZ = 100      # Messfrequenz
LOG_HZ = 20          # Schreibrate SD-Karte
WS_SEND_RATE_MS = 50 # Sende-Intervall (20 FPS)

LOG_FILE_NAME = "fahrt.csv"
MAX_FILE_NAME = "maxima.json"

# Globale Variablen
current_roll = 0.0
current_pitch = 0.0 # NEU: Für Brems-Kompensation
is_calibrating = True
off_gx, off_gy, off_gz = 0.0, 0.0, 0.0
off_ax, off_ay = 0.0, 0.0 

# SD-Karte Setup
storage_path = ""
try:
    cs = Pin(17, Pin.OUT, value=1)
    spi = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
    sd = sdcard.SDCard(spi, cs)
    vfs = os.VfsFat(sd)
    os.mount(vfs, "/sd")
    storage_path = "/sd"
    print("SD-Karte montiert.")
except:
    print("Keine SD-Karte. Nutze internen Speicher.")

# Daten-Management
data_lock = _thread.allocate_lock()
shared_json = "{}"
shared_data = {
    "ax": 0.0, "ay": 0.0, "roll": 0.0, 
    "calibrated": False,
    "max": {"ax": 0.0, "ay": 0.0, "roll_left": 0.0, "roll_right": 0.0}
}

def load_maxima():
    try:
        with open(f"{storage_path}/{MAX_FILE_NAME}", "r") as f: return json.load(f)
    except: return {"ax": 0.0, "ay": 0.0, "roll_left": 0.0, "roll_right": 0.0}
shared_data["max"] = load_maxima()

# WLAN 
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="MotoTelemetry", password="racinglines")
try: ap.config(pm=0xa11140) 
except: pass
ap.ifconfig(("192.168.4.1", "255.255.255.0", "192.168.4.1", "8.8.8.8"))
print(f"IP: {ap.ifconfig()[0]}")

# Sensor Setup
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
SCALE_FACTOR = 8192.0 # 4G

try: 
    i2c.writeto_mem(0x68, 0x6B, b'\x00') 
    i2c.writeto_mem(0x68, 0x1C, b'\x08') 
    print("Sensor OK (4G).")
except: 
    print("Sensor Fehler!")

def conv(msb, lsb):
    v = (msb << 8) | lsb
    return v - 65536 if v > 32767 else v

# --- KALIBRIERUNG ---
def calibrate_system():
    global off_gx, off_gy, off_gz, off_ax, off_ay, current_roll, current_pitch, is_calibrating
    is_calibrating = True
    print("Kalibrierung läuft...")
    samples = 200
    sgx, sgy, sgz = 0,0,0
    sax, say = 0,0 
    
    for _ in range(samples):
        try:
            b = i2c.readfrom_mem(0x68, 0x3B, 14)
            raw_s_x = conv(b[0], b[1])
            raw_s_y = conv(b[2], b[3])
            raw_s_z = conv(b[4], b[5]) 
            
            sgx += conv(b[8], b[9])
            sgy += conv(b[10], b[11])
            sgz += conv(b[12], b[13])
            
            # Y=Fahrtrichtung, X=Quer
            sax += raw_s_y 
            say += raw_s_x 
        except: pass
        time.sleep_ms(3)
        
    off_gx = sgx/samples
    off_gy = sgy/samples
    off_gz = sgz/samples
    
    # Offsets für 0-Punkt
    off_ax = (sax/samples) / SCALE_FACTOR
    off_ay = (say/samples) / SCALE_FACTOR
    
    # Start-Winkel setzen
    avg_x = raw_s_x / SCALE_FACTOR
    avg_y = raw_s_y / SCALE_FACTOR
    avg_z = raw_s_z / SCALE_FACTOR
    
    # Roll (um Y-Achse, basiert auf X und Z)
    current_roll = math.degrees(math.atan2(avg_x, avg_z))
    # Pitch (um X-Achse, basiert auf Y und Z)
    current_pitch = math.degrees(math.atan2(avg_y, avg_z))
    
    is_calibrating = False
    print("Kalibrierung fertig.")

# --- CORE 1: MESSUNG ---
def measurement_task():
    global current_roll, current_pitch, shared_json
    calibrate_system()
    last_ts = time.ticks_us()
    
    # CSV Header schreiben falls neu
    log_path = f"{storage_path}/{LOG_FILE_NAME}"
    if not f"{LOG_FILE_NAME}" in os.listdir(storage_path):
        try:
            with open(log_path, "w") as f: f.write("Time_ms,Ax,Ay,Roll,Pitch\n")
        except: pass

    try: log_file = open(log_path, "a")
    except: log_file = None
    
    loop_cnt = 0
    save_cnt = 0
    
    while True:
        loop_start = time.ticks_us()
        try:
            b = i2c.readfrom_mem(0x68, 0x3B, 14)
            
            # 1. Rohdaten
            phys_x = conv(b[0], b[1]) / SCALE_FACTOR
            phys_y = conv(b[2], b[3]) / SCALE_FACTOR
            phys_z = conv(b[4], b[5]) / SCALE_FACTOR
            
            # Gyro (X=Pitch, Y=Roll, Z=Yaw)
            # WICHTIG: Achsenmapping beachten!
            # Wenn Sensor-X zur Seite zeigt, ist Rotation um X = PITCH (Nicken)
            # Wenn Sensor-Y nach vorne zeigt, ist Rotation um Y = ROLL (Kippen)
            g_raw_x = (conv(b[8], b[9]) - off_gx) / 131.0   # Pitch Speed
            g_raw_y = (conv(b[10], b[11]) - off_gy) / 131.0 # Roll Speed
            
            # 2. Beschleunigung bereinigt um Offset
            raw_ax = phys_y - off_ax # Längs (Fahrt)
            raw_ay = phys_x - off_ay # Quer
            
            # 3. Zeit
            now = time.ticks_us()
            dt = time.ticks_diff(now, last_ts) / 1000000.0
            last_ts = now
            
            # 4. Filter ROLL (Kippen / Schräglage)
            # NEU: Wir nutzen sqrt(y^2 + z^2). Das verhindert, dass Nicken (Pitch) 
            # fälschlicherweise als Schräglage interpretiert wird.
            acc_roll = math.degrees(math.atan2(phys_x, math.sqrt(phys_y**2 + phys_z**2)))
            current_roll = 0.98 * (current_roll + g_raw_y * dt) + 0.02 * acc_roll
            
            # 5. Filter PITCH (Nicken / Bremsen)
            # NEU: Wir nutzen sqrt(x^2 + z^2). Das verhindert, dass Schräglage (Roll)
            # fälschlicherweise als Bremsung interpretiert wird (dein 1G Fehler).
            acc_pitch = math.degrees(math.atan2(phys_y, math.sqrt(phys_x**2 + phys_z**2)))
            current_pitch = 0.98 * (current_pitch + g_raw_x * dt) + 0.02 * acc_pitch
            
            # 6. Schwerkraft-Kompensation (Gravity Removal)
            # Wir ziehen den Anteil von 1G ab, der durch die Neigung entsteht.
            # Da die Winkel jetzt sauber getrennt sind, beeinflussen sie sich nicht mehr gegenseitig.
            
            # Querbeschleunigung bereinigen (Gravity-Anteil auf X abziehen)
            grav_share_x = math.sin(math.radians(current_roll))
            final_ay = phys_x - off_ay - grav_share_x
            
            # Längsbeschleunigung bereinigen (Gravity-Anteil auf Y abziehen)
            grav_share_y = math.sin(math.radians(current_pitch))
            final_ax = phys_y - off_ax - grav_share_y
            
            loop_cnt += 1
            if loop_cnt >= (SAMPLE_HZ // LOG_HZ):
                loop_cnt = 0
                with data_lock:
                    m = shared_data["max"]
                    if not is_calibrating:
                        m["ax"] = max(m["ax"], abs(final_ax))
                        m["ay"] = max(m["ay"], abs(final_ay))
                        if current_roll > 0: m["roll_right"] = max(m["roll_right"], current_roll)
                        else: m["roll_left"] = max(m["roll_left"], abs(current_roll))
                    
                    # Ax invertieren: Bremsen soll negativ sein für Anzeige? 
                    # Oder Positiv? Wir lassen es hier roh, das JS regelt die Richtung.
                    shared_data["ax"] = -final_ax # Minus damit Bremsen für G-Meter passt
                    shared_data["ay"] = final_ay
                    shared_data["roll"] = current_roll
                    shared_data["calibrated"] = not is_calibrating
                    shared_json = json.dumps(shared_data) 
                
                if log_file and not is_calibrating:
                    # CSV Format: ms, ax, ay, roll, pitch
                    log_file.write(f"{time.ticks_ms()},{final_ax:.2f},{final_ay:.2f},{current_roll:.1f},{current_pitch:.1f}\n")
                    save_cnt += 1
                    if save_cnt > 50: log_file.flush(); save_cnt = 0
                    
        except Exception as e: pass
        
        elapsed = time.ticks_diff(time.ticks_us(), loop_start)
        wait = (1000000 // SAMPLE_HZ) - elapsed
        if wait > 0: time.sleep_us(wait)

# --- WEBSOCKET TASK (SENDER) ---
async def send_frame(writer, data):
    try:
        msg = data.encode()
        length = len(msg)
        fmt = 0x81 
        if length <= 125: header = bytes([fmt, length])
        elif length <= 65535: header = bytes([fmt, 126, (length >> 8) & 255, length & 255])
        else: return 
        writer.write(header + msg)
        await writer.drain()
    except: pass

async def ws_sender(writer):
    global shared_json
    last_sent = ""
    while True:
        try:
            if shared_json != last_sent:
                await send_frame(writer, shared_json)
                last_sent = shared_json
            await asyncio.sleep_ms(WS_SEND_RATE_MS) 
        except: break

async def ws_handler(reader, writer):
    print("WS Verbunden")
    send_task = asyncio.create_task(ws_sender(writer))
    try:
        while True:
            header = await reader.read(2)
            if not header: break
            length = header[1] & 127
            if length == 126:
                l_bytes = await reader.read(2)
                length = (l_bytes[0] << 8) | l_bytes[1]
            mask = await reader.read(4)
            payload = await reader.read(length)
            
            decoded = bytearray(length)
            for i in range(length): decoded[i] = payload[i] ^ mask[i % 4]
            msg = decoded.decode()
            
            if "reset:" in msg:
                key = msg.split(":")[1]
                with data_lock:
                    if key == "all":
                        shared_data["max"] = {"ax": 0.0, "ay": 0.0, "roll_left": 0.0, "roll_right": 0.0}
                    elif key in shared_data["max"]:
                        shared_data["max"][key] = 0.0
    except: pass
    finally:
        send_task.cancel()
        try: writer.close(); await writer.wait_closed()
        except: pass

# --- HTTP SERVER & ROUTING ---
async def handle_client(reader, writer):
    try:
        req = (await reader.read(1024)).decode()
        
        # WEBSOCKET
        if "Upgrade: websocket" in req:
            key = req.split("Sec-WebSocket-Key: ")[1].split("\r\n")[0]
            acc = ubinascii.b2a_base64(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).strip()
            writer.write(b"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: " + acc + b"\r\n\r\n")
            await writer.drain()
            await ws_handler(reader, writer)
            return

        # CSV DOWNLOAD
        if "GET /download" in req:
            f_path = f"{storage_path}/{LOG_FILE_NAME}"
            try:
                # Größe ermitteln
                f_stat = os.stat(f_path)
                f_size = f_stat[6]
                
                writer.write(b"HTTP/1.0 200 OK\r\n")
                writer.write(b"Content-Type: text/csv\r\n")
                writer.write(f"Content-Disposition: attachment; filename={LOG_FILE_NAME}\r\n")
                writer.write(f"Content-Length: {f_size}\r\n\r\n")
                await writer.drain()
                
                # Datei in Stücken senden (RAM sparen)
                with open(f_path, "rb") as f:
                    while True:
                        chunk = f.read(1024)
                        if not chunk: break
                        writer.write(chunk)
                        await writer.drain()
            except:
                writer.write(b"HTTP/1.0 404 Not Found\r\n\r\nKeine Daten.")

        # CSV DELETE
        elif "GET /delete" in req:
            try:
                os.remove(f"{storage_path}/{LOG_FILE_NAME}")
                print("CSV geloescht.")
            except: pass
            # Redirect zur Startseite
            writer.write(b"HTTP/1.1 303 See Other\r\nLocation: /\r\n\r\n")

        # INDEX HTML
        elif "GET / " in req or "index.html" in req:
            try:
                with open("index.html", "rb") as f:
                    writer.write(b"HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
                    writer.write(f.read())
            except: writer.write(b"HTTP/1.0 404 Not Found\r\n\r\nindex.html fehlt!")
            
        else: writer.write(b"HTTP/1.0 404 Not Found\r\n\r\n")
            
        await writer.drain()
        writer.close()
        await writer.wait_closed()
    except: pass

async def main():
    _thread.start_new_thread(measurement_task, ())
    print("System gestartet.")
    server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
    while True: await asyncio.sleep(1)

try: asyncio.run(main())
except KeyboardInterrupt: pass
