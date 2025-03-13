import cv2
import os

# Load model nhận diện khuôn mặt
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Kết nối camera (điều chỉnh index nếu cần; với DroidCam có thể dùng URL nếu hỗ trợ)
cap = cv2.VideoCapture(0)  # hoặc thay thành URL stream từ DroidCam

if not cap.isOpened():
    print("Không mở được camera. Kiểm tra lại kết nối hoặc thiết lập camera.")
    exit()

# Chụp 1 khung hình duy nhất
ret, frame = cap.read()
if not ret:
    print("Không lấy được khung hình từ camera.")
    cap.release()
    exit()

# Chuyển ảnh sang màu xám để phát hiện khuôn mặt
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

if len(faces) == 0:
    print("Không phát hiện được khuôn mặt.")
else:
    # Chọn khuôn mặt đầu tiên phát hiện được
    (x, y, w, h) = faces[0]
    face_crop = gray[y:y+h, x:x+w]
    
    # Nhập ID người dùng và tạo thư mục lưu ảnh
    user_id = input("Nhập ID người dùng: ")
    dataset_path = f"dataset/user_{user_id}"
    os.makedirs(dataset_path, exist_ok=True)
    
    # Lưu ảnh khuôn mặt
    file_name = f"{dataset_path}/img_0.jpg"
    cv2.imwrite(file_name, face_crop)
    print(f"Đã lưu ảnh khuôn mặt tại: {file_name}")
    
    # Hiển thị ảnh đã chụp kèm khuôn mặt được phát hiện
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.imshow("Captured Face", frame)
    cv2.waitKey(0)  # Chờ phím bất kỳ để đóng cửa sổ

cap.release()
cv2.destroyAllWindows()



# import cv2
# import os
# import time

# # Đặt URL DroidCam cố định
# droidcam_url = "http://192.168.193.109:8080/video"

# # Hỏi người dùng về ID
# user_id = input("Nhập ID người dùng: ")

# # Kết nối camera DroidCam
# cap = cv2.VideoCapture(droidcam_url)

# if not cap.isOpened():
#     print("Không mở được camera. Kiểm tra lại kết nối với DroidCam.")
#     exit()

# # Load model nhận diện khuôn mặt
# face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# # Tạo thư mục lưu ảnh nếu chưa có
# dataset_path = f"dataset/user_{user_id}"
# os.makedirs(dataset_path, exist_ok=True)

# # Tìm số thứ tự ảnh lớn nhất đã có để tiếp tục lưu không bị ghi đè
# existing_images = [int(f.split('_')[-1].split('.')[0]) for f in os.listdir(dataset_path) if f.startswith("img_") and f.endswith(".jpg")]
# image_count = max(existing_images) + 1 if existing_images else 0

# print("Chương trình đang chạy... Nhấn 'q' để thoát.")

# # Biến để kiểm soát thời gian giữa các lần chụp ảnh
# last_capture_time = time.time()
# capture_interval = 2  # Chụp ảnh mỗi 2 giây

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Không lấy được khung hình từ DroidCam.")
#         break

#     # Chuyển sang ảnh xám để nhận diện khuôn mặt
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

#     for (x, y, w, h) in faces:
#         cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

#     # Hiển thị khung hình
#     cv2.imshow("Capture Face", frame)

#     # Tự động lưu ảnh nếu phát hiện khuôn mặt và đủ thời gian giữa các lần chụp
#     if len(faces) > 0 and time.time() - last_capture_time >= capture_interval:
#         (x, y, w, h) = faces[0]
#         face_crop = gray[y:y+h, x:x+w]

#         file_name = f"{dataset_path}/img_{image_count}.jpg"
#         cv2.imwrite(file_name, face_crop)
#         print(f"Đã lưu ảnh: {file_name}")

#         image_count += 1  # Tăng số thứ tự ảnh tiếp theo
#         last_capture_time = time.time()  # Cập nhật thời gian chụp cuối cùng

#     # Kiểm tra phím nhấn để thoát chương trình
#     key = cv2.waitKey(1) & 0xFF
#     if key == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()
