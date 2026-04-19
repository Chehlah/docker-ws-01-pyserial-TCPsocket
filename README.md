# Serial Bridge + Real-time Plot

รับข้อมูลจาก Arduino ผ่าน Serial บนเครื่อง Host ส่งเข้า Docker Container แปลงข้อมูล แล้วแสดงผลเป็นกราฟ Real-time

---

## Architecture

```
[Arduino]
    │ Serial /dev/cu.usbmodem101
    ▼
[Host] bridge_readplot.py  ──────────────────────────────► กราฟ (host)
    │ TCP port 7777
    ▼
[Container] read_plot.py  (กลับเครื่องหมายค่า)
    │ TCP port 7778
    ▼
[Host] bridge_mathplot.py  ──────────────────────────────► กราฟ (host)
```

---

## ไฟล์และหน้าที่

### `bridge_plot.py`
รับข้อมูล Serial จาก Arduino แล้วส่งต่อให้ Container ผ่าน TCP port 7777 (ไม่มีกราฟ)

- รันบน: **Host**
- รับข้อมูลจาก: Arduino Serial `/dev/cu.usbmodem101`
- ส่งข้อมูลไปยัง: Container port `7777`

---

### `bridge_readplot.py`
เหมือน `bridge_plot.py` แต่เพิ่มการแสดงกราฟ Real-time บน Host ด้วย

- รันบน: **Host**
- รับข้อมูลจาก: Arduino Serial `/dev/cu.usbmodem101`
- ส่งข้อมูลไปยัง: Container port `7777`
- แสดงผล: กราฟ Real-time บนหน้าจอ Host

---

### `read_plot.py`
รับข้อมูลจาก Bridge กลับเครื่องหมายค่า (บวก↔ลบ) แล้วส่งต่อให้ผู้เชื่อมต่อผ่าน port 7778

- รันบน: **Container**
- รับข้อมูลจาก: Host port `7777` (`host.docker.internal:7777`)
- ส่งข้อมูลไปยัง: ผู้เชื่อมต่อ port `7778` (รองรับหลาย client)
- แปลงข้อมูล: กลับเครื่องหมายทุกค่า เช่น `3.5` → `-3.5`

---

### `bridge_mathplot.py`
รับข้อมูลจาก Container port 7778 แล้วแสดงเป็นกราฟ Real-time บน Host

- รันบน: **Host**
- รับข้อมูลจาก: Container port `7778` (`localhost:7778`)
- แสดงผล: กราฟ Real-time บนหน้าจอ Host

---

## Container

### Dockerfile
- Base image: `ubuntu:20.04`
- ติดตั้ง: `python3`, `python3-pip`, `python3-tk`
- Working directory: `/py_ws` (mount จากภายนอก, เปลี่ยยชื่อตามชอบ)

### requirements.txt
```
pyserial
matplotlib
```

### Build Image
```bash
docker build -t serial-bridge .  # directory name = image name
```

### รัน Container
```bash
docker run -it \
  -p 7778:7778 \
  -v $(pwd):/py_ws \
  --name serial-bridge \
  serial-bridge bash
```

| Flag | ความหมาย |
|------|----------|
| `-p 7778:7778` | expose port 7778 ออกมาให้ Host เชื่อมต่อได้ |
| `-v $(pwd):/py_ws` | mount โฟลเดอร์ปัจจุบันเข้าไปใน container |
| `--name serial-bridge` | ตั้งชื่อ container |

---

## การติดตั้ง (Host)

```bash
pip3 install pyserial matplotlib
```

---

## วิธีใช้งาน

### รูปแบบที่ 1 — Bridge + กราฟที่ Host (ไม่ใช้ Container)

```bash
python3 bridge_readplot.py
```

---

### รูปแบบที่ 2 — Full Pipeline (Host → Container → Host)

**ขั้นตอนที่ 1** รัน bridge บน Host ก่อน:
```bash
python3 bridge_readplot.py
```

**ขั้นตอนที่ 2** รัน Container พร้อม expose port 7778:
```bash
docker run -it -p 7778:7778 -v $(pwd):/py_ws serial-bridge bash
```

**ขั้นตอนที่ 3** รัน read_plot.py ใน Container:
```bash
cd /py_ws && python3 read_plot.py
```

**ขั้นตอนที่ 4** รัน bridge_mathplot.py บน Host เพื่อดูกราฟจาก Container:
```bash
python3 bridge_mathplot.py
```

---

## Port Summary

| Port | ทิศทาง | ใช้โดย |
|------|--------|--------|
| `7777` | Host → Container | `bridge_readplot.py` / `bridge_plot.py` ส่ง, `read_plot.py` รับ |
| `7778` | Container → Host | `read_plot.py` ส่ง, `bridge_mathplot.py` รับ |

---

## รูปแบบข้อมูล

ข้อมูลที่รับส่งเป็น plain text ต่อบรรทัด รองรับทั้งค่าเดียวและหลาย channel:

```
# ค่าเดียว
42.5

# หลาย channel คั่นด้วย comma
1.2,3.4,5.6
```

กราฟจะแสดงเส้นแยกแต่ละ channel โดยอัตโนมัติ (`ch1`, `ch2`, `ch3`, ...)
