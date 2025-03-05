from flask import Flask, render_template, jsonify
import requests
import csv
import time
import threading
import pandas as pd

app = Flask(__name__)
DWEET_URL = "https://dweet.io/get/latest/dweet/for/my_esp8266_sensor"
CSV_FILE = "sensor_data.csv"

# Hàm lưu dữ liệu vào file CSV
def save_to_csv(timestamp, data):
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp] + data)

# Hàm cập nhật dữ liệu từ Dweet.io mỗi 10 giây
def update_data():
    while True:
        try:
            response = requests.get(DWEET_URL)
            if response.status_code == 200:
                dweet_data = response.json()

                if "with" in dweet_data and len(dweet_data["with"]) > 0:
                    for entry in dweet_data["with"]:
                        timestamp = entry["created"]
                        sensor_values = entry['content'].get('sensorData', [])

                        if isinstance(sensor_values, list) and len(sensor_values) == 5:
                            save_to_csv(timestamp, sensor_values)
                            print("📥 Dữ liệu lưu:", sensor_values)
                        else:
                            print("⚠ Dữ liệu không hợp lệ:", sensor_values)
                else:
                    print("❌ API không chứa dữ liệu hợp lệ!")

            else:
                print(f"❌ Lỗi HTTP {response.status_code} khi truy cập Dweet.io")

        except Exception as e:
            print("❌ Lỗi khi lấy dữ liệu:", e)

        time.sleep(10)  # Chờ 10 giây trước khi lấy dữ liệu tiếp theo

# Tạo file CSV nếu chưa có
with open(CSV_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Temperature", "Humidity", "Light", "Gas", "Sound"])

# Chạy luồng lấy dữ liệu từ Dweet.io
threading.Thread(target=update_data, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    try:
        df = pd.read_csv(CSV_FILE)
        data = df.tail(50).to_dict(orient='records')  # Lấy 50 dòng gần nhất
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
