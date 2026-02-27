import pyautogui
import time
import cv2
import numpy as np

def capture_screen_region(x, y, width, height):
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    return np.array(screenshot)

def main():
    start_time = time.time()
    frame_count = 0

    while True:
        # Capture the screen 800 x 640 top left corner
        frame = capture_screen_region(0, 40, 800, 640)
        # Convert it from BGR(Blue, Green, Red) to
        # RGB(Red, Green, Blue)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Displaying the captured screen with edge detection
        cv2.imshow("Captured Screen", frame)

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
