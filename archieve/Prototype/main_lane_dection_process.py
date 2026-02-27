import cv2
import numpy as np
import time
from mss import mss
from statistics import mean
from numpy.linalg import lstsq
from numpy import ones,vstack

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

# Main image processing function
def process_img(original_image):
    # Convert the RGB image to a grayscale image to simplify analysis.
    processed_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    
    # Use Canny edge detection to detect edges in the image.
    # This will highlight the structural features, such as lanes.
    # original th1 = 200 th2 = 300
    processed_img = cv2.Canny(processed_img, threshold1=200, threshold2=280)
    
    # Apply a Gaussian blur to the image to reduce noise and make edges smoother.
    # This helps in achieving better results in edge detection.
    processed_img = cv2.GaussianBlur(processed_img, (5,5), 0)
    
    # Define a polygonal region of interest (ROI) to focus on the main road area.
    # This helps to ignore other unnecessary details from the image.
    #vertices = np.array([[10,500],[10,300],[300,200],[500,200],[800,300],[800,500]], np.int32) #Original
    #vertices = np.array([[10, 500], [300, 250],  [500, 200], [790, 400]], np.int32) #no2
    #vertices = np.array([[10, 500], [300, 250],  [500, 200], [790, 400]], np.int32)
    vertices = np.array([[10,500],[28,360],[350,320],[450,320],[750,360],[800,500]], np.int32) 
    #vertices = np.array([[10,500],[10,360],[300,220],[500,220],[800,360],[800,500]], np.int32) 
    
    # Apply the ROI on the processed image to retain only the defined polygonal region.
    processed_img = roi(processed_img, [vertices])
    
    # Use the Hough transform to detect lines in the image.
    # These lines will represent the lane lines and other linear features.
    lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 180, 20, 15)
    
    try:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(original_image, (x1, y1), (x2, y2), [255,0,0], 3)  # Drawing in blue color

    except Exception as e:
        # If there's any error in drawing main lanes, log the error.
        print(str(e))
        pass
         
    # Return the processed image with all detected lines 
    return processed_img, original_image

def main():
    start_time = time.time()
    frame_count = 0

    while True:
        # Capture a portion of the screen
        frame = capture_screen_region(0, 40, 800, 600)
        # Process the captured frame (edge detection, ROI, line detection)
        processed_frame, original_frame = process_img(frame)
        # Display the processed image
        cv2.imshow("Processed", processed_frame)
        cv2.imshow("Original", original_frame)

        frame_count += 1
        elapsed_time = time.time() - start_time
        
        # Calculate and display FPS every second
        if elapsed_time > 1:
            print(f"FPS: {frame_count/elapsed_time:.2f}")
            start_time = time.time()
            frame_count = 0

        # Exit loop and release the key if 'ESC' key is pressed
        if cv2.waitKey(1) == 27:
            break

    # Close all OpenCV windows after exiting the loop
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
