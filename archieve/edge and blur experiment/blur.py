import cv2
import numpy as np
import time
from mss import mss

def capture_screen_region(x, y, width, height):
    with mss() as sct:
        monitor = {"top": y, "left": x, "width": width, "height": height}
        screenshot = sct.grab(monitor)
        return np.array(screenshot)

def edge_detection(image):
    
    edges = cv2.GaussianBlur(image, (9,9), 0)
    
    return edges

def main():
    start_time = time.time()
    frame_count = 0

    while True:
        # Capture the screen 800 x 640 top left corner
        frame = capture_screen_region(0, 40, 800, 600)
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
        if cv2.waitKey(1) == 27:  # 27 is the 'ESC' key
            break

    # quit program
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
