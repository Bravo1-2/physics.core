import cv2
import matplotlib.pyplot as plt

# List of image paths
image_paths = [
    # Change the image path based on your location
    '/home/preet/Documents/physics.core/image1.png',
    '/home/preet/Documents/physics.core/image2.png',
    '/home/preet/Documents/physics.core/image3.png'
               ]
for image_path in image_paths:
    # Load the image
    image = cv2.imread(image_path)

    # Convert BGR to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Display the image
    plt.figure(figsize=(8, 6))
    plt.imshow(image_rgb)
    plt.title(f'Loaded Diagram - {image_path}')
    plt.axis('off')
    plt.show()