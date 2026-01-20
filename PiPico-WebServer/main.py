import network
import socket
import time
import os

SSID = "Tralalero"
PASSWORD = "187691234"

# ---------- WLAN ----------
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Verbinde mit WLAN...")
while not wlan.isconnected():
    time.sleep(0.5)

ip = wlan.ifconfig()[0]
print("IP-Adresse:", ip)

# ---------- SERVER ----------
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(1)

print("Webserver läuft")

# ---------- CONTENT TYPE ----------
def content_type(path):
    if path.endswith(".html"):
        return "text/html"
    if path.endswith(".png"):
        return "image/png"
    if path.endswith(".jpg") or path.endswith(".jpeg"):
        return "image/jpeg"
    if path.endswith(".css"):
        return "text/css"
    if path.endswith(".js"):
        return "application/javascript"
    return "text/plain"

# ---------- REQUEST LOOP ----------
while True:
    client, addr = server.accept()
    request = client.recv(1024)

    try:
        request = request.decode()
        path = request.split(" ")[1]
        if path == "/":
            path = "/index.html"

        filename = path.lstrip("/")

        with open(filename, "rb") as f:
            data = f.read()

        header = (
            "HTTP/1.0 200 OK\r\n"
            "Content-Type: %s\r\n"
            "Content-Length: %d\r\n"
            "Connection: close\r\n\r\n"
            % (content_type(filename), len(data))
        )

        client.send(header.encode())
        client.send(data)

    except Exception as e:
        client.send(
            b"HTTP/1.0 404 Not Found\r\nContent-Type: text/plain\r\n\r\nDatei nicht gefunden"
        )

    client.close()

