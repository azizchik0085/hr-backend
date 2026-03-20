from deepface import DeepFace
import cv2
import numpy as np
import os

print("DeepFace imported successfully.")

# Create temporary black images just to test initialization
img1 = np.zeros((224, 224, 3), dtype=np.uint8)
img2 = np.zeros((224, 224, 3), dtype=np.uint8)

cv2.imwrite("test1.jpg", img1)
cv2.imwrite("test2.jpg", img2)

try:
    print("Testing verification...")
    # This will download weights if not present
    DeepFace.verify("test1.jpg", "test2.jpg", enforce_detection=False)
    print("DeepFace is working!")
except Exception as e:
    print(f"Error: {e}")

try:
    os.remove("test1.jpg")
    os.remove("test2.jpg")
except:
    pass
