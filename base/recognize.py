import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math
import time
import pyttsx3  # Thêm thư viện pyttsx3 để chuyển văn bản thành giọng nói
from nltk.tokenize import word_tokenize
from nltk import pos_tag

# Tải mô hình và nhãn
detector = HandDetector(maxHands=1)  # Sử dụng detector cho 1 bàn tay
classifier = Classifier("base/model/asl_model_ct.h5", "base/model/labels.txt")  # Mô hình và nhãn
offset = 20  # Độ lệch để vẽ vùng chứa tay
imgSize = 300  # Thay đổi kích thước ảnh đầu vào cho mô hình (298x298)
labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
          'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'Next']

# Biến lưu trữ ký tự nhận diện
detected_text = []
sentence = ""  # Biến lưu trữ câu nhận diện
last_detection_time = time.time()  # Lưu thời gian nhận diện ký tự lần cuối
detection_timeout = 2  # Thời gian chờ giữa các ký tự (1.5 giây)
threshold = 0.4 # Ngưỡng xác suất để chấp nhận dự đoán

# Khởi tạo pyttsx3 cho việc phát âm
engine = pyttsx3.init()

# Danh sách từ/cụm từ gợi ý (có thể thay đổi tùy vào ngữ cảnh ứng dụng)
suggestions = {
    'A': ['Apple', 'Animal', 'Ask', 'Art', 'Ant'],
    'B': ['Ball', 'Banana', 'Bicycle', 'Bottle', 'Bird'],
    'C': ['Cat', 'Car', 'Camera', 'Cup', 'Clock'],
}

# Hàm xử lý văn bản, ví dụ: tách từ và phân tích ngữ pháp
def nlp_process(text):
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)  # Phân tích từ loại
    return ' '.join(tokens)  # Trả về câu sau khi xử lý

def recognize_sign_language(img):
    global detected_text, sentence, last_detection_time, detection_timeout, engine

    imgOutput = img.copy()  # Tạo bản sao của ảnh để vẽ
    hands, img = detector.findHands(img)  # Phát hiện bàn tay

    if hands:
        hand = hands[0]  # Lấy thông tin bàn tay đầu tiên
        x, y, w, h = hand['bbox']  # Tọa độ của bounding box
        imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255  # Tạo ảnh trắng để chứa bàn tay đã crop
        imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]  # Crop bàn tay từ ảnh
        imgCropShape = imgCrop.shape
        aspectRatio = h / w  # Tính tỷ lệ của ảnh crop

        if aspectRatio > 1:  # Nếu chiều cao lớn hơn chiều rộng
            k = imgSize / h
            wCal = math.ceil(k * w)  # Tính lại chiều rộng
            imgResize = cv2.resize(imgCrop, (wCal, imgSize))  # Resize ảnh crop theo chiều rộng
            wGap = math.ceil((imgSize - wCal) / 2)  # Tính độ lệch để căn giữa
            imgWhite[:, wGap:wCal + wGap] = imgResize  # Gắn ảnh resize vào ảnh trắng

        else:  # Nếu chiều rộng lớn hơn chiều cao
            k = imgSize / w
            hCal = math.ceil(k * h)  # Tính lại chiều cao
            imgResize = cv2.resize(imgCrop, (imgSize, hCal))  # Resize ảnh crop theo chiều cao
            hGap = math.ceil((imgSize - hCal) / 2)  # Tính độ lệch để căn giữa
            imgWhite[hGap:hCal + hGap, :] = imgResize  # Gắn ảnh resize vào ảnh trắng

        # Đảm bảo ảnh có kích thước đúng trước khi đưa vào mô hình
        imgWhite = cv2.resize(imgWhite, (imgSize, imgSize))  # Resize ảnh đầu vào của mô hình

        # Dự đoán nhãn
        prediction, index = classifier.getPrediction(imgWhite, draw=False)
        confidence = np.max(prediction)  # Lấy xác suất cao nhất từ dự đoán

        if confidence > threshold:  # Chỉ chấp nhận dự đoán nếu xác suất cao hơn ngưỡng
            character = labels[index]  # Cập nhật ký tự

            # Kiểm tra nếu khoảng thời gian giữa các lần nhận diện đủ dài (detection_timeout)
            if time.time() - last_detection_time > detection_timeout:
                # Lưu ký tự nhận diện vào biến detected_text
                detected_text.append(character)
                last_detection_time = time.time()  # Cập nhật thời gian nhận diện lần cuối

                # Nếu ký tự là 'Next', chỉ lưu ký tự cuối cùng và reset detected_text
                if character == 'Next':
                    if detected_text:
                        detected_text = [detected_text[-2]] if len(detected_text) > 1 else []
                    else:
                        detected_text = []

            return character, imgOutput, x, y, w, h, labels[index]
        else:
            return "Low confidence", img, 0, 0, 0, 0, ""
    else:
        return "No hand detected", img, 0, 0, 0, 0, ""

def decode_prediction(prediction):
    class_names = labels  # Replace with your actual class names
    predicted_class = class_names[np.argmax(prediction)]
    return predicted_class

def text_to_speech(text):
    engine.say(text)
    engine.runAndWait()