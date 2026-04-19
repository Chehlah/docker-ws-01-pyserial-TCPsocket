import socket
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

HOST = 'localhost'
PORT = 7778
MAX_POINTS = 100

conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect((HOST, PORT))
conn.setblocking(False)
print(f'เชื่อมต่อกับ container port {PORT} สำเร็จ')

buffer = ''
data_queues = {}
lock = threading.Lock()

def read_socket():
    global buffer
    try:
        chunk = conn.recv(1024).decode('utf-8', errors='replace')
        if not chunk:
            return False
        buffer += chunk
    except BlockingIOError:
        pass
    except Exception as e:
        print('connection error:', e)
        return False
    return True

fig, ax = plt.subplots()
ax.set_title('Real-time Data from Container')
ax.set_xlabel('Sample')
ax.set_ylabel('Value')
lines = {}

def update(_):
    global buffer

    if not read_socket():
        return lines.values()

    with lock:
        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            line = line.strip()
            if not line:
                continue

            parts = line.split(',')
            try:
                values = [float(p) for p in parts]
            except ValueError:
                continue

            for i, val in enumerate(values):
                key = f'ch{i+1}' if len(values) > 1 else 'value'
                if key not in data_queues:
                    data_queues[key] = deque(maxlen=MAX_POINTS)
                    lines[key], = ax.plot([], [], label=key)
                    ax.legend()
                data_queues[key].append(val)

    for key, q in data_queues.items():
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
