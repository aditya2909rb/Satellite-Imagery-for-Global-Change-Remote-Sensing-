import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Dict, Tuple
import numpy as np
import cv2
import onnxruntime as ort
from pathlib import Path
import asyncio
import psutil
import datetime

class SmokeDetector:
    """Smoke detection model using ONNX for hardware optimization"""
    def __init__(self, model_dir: str):
        self.model_path = Path(model_dir) / "smoke_detection.onnx"
        self.session = None
        self.is_loaded = False
        self.input_shape = (3, 512, 512)  # RGB, 512x512
        self.confidence_threshold = 0.7

    async def load_model(self):
        """Load the smoke detection model"""
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model not found: {self.model_path}")

            # Create ONNX session with hardware optimization
            self.session = ort.InferenceSession(
                str(self.model_path),
                providers=['CUDAExecutionProvider' if torch.cuda.is_available() else 'CPUExecutionProvider']
            )
            self.is_loaded = True
            print(f"Smoke detector loaded: {self.model_path}")
        except Exception as e:
            print(f"Error loading smoke detector: {e}")
            self.is_loaded = False

    async def detect(self, image: np.ndarray, confidence_threshold: float = 0.7) -> List[Dict]:
        """Detect smoke in the given image"""
        if not self.is_loaded:
            raise RuntimeError("Smoke detector model not loaded")

        # Preprocess for model input
        input_tensor = self._preprocess_input(image)

        # Run inference
        outputs = self.session.run(
            None,
            {"input": input_tensor}
        )

        # Post-process detections
        detections = self._postprocess_outputs(outputs, confidence_threshold)

        return detections

    def _preprocess_input(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for model input"""
        # Resize to model input shape
        resized = cv2.resize(image, (self.input_shape[2], self.input_shape[1]))
        # Normalize to [0, 1]
        normalized = resized / 255.0
        # Convert to tensor format (CHW)
        tensor = np.transpose(normalized, (2, 0, 1))
        # Add batch dimension
        tensor = np.expand_dims(tensor, axis=0).astype(np.float32)
        return tensor

    def _postprocess_outputs(self, outputs: List[np.ndarray], threshold: float) -> List[Dict]:
        """Post-process model outputs to get detections"""
        boxes = outputs[0]  # Assuming first output is bounding boxes
        scores = outputs[1]  # Assuming second output is confidence scores

        detections = []
        for i in range(len(scores)):
            if scores[i] >= threshold:
                detection = {
                    "box": boxes[i].tolist(),
                    "confidence": float(scores[i]),
                    "label": "smoke",
                    "timestamp": datetime.now().isoformat()
                }
                detections.append(detection)

        return detections

class DustDetector:
    """Dust detection model using ONNX for hardware optimization"""
    def __init__(self, model_dir: str):
        self.model_path = Path(model_dir) / "dust_detection.onnx"
        self.session = None
        self.is_loaded = False
        self.input_shape = (3, 512, 512)
        self.confidence_threshold = 0.7

    async def load_model(self):
        """Load the dust detection model"""
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model not found: {self.model_path}")

            # Create ONNX session with hardware optimization
            self.session = ort.InferenceSession(
                str(self.model_path),
                providers=['CUDAExecutionProvider' if torch.cuda.is_available() else 'CPUExecutionProvider']
            )
            self.is_loaded = True
            print(f"Dust detector loaded: {self.model_path}")
        except Exception as e:
            print(f"Error loading dust detector: {e}")
            self.is_loaded = False

    async def detect(self, image: np.ndarray, confidence_threshold: float = 0.7) -> List[Dict]:
        """Detect dust in the given image"""
        if not self.is_loaded:
            raise RuntimeError("Dust detector model not loaded")

        # Preprocess for model input
        input_tensor = self._preprocess_input(image)

        # Run inference
        outputs = self.session.run(
            None,
            {"input": input_tensor}
        )

        # Post-process detections
        detections = self._postprocess_outputs(outputs, confidence_threshold)

        return detections

    def _preprocess_input(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for model input"""
        resized = cv2.resize(image, (self.input_shape[2], self.input_shape[1]))
        normalized = resized / 255.0
        tensor = np.transpose(normalized, (2, 0, 1))
        tensor = np.expand_dims(tensor, axis=0).astype(np.float32)
        return tensor

    def _postprocess_outputs(self, outputs: List[np.ndarray], threshold: float) -> List[Dict]:
        """Post-process model outputs to get detections"""
        boxes = outputs[0]
        scores = outputs[1]

        detections = []
        for i in range(len(scores)):
            if scores[i] >= threshold:
                detection = {
                    "box": boxes[i].tolist(),
                    "confidence": float(scores[i]),
                    "label": "dust",
                    "timestamp": datetime.now().isoformat()
                }
                detections.append(detection)

        return detections

# Hardware optimization utilities
def get_system_info() -> Dict:
    """Get system information for optimization"""
    return {
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "gpu_available": torch.cuda.is_available(),
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
        "torch_version": torch.__version__
    }

def optimize_model(model_path: str, optimize_for: str = "mobile") -> str:
    """Optimize model for specific hardware"""
    # This would include model quantization, pruning, etc.
    # For now, return the same path
    return model_path