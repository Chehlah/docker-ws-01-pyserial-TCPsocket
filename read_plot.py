import socket
import threading

RECV_HOST = 'host.docker.internal'
RECV_PORT = 7777
SEND_PORT = 7778

# server สำหรับส่งข้อมูลออก
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', SEND_PORT))
server.listen(5)
print(f'รอการเชื่อมต่อขาออกที่ port {SEND_PORT}...')

subscribers = []
subscribers_lock = threading.Lock()

def accept_clients():
    while True:
        conn, addr = server.accept()
        with subscribers_lock:
            subscribers.append(conn)
        print(f'มีผู้เชื่อมต่อขาออก: {addr}')

threading.Thread(target=accept_clients, daemon=True).start()

# รับข้อมูลจาก bridge
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((RECV_HOST, RECV_PORT))
print('เชื่อมต่อกับ bridge สำเร็จ')

while True:
    data = client.recv(1024)
    if not data:
        print('การเชื่อมต่อถูกปิด')
        break

    line = data.decode('utf-8', errors='replace').strip()
    parts = line.split(',')
    try:
        values = [-float(p) for p in parts]
        out_line = ','.join(str(v) for v in values)
        # print('รับข้อมูล:', out_line)
    except ValueError:
        out_line = line
        # print('รับข้อมูล:', line)

    with subscribers_lock:
        dead = []
        for conn in subscribers:
            try:
                conn.sendall((out_line + '\n').encode())
            except Exception:
                dead.append(conn)
        for conn in dead:
            subscribers.remove(conn)
