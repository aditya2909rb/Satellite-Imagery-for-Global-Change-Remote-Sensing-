"""Preprocessing module for satellite detection project"""
import numpy as np
import cv2

def preprocess_image(image: np.ndarray) -> np.ndarray:
    """Simple image preprocessing for satellite imagery"""
    if image is None or len(image) == 0:
        return np.zeros((512, 512, 3), dtype=np.uint8)
    
    # Resize to model input size
    resized = cv2.resize(image, (512, 512))
    
    # Normalize to [0, 1]
    if resized.dtype == np.uint8:
        normalized = resized.astype(np.float32) / 255.0
    else:
        normalized = resized.astype(np.float32)
    
    return normalized
