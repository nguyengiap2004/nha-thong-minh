import cv2
import numpy as np
import os

# Tạo model nhận diện khuôn mặt
recognizer = cv2.face.LBPHFaceRecognizer_create()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Đường dẫn dataset chứa các ảnh khuôn mặt
dataset_path = "dataset/"
images, labels = [], []
label_dict = {}  # Lưu thông tin ID của người dùng

user_id = 0
fixed_size = (200, 200)  # Kích thước cố định cho các ảnh

for user_folder in os.listdir(dataset_path):
    user_path = os.path.join(dataset_path, user_folder)
    
    if os.path.isdir(user_path):
        label_dict[user_id] = user_folder
        
        for img_name in os.listdir(user_path):
            img_path = os.path.join(user_path, img_name)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            # Resize ảnh về kích thước cố định
            img_resized = cv2.resize(img, fixed_size)
            images.append(img_resized)
            labels.append(user_id)
        
        user_id += 1

# Chuyển danh sách thành mảng NumPy đồng nhất
images = np.array(images, dtype='uint8')
labels = np.array(labels)

# Huấn luyện mô hình với dữ liệu đã thu thập
recognizer.train(images, labels)
recognizer.save("face_model.yml")  # Lưu model đã huấn luyện
print("Huấn luyện xong!")
