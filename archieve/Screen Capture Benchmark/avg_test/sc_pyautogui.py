import pyautogui
import time
import cv2
import numpy as np

def capture_screen_region(x, y, width, height):
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    return np.array(screenshot)

def main():
    initial_start_time = time.time()  # Keep track of the start time for the 90-second check
    start_time = initial_start_time
    frame_count = 0
    total_fps = 0

    while True:
        # Capture the screen 800 x 600 top left corner
        frame = capture_screen_region(0, 40, 800, 600)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Displaying the captured screen with edge detection
        cv2.imshow("Captured Screen", frame)

        frame_count += 1
        elapsed_time = time.time() - start_time
        total_elapsed_time = time.time() - initial_start_time  # Calculate total elapsed time
        
        # Calculate and display the FPS every second
        if elapsed_time > 1:
            current_fps = frame_count / elapsed_time
            print(f"FPS: {current_fps:.2f}")
            total_fps += current_fps
            start_time = time.time()
            frame_count = 0
        
        # Check for 'ESC' key press to exit the loop
        if cv2.waitKey(1) == 27:  # 27 is the 'ESC' key
            break

        # Stop the loop after 90 seconds
        if total_elapsed_time >= 90:
            break

    # Calculate and display the average FPS after 90 seconds
    average_fps = total_fps / 90
    print(f"Average FPS (90 seconds): {average_fps:.2f}")

    # quit program
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
