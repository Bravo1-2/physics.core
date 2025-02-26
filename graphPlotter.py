import cv2
from PIL import Image
import numpy as np
import re
import matplotlib.pyplot as plt
import pytesseract

class GraphPlotter:
    def __init__(self, graph_path, convert_to_si=False):
        self.image_path = graph_path
        self.convert_to_si = convert_to_si
        self.graph_type = None
        self.units = None
        self.data_points = []

    def preprocess_graph(self):
        # Preprocess the graph image for better OCR results
        graph = cv2.imread(self.image_path)
        gray = cv2.cvtColor(graph, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5,5), 0)
        adaptive_thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        return adaptive_thresh

    def extract_text(self, processed_image):
        # Extract text from the image using OCR
        text = pytesseract.image_to_string(Image.fromarray(processed_image))
        return text

    def detect_graph_types_and_units(self, text):
        # Detect the type of graph and the units used
        if "Distance" in text and "Time" in text:
            self.graph_type  = "Distance vs Time"
            self.units = {"x": "s", "y": "m"} # Default SI
        elif "Speed" in text and "Time" in text:
            self.graph_type = "Speed vs Time"
            self.units = {"x": "s", "y": "m/s"}
        elif "Velocity" in text and "Time" in text:
            self.graph_type = "Velocity vs Time"
            self.units = {"x": "s", "y": "m/s"}
        elif "Speed" in text and "Displacement" in text:
            self.graph_type = "Speed vs Displacement"
            self.units = {"x": "m", "y": "m/s"}
        elif "Velocity" in text and "Displacement" in text:
            self.graph_type = "Velocity vs Displacement"
            self.units = {"x": "m", "y": "m/s"}
        else:
            self.graph_type = "Unknown"
            self.units = {"x": "Unknown", "y": "Unknown"}
        # Detect other possible units
        unit_patterns = {"km/s": "km/s", "m/hr": "m/hr", "km/hr": "km/hr", "min":"min"}
        for pattern, unit in unit_patterns.items():
            if pattern in text:
                self.units = {"x": unit if "Time" in self.graph_type else "m", "y": unit}
                break

    def extract_data_points(self, text):
        # Extract numerical data points from the graph
        time_pattern = r"(\d{1,2}[:.]\d{2})" # Matches time formats
        value_pattern = r"(\d+)" # Matches numerical values
        times = re.findall(time_pattern, text)
        values = re.findall(value_pattern, text)
        self.data_points = list(zip(times, values[:len(times)]))

    def convert_to_si_units(self):
        # Convert extracted values to SI units if requested
        if self.convert_to_si:
            conversion_factors = {"km/s": 1000, "km/hr": 1000 / 3600, "m/hr": 1 / 3600, "min": 60}
            for unit, factor in conversion_factors.items():
                if self.units["y"] == unit:
                    self.data_points = [(t, float(v) * factor) for t, v in self.data_points]
                    self.units["y"] = "m/s"
                if self.units["x"] == "min":
                    self.data_points = [(float(t) * 60, v) for t, v in self.data_points]
                    self.units["x"] = "s"

    def plot_graph(self):
        # Plot the extracted data points
        if not self.data_points:
            print("No data points available to plot")
            return

        x_values = [float(t.replace(':', '.')) for t, _ in self.data_points]
        y_values = [float(v) for _, v in self.data_points]

        plt.figure(figsize=(8,6))
        plt.plot(x_values, y_values, marker='o', linestyle='-', color='b')
        plt.xlabel(f"{self.units['x']}")
        plt.ylabel(f"{self.units['y']}")
        plt.title(f"{self.graph_type}")
        plt.grid(True)
        plt.show()

    def process_graph(self):
        # Main function to process the graph
        processed_graph = self.preprocess_graph()
        extracted_text = self.extract_text(processed_graph)
        self.detect_graph_types_and_units(extracted_text)
        self.extract_data_points(extracted_text)
        self.convert_to_si_units()
        self.plot_graph()
        return {
            "Graph Type": self.graph_type,
            "Units": self.units,
            "Data Points": self.data_points
        }

if __name__ == "__main__":
    image_path = input("Enter the path to the graph image: ")
    graph_plotter = GraphPlotter(image_path)
    result = graph_plotter.process_graph()
    print(result)
