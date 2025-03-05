#include <SoftwareSerial.h>
#include <DHT.h>

// Khai báo chân kết nối cảm biến
#define DHTPIN 8         // Cảm biến DHT11 nối chân 8
#define DHTTYPE DHT11    // Loại cảm biến DHT11
#define LDR_PIN A1       // Cảm biến ánh sáng (LDR)
#define MQ2_PIN A2       // Cảm biến khí gas MQ-2
#define SOUND_PIN A3     // Cảm biến âm thanh KY-038

DHT dht(DHTPIN, DHTTYPE);  // Khởi tạo đối tượng DHT

// Giao tiếp Serial giữa Arduino UNO và ESP8266
SoftwareSerial espSerial(2, 3);  // RX, TX (D2 -> ESP TX, D3 -> ESP RX)

void setup() {
    Serial.begin(115200);  // Serial Monitor
    espSerial.begin(115200);  // Serial ESP8266

    dht.begin();  // Khởi động cảm biến DHT
    delay(2000);  // Chờ cảm biến ổn định
}

void loop() {
    // Đọc dữ liệu từ cảm biến DHT11
    float temp = dht.readTemperature();  // Nhiệt độ (°C)
    float hum = dht.readHumidity();      // Độ ẩm (%)
    
    // Kiểm tra nếu cảm biến DHT bị lỗi
    if (isnan(temp) || isnan(hum)) {
        Serial.println("⚠️ Lỗi khi đọc cảm biến DHT11!");
        return;
    }

    // Đọc dữ liệu từ các cảm biến khác
    int light = analogRead(LDR_PIN);   // Ánh sáng (0 - 1023)
    int gas = analogRead(MQ2_PIN);     // Khí gas (0 - 1023)
    int sound = analogRead(SOUND_PIN); // Âm thanh (0 - 1023)

    // Định dạng dữ liệu gửi qua Serial với dấu phẩy `,`
    String data = String(temp) + "," + String(hum) + "," + 
                  String(light) + "," + String(gas) + "," + String(sound);
    
    // Gửi dữ liệu đến ESP8266
    espSerial.println(data);
    Serial.println(data);

    delay(10000);  // Gửi dữ liệu mỗi 10 giây
}
