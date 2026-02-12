from typing import List, Dict, Tuple, Optional
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import base64
import io

class DetectionOverlay:
    """Create visualization overlays for detection results"""
    def __init__(self, config):
        self.config = config
        self.color_map = config.VisualizationConfig.color_map
        self.overlay_alpha = config.VisualizationConfig.overlay_alpha

    def create_detection_overlay(
        self,
        image: np.ndarray,
        detections: List[Dict],
        label: str,
        color: Tuple[int, int, int] = (255, 0, 0)
    ) -> np.ndarray:
        """Create overlay image with detection bounding boxes"""
        overlay = image.copy()

        for detection in detections:
            box = detection["box"]
            confidence = detection["confidence"]

            # Draw bounding box
            overlay = self._draw_bounding_box(overlay, box, color)

            # Add label and confidence
            overlay = self._add_label(overlay, box, label, confidence, color)

        # Apply transparency
        overlay = self._apply_transparency(overlay, image)

        return overlay

    def _draw_bounding_box(self, image: np.ndarray, box: List[float], color: Tuple[int, int, int]) -> np.ndarray:
        """Draw bounding box on image"""
        x1, y1, x2, y2 = map(int, box)
        thickness = max(2, int(0.02 * image.shape[1]))  # Scale with image width

        # Draw rectangle
        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)

        return image

    def _add_label(self, image: np.ndarray, box: List[float], label: str, confidence: float, color: Tuple[int, int, int]) -> np.ndarray:
        """Add label and confidence text"""
        x1, y1, x2, y2 = map(int, box)
        font_scale = max(0.5, 0.002 * image.shape[1])  # Scale with image width
        thickness = max(1, int(0.001 * image.shape[1]))

        # Create label text
        text = f"{label}: {confidence:.2f}"

        # Get text size
        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)

        # Position text (top-left of box)
        text_x = x1
        text_y = y1 - 5

        # Draw text background
        cv2.rectangle(
            image,
            (text_x, text_y - text_height - 5),
            (text_x + text_width, text_y + 5),
            color,
            -1
        )

        # Draw text
        cv2.putText(
            image,
            text,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (255, 255, 255),  # White text
            thickness,
            cv2.LINE_AA
        )

        return image

    def _apply_transparency(self, overlay: np.ndarray, original: np.ndarray) -> np.ndarray:
        """Apply transparency to overlay"""
        alpha = self.overlay_alpha
        return cv2.addWeighted(overlay, alpha, original, 1 - alpha, 0)

    def create_heatmap_overlay(
        self,
        image: np.ndarray,
        heatmap: np.ndarray,
        colormap: str = "viridis"
    ) -> np.ndarray:
        """Create heatmap overlay for probability maps"""
        # Normalize heatmap to [0, 255]
        heatmap_normalized = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # Apply colormap
        heatmap_color = cv2.applyColorMap(heatmap_normalized, self._get_colormap_id(colormap))

        # Blend with original image
        overlay = cv2.addWeighted(heatmap_color, 0.5, image, 0.5, 0)

        return overlay

    def _get_colormap_id(self, colormap_name: str) -> int:
        """Get OpenCV colormap ID from name"""
        colormap_mapping = {
            "viridis": cv2.COLORMAP_VIRIDIS,
            "plasma": cv2.COLORMAP_PLASMA,
            "inferno": cv2.COLORMAP_INFERNO,
            "magma": cv2.COLORMAP_MAGMA,
            "cividis": cv2.COLORMAP_CIVIDIS,
            "hot": cv2.COLORMAP_HOT,
            "jet": cv2.COLORMAP_JET,
            "rainbow": cv2.COLORMAP_RAINBOW,
            "ocean": cv2.COLORMAP_OCEAN,
            "terrain": cv2.COLORMAP_TERRRAIN
        }
        return colormap_mapping.get(colormap_name, cv2.COLORMAP_VIRIDIS)

    def create_contour_overlay(
        self,
        image: np.ndarray,
        probability_map: np.ndarray,
        threshold: float = 0.5,
        color: Tuple[int, int, int] = (0, 255, 0)
    ) -> np.ndarray:
        """Create contour overlay from probability map"""
        # Binarize probability map
        binary_map = (probability_map > threshold).astype(np.uint8) * 255

        # Find contours
        contours, _ = cv2.findContours(binary_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw contours on image
        overlay = image.copy()
        cv2.drawContours(overlay, contours, -1, color, 2)

        return overlay

    def generate_visualization_report(
        self,
        original_image: np.ndarray,
        preprocessed_image: np.ndarray,
        detections: List[Dict],
        heatmap: Optional[np.ndarray] = None
    ) -> str:
        """Generate a complete visualization report as base64 string"""
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(12, 12))
        fig.tight_layout(pad=3.0)

        # Original image
        axes[0, 0].imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
        axes[0, 0].set_title('Original Image')
        axes[0, 0].axis('off')

        # Preprocessed image
        axes[0, 1].imshow(cv2.cvtColor(preprocessed_image, cv2.COLOR_BGR2RGB))
        axes[0, 1].set_title('Preprocessed Image')
        axes[0, 1].axis('off')

        # Detection overlay
        if detections:
            overlay_image = self.create_detection_overlay(
                original_image.copy(),
                detections,
                label="Detection",
                color=(255, 0, 0)
            )
            axes[1, 0].imshow(cv2.cvtColor(overlay_image, cv2.COLOR_BGR2RGB))
            axes[1, 0].set_title('Detection Overlay')
            axes[1, 0].axis('off')

        # Heatmap
        if heatmap is not None:
            heatmap_overlay = self.create_heatmap_overlay(
                original_image,
                heatmap,
                colormap=self.color_map
            )
            axes[1, 1].imshow(cv2.cvtColor(heatmap_overlay, cv2.COLOR_BGR2RGB))
            axes[1, 1].set_title('Heatmap Overlay')
            axes[1, 1].axis('off')

        # Save to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)

        # Convert to base64
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return image_base64

# Advanced visualization utilities
def create_probability_heatmap(
    image: np.ndarray,
    probability_map: np.ndarray,
    threshold: float = 0.5
) -> np.ndarray:
    """Create probability heatmap visualization"""
    # Resize heatmap to image size
    heatmap_resized = cv2.resize(probability_map, (image.shape[1], image.shape[0]))

    # Create overlay
    heatmap_color = cv2.applyColorMap(
        (heatmap_resized * 255).astype(np.uint8),
        cv2.COLORMAP_JET
    )

    # Blend with original image
    overlay = cv2.addWeighted(heatmap_color, 0.6, image, 0.4, 0)

    # Add threshold contour
    binary_map = (heatmap_resized > threshold).astype(np.uint8) * 255
    contours, _ = cv2.findContours(binary_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, contours, -1, (0, 255, 0), 2)

    return overlay

def create_time_series_plot(
    timestamps: List[str],
    detection_counts: List[int],
    title: str = "Detection Count Over Time"
) -> str:
    """Create time series plot of detection counts"""
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, detection_counts, marker='o', linewidth=2, markersize=5)
    plt.title(title)
    plt.xlabel('Time')
    plt.ylabel('Detection Count')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)

    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    # Convert to base64
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return image_base64