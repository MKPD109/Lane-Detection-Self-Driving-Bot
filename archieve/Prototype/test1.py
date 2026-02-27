import pyautogui
import keyboard
import time
import cv2
import numpy as np

def capture_screen_region(x, y, width, height):
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    return np.array(screenshot)

def edge_detection(image):
    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Canny edge detector
    edges = cv2.Canny(gray_image, 100, 200)
    
    return edges

def main():
    start_time = time.time()
    frame_count = 0

    while True:
        if keyboard.is_pressed('q'):  # If 'q' is pressed, exit the loop
            break

        # Capture the screen for the given region
        frame = capture_screen_region(0, 40, 800, 640)
        edges = edge_detection(frame)
        
        # Displaying the captured screen with edge detection
        cv2.imshow("Edges", edges)

        frame_count += 1
        elapsed_time = time.time() - start_time
        
        # Calculate and display the FPS every second
        if elapsed_time > 1:
            print(f"FPS: {frame_count/elapsed_time:.2f}")
            start_time = time.time()
            frame_count = 0

        # Check for 'ESC' key press to exit the loop
        if cv2.waitKey(1) == 27:  # 27 the 'ESC' key
            break

    # Destroy all OpenCV windows after exiting the loop
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
