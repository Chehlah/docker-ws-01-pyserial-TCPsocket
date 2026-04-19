
import serial
import socket

ser = serial.Serial('/dev/cu.usbmodem101', 9600, timeout=1)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 7777))
server.listen(1)
print('รอ container เชื่อมต่อ...')
conn, addr = server.accept()
print('เชื่อมต่อแล้วจาก', addr)
while True:
    data = ser.readline()
    if data:
        print('ส่งข้อมูล:', data)
        conn.sendall(data)