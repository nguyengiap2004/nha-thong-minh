#include <ESP8266WiFi.h>

// WiFi & IoT Cloud
const char* ssid = "phongbat";
const char* password = "12345678";
const char* thingName = "my_esp8266_sensor";  // Tên trên Dweet.io

void setup() {
    Serial.begin(115200); // Sử dụng Serial chính của ESP8266

    // Kết nối WiFi
    WiFi.begin(ssid, password);
    Serial.print("\U0001F504 Đang kết nối WiFi...");
    int timeout = 0;
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
        timeout++;
        if (timeout > 20) {  // Nếu quá 20 giây không kết nối, reset ESP8266
            Serial.println("\n\u274C Không thể kết nối WiFi. Reset lại ESP8266.");
            ESP.restart();
        }
    }
    Serial.println("\n\u2705 Đã kết nối WiFi!");
    Serial.print("\U0001F4F6 Địa chỉ IP: ");
    Serial.println(WiFi.localIP());
}

void loop() {
    if (Serial.available()) {
        String receivedData = Serial.readStringUntil('\n');  // Nhận dữ liệu từ Arduino
        receivedData.trim();
        
        if (receivedData.length() > 0) {
            Serial.println("\U0001F4E5 Dữ liệu nhận: " + receivedData);
            
            // Loại bỏ các ký tự không mong muốn
            receivedData.replace("📡 Gửi dữ liệu: ", "");
            
            // Gửi dữ liệu lên Dweet.io dạng JSON
            sendDataToDweet(receivedData);
        }
    }
    delay(10000);  // Gửi dữ liệu mỗi 10 giây
}

// Gửi dữ liệu lên Dweet.io dạng JSON
void sendDataToDweet(String sensorData) {
    WiFiClient client;
    if (client.connect("dweet.io", 80)) {
        String jsonPayload = "{\"sensorData\": [" + sensorData + "]}";
        String url = "/dweet/for/";
        url += thingName;

        client.print(String("POST ") + url + " HTTP/1.1\r\n" +
                     "Host: dweet.io\r\n" +
                     "Content-Type: application/json\r\n" +
                     "Content-Length: " + jsonPayload.length() + "\r\n" +
                     "Connection: close\r\n\r\n" +
                     jsonPayload);
        Serial.println("Gửi dữ liệu JSON lên Dweet.io: " + jsonPayload);
        delay(1000);
        client.stop();
    } else {
        Serial.println("\u274C Lỗi kết nối Dweet.io");
    }
}