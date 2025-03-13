
import cv2
import serial
import threading
import time
import requests
from flask import Flask, render_template_string, request, jsonify

# --- CẤU HÌNH Pushover ---
PUSHOVER_USER_KEY = "ukiakn1dh7fp8z7y3gmmyx82egpgq4"
PUSHOVER_API_TOKEN = "abwcwnpgqkwa51pyy1j6a1yf3y8t1j"

# --- CẤU HÌNH SERIAL CHO ARDUINO ---
ser = serial.Serial('COM8', 9600, timeout=1)
time.sleep(2)  # Chờ Arduino khởi động

# --- KHỞI TẠO FLASK APP ---
app = Flask(__name__)

# Biến toàn cục lưu trạng thái cửa và cảnh báo gas
servo_open = False
gas_detected = False

def send_pushover_notification(message):
    """Gửi tin nhắn cảnh báo qua Pushover"""
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": message,
        "title": "🚨 CẢNH BÁO GAS 🚨"
    }
    requests.post(url, data=data)

@app.route('/')
def index():
    return render_template_string('''
        <!doctype html>
        <html>
        <head>
            <title>Quản lý cửa</title>
            <script>
                function toggleServo() {
                    fetch('/toggle', { method: 'POST' })
                        .then(response => response.json())
                        .then(data => updateUI(data.status));
                }

                function updateUI(status) {
                    document.getElementById("servo-status").innerText = status;
                    let btn = document.getElementById("toggle-btn");
                    btn.innerText = status === "Mở" ? "Đóng cửa" : "Mở cửa";
                }

                function checkStatus() {
                    fetch('/status')
                        .then(response => response.json())
                        .then(data => updateUI(data.status));
                }

                setInterval(checkStatus, 2000);
            </script>
        </head>
        <style>
            body {
            text-align: center;
            }
            button {
            font-size: 18px;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            color: black;
            transition: 0.3s;
        }
        
        </style>
        <body>
            <h1>Điều khiển cửa nhà</h1>
            <p>Trạng thái cửa nhà: <span id="servo-status">{{ status }}</span></p>
            <button id="toggle-btn" onclick="toggleServo()">
                {% if status == 'Mở' %} Đóng cửa {% else %} Mở cửa {% endif %}
            </button>
        </body>
        </html>
    ''', status="Mở" if servo_open else "Đóng")

@app.route('/toggle', methods=['POST'])
def toggle_servo():
    global servo_open
    if servo_open:
        ser.write(b'0')  # Đóng cửa
        servo_open = False
    else:
        ser.write(b'1')  # Mở cửa
        servo_open = True
    return jsonify({"status": "Mở" if servo_open else "Đóng"})

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({"status": "Mở" if servo_open else "Đóng"})

@app.route('/update_status', methods=['POST'])
def update_status():
    """Cập nhật trạng thái cửa mà không kích hoạt toggle"""
    global servo_open
    data = request.get_json()
    servo_open = data.get("status") == "Mở"
    return jsonify({"status": "Mở" if servo_open else "Đóng"})

def listen_arduino():
    """Lắng nghe tín hiệu từ Arduino"""
    global gas_detected
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print("Arduino:", line)
            
            if line == "GAS_DETECTED":
                if not gas_detected:
                    gas_detected = True
                    print("⚠️ CẢNH BÁO: Phát hiện khí gas! Gửi tin nhắn...")
                    send_pushover_notification("⚠️ CẢNH BÁO: Phát hiện khí gas nguy hiểm! Hãy kiểm tra ngay.")
            elif line == "GAS_CLEARED":
                gas_detected = False
                print("✅ Không còn khí gas.")

def face_recognition_loop():
    """Nhận diện khuôn mặt để điều khiển servo"""
    global servo_open

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("face_model.yml")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Không lấy được khung hình từ camera.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        for (x, y, w, h) in faces:
            face_crop = gray[y:y+h, x:x+w]
            label, confidence = recognizer.predict(face_crop)

            if confidence < 50:
                if not servo_open:
                    print("Khuôn mặt hợp lệ! Mở cửa.")
                    ser.write(b'1')
                    servo_open = True
                    requests.post('http://127.0.0.1:5000/update_status', json={"status": "Mở"})

                break  # Thoát loop sau khi nhận diện thành công

        for (x, y, w, h) in faces:
            color = (0, 255, 0) if servo_open else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

        cv2.imshow("Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # Khởi động Flask trong luồng riêng
    flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False}, daemon=True)
    flask_thread.start()

    # Khởi động luồng lắng nghe Arduino
    arduino_thread = threading.Thread(target=listen_arduino, daemon=True)
    arduino_thread.start()

    # Chạy nhận diện khuôn mặt
    face_recognition_loop()

    # Đóng Serial khi thoát
    ser.close()

