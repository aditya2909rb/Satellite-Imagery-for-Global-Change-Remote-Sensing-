import numpy as np
import cv2
from typing import Tuple, Optional
from pathlib import Path
import asyncio

class ImagePreprocessor:
    """Image preprocessing pipeline for satellite imagery"""
    def __init__(self, config):
        self.config = config
        self.cloud_threshold = config.PreprocessingConfig.cloud_detection_threshold
        self.atmospheric_correction = config.PreprocessingConfig.atmospheric_correction

    async def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Complete preprocessing pipeline"""
        # Step 1: Cloud detection and masking
        cloud_mask = await self._detect_clouds(image)

        # Step 2: Atmospheric correction
        if self.atmospheric_correction:
            image = self._correct_atmosphere(image, cloud_mask)

        # Step 3: Normalization
        image = self._normalize(image)

        # Step 4: Resize for model input
        image = self._resize(image)

        return image

    async def _detect_clouds(self, image: np.ndarray) -> np.ndarray:
        """Detect clouds using spectral analysis"""
        # Convert to HSV for better cloud detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Cloud detection using brightness and saturation
        brightness = hsv[:, :, 2]
        saturation = hsv[:, :, 1]

        # Cloud mask: bright and low saturation
        cloud_mask = (brightness > 200) & (saturation < 50)

        # Convert to 3-channel mask
        cloud_mask_3c = np.zeros_like(image)
        cloud_mask_3c[cloud_mask] = [255, 255, 255]

        return cloud_mask_3c

    def _correct_atmosphere(self, image: np.ndarray, cloud_mask: np.ndarray) -> np.ndarray:
        """Correct atmospheric effects"""
        # Dark Channel Prior for haze removal
        dark_channel = self._dark_channel_prior(image)

        # Estimate atmospheric light
        atmospheric_light = self._estimate_atmospheric_light(image, dark_channel)

        # Transmission estimation
        transmission = self._estimate_transmission(dark_channel, atmospheric_light)

        # Apply atmospheric correction
        corrected = self._apply_atmospheric_correction(
            image,
            atmospheric_light,
            transmission,
            cloud_mask
        )

        return corrected

    def _dark_channel_prior(self, image: np.ndarray, patch_size: int = 15) -> np.ndarray:
        """Calculate dark channel prior"""
        b, g, r = cv2.split(image)
        min_img = cv2.min(cv2.min(r, g), b)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (patch_size, patch_size))
        dark_channel = cv2.erode(min_img, kernel)
        return dark_channel

    def _estimate_atmospheric_light(self, image: np.ndarray, dark_channel: np.ndarray) -> np.ndarray:
        """Estimate atmospheric light"""
        # Find top 0.1% brightest pixels in dark channel
        num_pixels = int(0.001 * dark_channel.size)
        dark_channel_flat = dark_channel.flatten()
        indices = np.argpartition(dark_channel_flat, -num_pixels)[-num_pixels:]
        atmospheric_light = np.mean(image.reshape(-1, 3)[indices], axis=0)
        return atmospheric_light

    def _estimate_transmission(self, dark_channel: np.ndarray, atmospheric_light: np.ndarray) -> np.ndarray:
        """Estimate transmission map"""
        omega = 0.95  # Haze retention factor
        transmission = 1 - omega * (self._dark_channel_prior(dark_channel) / atmospheric_light)
        return transmission

    def _apply_atmospheric_correction(
        self,
        image: np.ndarray,
        atmospheric_light: np.ndarray,
        transmission: np.ndarray,
        cloud_mask: np.ndarray
    ) -> np.ndarray:
        """Apply atmospheric correction to image"""
        t0 = 0.1  # Minimum transmission
        transmission = np.maximum(transmission, t0)

        # Avoid division by zero
        transmission = np.maximum(transmission, 1e-8)

        # Haze removal
        J = np.zeros_like(image, dtype=np.float32)
        for c in range(3):
            J[:, :, c] = (image[:, :, c] - atmospheric_light[c]) / transmission + atmospheric_light[c]

        # Convert back to uint8
        J = np.clip(J, 0, 255).astype(np.uint8)

        # Apply cloud mask
        J = np.where(cloud_mask == 255, image, J)

        return J

    def _normalize(self, image: np.ndarray) -> np.ndarray:
        """Normalize image using specified method"""
        method = self.config.PreprocessingConfig.normalization

        if method == "min-max":
            return cv2.normalize(image, None, 0, 1, cv2.NORM_MINMAX).astype(np.float32)
        elif method == "z-score":
            mean = np.mean(image, axis=(0, 1), keepdims=True)
            std = np.std(image, axis=(0, 1), keepdims=True)
            return (image - mean) / (std + 1e-6)
        else:
            return image / 255.0

    def _resize(self, image: np.ndarray) -> np.ndarray:
        """Resize image to model input size"""
        target_size = (512, 512)  # Model input size
        method = self.config.PreprocessingConfig.resize_method

        if method == "bilinear":
            return cv2.resize(image, target_size, interpolation=cv2.INTER_LINEAR)
        elif method == "bicubic":
            return cv2.resize(image, target_size, interpolation=cv2.INTER_CUBIC)
        elif method == "area":
            return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
        else:
            return cv2.resize(image, target_size)

# Additional preprocessing utilities
def enhance_contrast(image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
    """Enhance image contrast using CLAHE"""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    l_enhanced = clahe.apply(l)

    lab_enhanced = cv2.merge([l_enhanced, a, b])
    image_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

    return image_enhanced

def remove_noise(image: np.ndarray, method: str = "gaussian", kernel_size: int = 5) -> np.ndarray:
    """Remove noise from image"""
    if method == "gaussian":
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    elif method == "median":
        return cv2.medianBlur(image, kernel_size)
    elif method == "bilateral":
        return cv2.bilateralFilter(image, kernel_size, 75, 75)
    else:
        return image

def correct_illumination(image: np.ndarray) -> np.ndarray:
    """Correct non-uniform illumination"""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # Apply morphological operations to get background
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
    background = cv2.morphologyEx(l, cv2.MORPH_CLOSE, kernel)

    # Normalize illumination
    l_corrected = cv2.divide(l, background, scale=255)

    lab_corrected = cv2.merge([l_corrected, a, b])
    image_corrected = cv2.cvtColor(lab_corrected, cv2.COLOR_LAB2BGR)

    return image_corrected.astype(np.uint8)