import cv2
import numpy as np
import time
from mss import mss
from directkey import PressKey, ReleaseKey, KeyCodes

# Function to capture a specific screen region using the mss library
def capture_screen_region(x, y, width, height):
    with mss() as sct:
        # Define the region for screen capture
        monitor = {"top": y, "left": x, "width": width, "height": height}
        # Capture the screenshot for the defined region
        screenshot = sct.grab(monitor)
        # Convert the screenshot to a numpy array and return
        return np.array(screenshot)

# Function to extract a region of interest from the image
def roi(img, vertices):
    # Initialize a blank mask of zeros with the same shape as the image
    mask = np.zeros_like(img)
    # Fill the specified vertices with 255 to create the ROI
    cv2.fillPoly(mask, vertices, 255)
    # Return the image only where mask pixels are nonzero
    masked = cv2.bitwise_and(img, mask)
    return masked

# Function to draw identified lines onto the image
def draw_lines(img, lines):
    for line in lines:
        coords = line[0]
        # Draw the line on the image
        cv2.line(img, (coords[0], coords[1]), (coords[2], coords[3]), [255,255,255], 3)

# Main image processing function
def process_img(original_image):
    # Convert the image to grayscale
    processed_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    # Apply the Canny edge detection
    processed_img = cv2.Canny(processed_img, threshold1=200, threshold2=300)
    # Apply Gaussian blur to smooth the image
    processed_img = cv2.GaussianBlur(processed_img, (5,5), 0)
    # Define the vertices for the region of interest
    vertices = np.array([[10,500],[10,300],[300,200],[500,200],[800,300],[800,500]], np.int32)
    # Extract the region of interest from the image
    processed_img = roi(processed_img, [vertices])
    # Detect lines in the image using the Hough transform
    lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 180, 20, 15)
    # Draw the detected lines onto the image
    draw_lines(processed_img, lines)
    return processed_img

def main():
    start_time = time.time()
    frame_count = 0

    while True:
        # Capture a portion of the screen
        frame = capture_screen_region(0, 40, 800, 640)
        # Process the captured frame (edge detection, ROI, line detection)
        processed_frame = process_img(frame)
        # Display the processed image
        cv2.imshow("Processed", processed_frame)

        frame_count += 1
        elapsed_time = time.time() - start_time
        
        # Calculate and display FPS every second
        if elapsed_time > 1:
            print(f"FPS: {frame_count/elapsed_time:.2f}")
            start_time = time.time()
            frame_count = 0

        # Simulate a key press (for game control or other purposes)
        PressKey(KeyCodes.W.value)

        # Exit loop and release the key if 'ESC' key is pressed
        if cv2.waitKey(1) == 27:
            ReleaseKey(KeyCodes.W.value)
            break

    # Close all OpenCV windows after exiting the loop
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
