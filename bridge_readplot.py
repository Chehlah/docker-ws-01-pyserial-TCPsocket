import serial
import socket
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

SERIAL_PORT = '/dev/cu.usbmodem101'
BAUD = 9600
LISTEN_PORT = 7777
MAX_POINTS = 100

ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', LISTEN_PORT))
server.listen(1)
print(f'รอ container เชื่อมต่อที่ port {LISTEN_PORT}...')
conn, addr = server.accept()
print('เชื่อมต่อแล้วจาก', addr)

data_queues = {}
lock = threading.Lock()

def serial_loop():
    while True:
        raw = ser.readline()
        if not raw:
            continue

        print('ส่งข้อมูล:', raw)
        try:
            conn.sendall(raw)
        except Exception as e:
            print('socket error:', e)
            break

        line = raw.decode('utf-8', errors='replace').strip()
        parts = line.split(',')
        try:
            values = [float(p) for p in parts]
        except ValueError:
            continue

        with lock:
            for i, val in enumerate(values):
                key = f'ch{i+1}' if len(values) > 1 else 'value'
                if key not in data_queues:
                    data_queues[key] = deque(maxlen=MAX_POINTS)
                data_queues[key].append(val)

threading.Thread(target=serial_loop, daemon=True).start()

fig, ax = plt.subplots()
ax.set_title('Real-time Serial Data')
ax.set_xlabel('Sample')
ax.set_ylabel('Value')
lines = {}

def update(_):
    with lock:
        for key, q in data_queues.items():
            if key not in lines:
                lines[key], = ax.plot([], [], label=key)
                ax.legend()
            y = list(q)
            lines[key].set_data(range(len(y)), y)

        if data_queues:
            all_vals = [v for q in data_queues.values() for v in q]
            if all_vals:
                margin = (max(all_vals) - min(all_vals)) * 0.1 or 1
                ax.set_ylim(min(all_vals) - margin, max(all_vals) + margin)
                ax.set_xlim(0, MAX_POINTS)

    return lines.values()

ani = animation.FuncAnimation(fig, update, interval=50, blit=False, cache_frame_data=False)
plt.tight_layout()
plt.show()

conn.close()
server.close()
ser.close()
