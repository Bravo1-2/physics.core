import cv2
import numpy as np
import pytesseract
from PIL import Image
import matplotlib.pyplot as plt
import re

class AdvancedGraphAnalyzer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.original_image = cv2.imread(image_path)
        self.processed_image = None
        self.plot_area = None
        self.axis_labels = {"x": None, "y": None}
        self.units = {"x": "unknown", "y": "unknown"}
        self.data_points = []
        self.graph_type = "unknown"
        
        # Configuration
        self.ocr_config = r'--oem 3 --psm 6'
        self.unit_conversion = {
            'km/h': {'factor': 0.27778, 'target': 'm/s'},
            'mph': {'factor': 0.44704, 'target': 'm/s'},
            'min': {'factor': 60, 'target': 's'},
            'hr': {'factor': 3600, 'target': 's'},
            'km': {'factor': 1000, 'target': 'm'}
        }

    def _preprocess_image(self):
        """Enhance image for better OCR and feature detection"""
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        self.processed_image = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

    def _detect_plot_area(self):
        """Find main plot area using contour analysis"""
        edges = cv2.Canny(self.processed_image, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            raise ValueError("No contours found - cannot detect plot area")

        # Find largest rectangular contour
        largest_contour = max(contours, key=lambda c: cv2.contourArea(c))
        x, y, w, h = cv2.boundingRect(largest_contour)
        self.plot_area = self.processed_image[y:y+h, x:x+w]
        return x, y, w, h

    def _extract_axis_labels(self):
        """Extract and parse axis labels using targeted OCR"""
        # Detect X-axis label (bottom 10% of plot area)
        x_axis_roi = self.plot_area[-int(self.plot_area.shape[0]*0.1):, :]
        x_text = pytesseract.image_to_string(
            Image.fromarray(x_axis_roi), config=self.ocr_config
        )
        
        # Detect Y-axis label (left 10% of plot area)
        y_axis_roi = self.plot_area[:, :int(self.plot_area.shape[1]*0.1)]
        y_text = pytesseract.image_to_string(
            Image.fromarray(y_axis_roi), config=self.ocr_config
        )

        # Parse units using improved regex
        unit_pattern = r"\(?([a-zA-Z/]+)\)?"
        self.axis_labels["x"] = self._parse_axis_label(x_text)
        self.axis_labels["y"] = self._parse_axis_label(y_text)
        
        # Determine graph type based on axis labels
        self.graph_type = f"{self.axis_labels['y']} vs {self.axis_labels['x']}"

    def _parse_axis_label(self, text):
        """Enhanced label parsing with unit detection"""
        # Remove special characters
        clean_text = re.sub(r'[^a-zA-Z0-9/]', ' ', text)
        # Find potential units
        matches = re.findall(r'\b(m/s|km/h|s|m|min|hr)\b', clean_text, re.IGNORECASE)
        return matches[0].lower() if matches else "unknown"

    def _extract_data_points(self):
        """Detect data points using line detection and pixel analysis"""
        # Convert to RGB for visualization
        plot_rgb = cv2.cvtColor(self.plot_area, cv2.COLOR_GRAY2RGB)
        
        # Detect lines using Hough Transform
        lines = cv2.HoughLinesP(
            self.plot_area, 1, np.pi/180, threshold=50,
            minLineLength=30, maxLineGap=10
        )

        if lines is None:
            raise ValueError("No data line detected in the plot area")

        # Collect all points from detected lines
        points = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            points.extend([(x1, y1), (x2, y2)])
            
        # Convert pixel positions to data values
        self._pixel_to_data(points)

    def _pixel_to_data(self, pixel_points):
        """Convert pixel coordinates to data values (simplified example)"""
        # In real implementation, use axis scale calibration
        # This is a simplified linear approximation
        x_min, x_max = 0, self.plot_area.shape[1]
        y_min, y_max = self.plot_area.shape[0], 0
        
        # Assume sample data range for demonstration
        data_x = np.linspace(0, 10, x_max)
        data_y = np.linspace(0, 100, y_max)
        
        for x, y in pixel_points:
            self.data_points.append((
                round(data_x[x], 2),
                round(data_y[y], 2)
            ))

    def _convert_units(self):
        """Apply unit conversions based on detected units"""
        for axis in ['x', 'y']:
            unit = self.axis_labels[axis]
            if unit in self.unit_conversion:
                conversion = self.unit_conversion[unit]
                self.data_points = [
                    (x * conversion['factor'] if axis == 'x' else x,
                     y * conversion['factor'] if axis == 'y' else y)
                    for x, y in self.data_points
                ]
                self.axis_labels[axis] = conversion['target']

    def analyze(self):
        """Main analysis pipeline"""
        try:
            self._preprocess_image()
            self._detect_plot_area()
            self._extract_axis_labels()
            self._extract_data_points()
            self._convert_units()
            return True
        except Exception as e:
            print(f"Analysis failed: {str(e)}")
            return False

    def visualize(self):
        """Create visualization of processed data"""
        if not self.data_points:
            print("No data points to visualize")
            return

        plt.figure(figsize=(10, 6))
        x_vals, y_vals = zip(*self.data_points)
        
        plt.plot(x_vals, y_vals, 'b-', marker='o')
        plt.xlabel(f"{self.axis_labels['x'].upper()} ({self.units['x']})")
        plt.ylabel(f"{self.axis_labels['y'].upper()} ({self.units['y']})")
        plt.title(f"Processed Graph: {self.graph_type}")
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    analyzer = AdvancedGraphAnalyzer("sample_graph.png")
    if analyzer.analyze():
        print("Analysis successful!")
        print(f"Graph Type: {analyzer.graph_type}")
        print(f"Data Points: {analyzer.data_points[:5]}...")  # Show first 5 points
        analyzer.visualize()
    else:
        print("Analysis failed")
