#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>

#define SS_PIN 10
#define RST_PIN 9
#define SERVO_PIN 6
#define BLOCK_NUM 4  // Block lưu mật khẩu

MFRC522 mfrc522(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key;
Servo doorServo;

bool doorOpen = false; // Trạng thái cửa
unsigned long openTime = 0; // Lưu thời gian cửa mở
byte lastUID[4];       // Lưu UID của thẻ mở cửa

void setup() {
    Serial.begin(9600);
    SPI.begin();
    mfrc522.PCD_Init();
    doorServo.attach(SERVO_PIN);
    doorServo.write(0);  // Cửa đóng ban đầu

    for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;

    Serial.println("🔄 Đặt thẻ gần đầu đọc...");
}

void loop() {
    if (!mfrc522.PICC_IsNewCardPresent()) {
        // Nếu cửa đã mở, kiểm tra thời gian để tự đóng
        if (doorOpen && millis() - openTime >= 60000) { // 2 phút = 120000 ms
            Serial.println("⏳ Hết thời gian! Đóng cửa tự động...");
            doorServo.write(0);
            doorOpen = false;
        }
        return;
    }

    if (!mfrc522.PICC_ReadCardSerial()) return;

    Serial.println("✅ Thẻ được nhận diện!");

    // Đọc UID thẻ
    byte currentUID[4];
    for (byte i = 0; i < 4; i++) {
        currentUID[i] = mfrc522.uid.uidByte[i];
    }

    byte buffer[18];
    byte size = sizeof(buffer);

    MFRC522::StatusCode status = mfrc522.PCD_Authenticate(
        MFRC522::PICC_CMD_MF_AUTH_KEY_A, BLOCK_NUM, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
        Serial.print("❌ Lỗi xác thực: ");
        Serial.println(mfrc522.GetStatusCodeName(status));
        return;
    }

    status = mfrc522.MIFARE_Read(BLOCK_NUM, buffer, &size);
    if (status != MFRC522::STATUS_OK) {
        Serial.print("❌ Lỗi đọc: ");
        Serial.println(mfrc522.GetStatusCodeName(status));
        return;
    }

    Serial.print("📄 Dữ liệu đọc được: ");
    String cardData = "";
    for (byte i = 0; i < 16; i++) {
        Serial.write(buffer[i]);
        cardData += (char)buffer[i];
    }
    Serial.println();

    if (!doorOpen) {
        // Nếu cửa đang đóng, kiểm tra mật khẩu để mở cửa
        if (cardData.indexOf("Hello RFID!") >= 0) {
            Serial.println("🔓 Mật khẩu đúng! Mở cửa...");
            doorServo.write(90);
            doorOpen = true;
            openTime = millis(); // Ghi nhận thời gian mở cửa

            // Lưu lại UID của thẻ mở cửa
            for (byte i = 0; i < 4; i++) {
                lastUID[i] = currentUID[i];
            }
        } else {
            Serial.println("❌ Mật khẩu sai! Không mở cửa.");
        }
    } else {
        // Nếu cửa đang mở, kiểm tra nếu đúng thẻ mở cửa thì đóng lại
        bool sameCard = true;
        for (byte i = 0; i < 4; i++) {
            if (currentUID[i] != lastUID[i]) {
                sameCard = false;
                break;
            }
        }

        if (sameCard) {
            Serial.println("🔒 Quét lại thẻ! Đóng cửa...");
            doorServo.write(0);
            doorOpen = false;
        } else {
            Serial.println("⚠ Không phải thẻ đã mở cửa! Không đóng.");
        }
    }

    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
}
