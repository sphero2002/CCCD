# qr_utils.py
from pyzbar.pyzbar import decode
from PIL import Image
import cv2
import numpy as np
from scipy import ndimage

class QRHelper:
    def preprocess_image(self, image):
        """
        Tiền xử lý ảnh để tăng khả năng đọc QR code
        """
        # Chuyển sang ảnh xám
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Làm mịn ảnh để giảm nhiễu
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Tăng độ tương phản
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(blurred)
        
        # Nhị phân hóa với ngưỡng thích ứng
        threshold = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        return threshold

    def resize_and_decode(self, image, scale_factors=[1.0, 1.5, 0.5]):
        """
        Thử decode với các kích thước ảnh khác nhau
        """
        results = []
        for scale in scale_factors:
            width = int(image.shape[1] * scale)
            height = int(image.shape[0] * scale)
            resized = cv2.resize(image, (width, height))
            
            # Thử decode ảnh gốc
            decoded = decode(resized)
            if decoded:
                results.extend(decoded)
                
            # Thử decode ảnh đã xử lý
            processed = self.preprocess_image(resized)
            decoded = decode(processed)
            if decoded:
                results.extend(decoded)
                
        return results

    def decode_with_rotation(self, image, angles=[0, 90, 180, 270]):
        """
        Thử decode với các góc xoay khác nhau
        """
        results = []
        for angle in angles:
            rotated = ndimage.rotate(image, angle)
            decoded = decode(rotated)
            if decoded:
                results.extend(decoded)
        return results

    def decode_qr_with_retry(self, image, max_attempts=3):
        """
        Thử decode nhiều lần với các phương pháp khác nhau
        """
        try:
            # Attempt 1: Decode trực tiếp
            results = decode(image)
            if results:
                return results

            # Attempt 2: Decode sau khi xử lý ảnh
            processed = self.preprocess_image(image)
            results = decode(processed)
            if results:
                return results

            # Attempt 3: Thử với nhiều kích thước
            results = self.resize_and_decode(image)
            if results:
                return results

            # Attempt 4: Thử với các góc xoay
            results = self.decode_with_rotation(processed)
            if results:
                return results

            return None

        except Exception as e:
            print(f"Error in decode_qr_with_retry: {str(e)}")
            return None