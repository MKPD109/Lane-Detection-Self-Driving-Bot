import cv2
import numpy as np
import time
from mss import mss
from statistics import mean
from numpy.linalg import lstsq
from numpy import ones,vstack
from directkeys import PressKey, ReleaseKey, W,A,D,S

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

def draw_lanes(img, lines, color=[0, 255, 255], thickness=3):
    """
    Identifies and draws lanes on the given image based on detected lines.

    Function Args:
    - img: The input image on which lanes are to be drawn.
    - lines: The lines detected in the image.
    Returns:
    - Coordinates of the two main lanes detected.
    """
    try:
        # Extract y-coordinates from the detected lines to determine the horizon level.
        ys = [coord for i in lines for coord in [i[0][1], i[0][3]]]
        min_y = min(ys)
        max_y = 600  # Assuming a fixed value for the maximum y-coordinate, as it is the game resoloution in Y coordinate

        # Calculate line equations for detected lines and filter relevant ones.
        # Create a dictionary to store the calculated line equations for each detected line
        line_dict = {}
        # Loop through each line detected by the Hough transform
        # modified from http://stackoverflow.com/questions/21565994/method-to-return-the-equation-of-a-straight-line-given-two-points
        for idx, line in enumerate(lines):
            # For each detected line, it provides two sets of x,y coordinates representing 
            # the start and end points of the line segment.
            for xyxy in line:

                # Extract the x and y coordinates of the start and end points of the line segment.
                # x_coords contains the x-values of the start and end points of the line.
                # y_coords contains the y-values of the start and end points of the line.
                x_coords, y_coords = (xyxy[0], xyxy[2]), (xyxy[1], xyxy[3])
                
                # Construct the A matrix for the least squares method. 
                # The A matrix is constructed such that each row corresponds to the x coordinate 
                # of a point and a constant value of 1. This format is used to solve for the slope 
                # (m) and y-intercept (c) of the line equation y = mx + c using the least squares method.                
                A = vstack([x_coords, ones(len(x_coords))]).T

                # Use the least squares method to compute the slope (m) and y-intercept (c) 
                # of the best-fit line for the provided points. The lstsq function returns 
                # multiple values, but we're primarily interested in the first value which contains m and c.
                m, c = lstsq(A, y_coords, rcond=None)[0]  # Line equation: y = mx + c

                # Compute new endpoints for the line based on the detected horizon.
                x1, x2 = int((min_y-c) / m), int((max_y-c) / m)

                # Store the calculated slope (m), y-intercept (c), and line segment coordinates 
                # in the line_dict dictionary for further processing or filtering.
                line_dict[idx] = [m, c, [x1, min_y, x2, max_y]]

        # Group similar lines based on slope and y-intercept.
        final_lanes = {}
        for idx, (m, c, line) in line_dict.items():
             # If 'final_lanes' is empty, add the first line.
            if not final_lanes:
                final_lanes[m] = [[m, c, line]]
            else:
                # Assume the line is not grouped initially
                grouped = False

                # Iterate over the existing lines in 'final_lanes'.
                for key_m, group in final_lanes.items():
                    # Check if the current line's slope and y-intercept are similar to an existing group's.
                    # The slope should be within 20% (1.2x and 0.8x) of an existing line's slope.
                    # The y-intercept should also be within 20% of an existing line's y-intercept.
                    if abs(key_m*1.2) > abs(m) > abs(key_m*0.2) and \
                       abs(group[0][1]*1.2) > abs(c) > abs(group[0][1]*0.2):
                        
                        # If conditions are met, append the current line to the existing group.
                        final_lanes[key_m].append([m, c, line])
                        # Indicate that the line has been grouped.
                        grouped = True
                        break
                
                # If the line was not grouped with any existing groups, create a new group for it.   
                if not grouped:
                    final_lanes[m] = [[m, c, line]]

        # From the previously grouped lines in 'final_lanes', we want to determine 
        # the two most dominant lanes. These are often the left and right lanes 
        # in a typical road scenario.

        # Create a list of tuples containing each lane's slope (as an identifier) 
        # and the count of lines grouped under that slope. 
        # The idea is that a dominant lane will have more lines grouped under it.
        top_lanes = sorted([(k, len(v)) for k, v in final_lanes.items()], key=lambda x: x[1], reverse=True)[:2]
        
        # Extract the slope identifiers for the two most dominant lanes.
        lane1_id, lane2_id = top_lanes[0][0], top_lanes[1][0]

        # Define a function to average out the coordinates of the lines 
        # within a given lane group. This will provide a single representative 
        # line for that lane.
        def average_lane(lane_data):
            # Extract the start and end coordinates for all the lines in the lane group.
            x1s, y1s, x2s, y2s = zip(*[data[2] for data in lane_data])
            
            # Calculate the mean of the start and end coordinates 
            # to get the average line for the lane group.
            return int(mean(x1s)), int(mean(y1s)), int(mean(x2s)), int(mean(y2s))

        # Get the averaged coordinates for the two dominant lanes.
        lane1_coords, lane2_coords = average_lane(final_lanes[lane1_id]), average_lane(final_lanes[lane2_id])

        # Return the averaged coordinates, which will be used to draw 
        # the representative lines for the two dominant lanes.
        return lane1_coords, lane2_coords,lane1_id, lane2_id

    # Handle any exceptions that may arise during the lane detection process.
    except Exception as e:
        print(f"Error in draw_lanes: {e}")



# Main image processing function
def process_img(original_image):
    # Convert the RGB image to a grayscale image to simplify analysis.
    processed_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    
    # Use Canny edge detection to detect edges in the image.
    # This will highlight the structural features, such as lanes.
    # original th1 = 200 th2 = 300
    processed_img = cv2.Canny(processed_img, threshold1=150, threshold2=300)
    
    # Apply a Gaussian blur to the image to reduce noise and make edges smoother.
    # This helps in achieving better results in edge detection.
    processed_img = cv2.GaussianBlur(processed_img, (3,3), 0)
    
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
    m1 = 0
    m2 = 0
    try:
        # Get the two main lanes from the detected lines.
        l1, l2,m1,m2= draw_lanes(original_image, lines)
        
        # Draw these main lanes on the original image for visualization.
        cv2.line(original_image, (l1[0], l1[1]), (l1[2], l1[3]), [0,0,255], 30)  # Drawing in red color
        cv2.line(original_image, (l2[0], l2[1]), (l2[2], l2[3]), [0,0,255], 30)
    except Exception as e:
        # If there's any error in drawing main lanes, log the error.
        print(str(e))
        pass
    
    try:
        # Draw all detected lines on the processed image for visualization.
        for coords in lines:
            coords = coords[0]
            try:
                cv2.line(processed_img, (coords[0], coords[1]), (coords[2], coords[3]), [255,0,0], 3)  # Drawing in blue color
            except Exception as e:
                # If there's any error in drawing a specific line, log the error.
                print(str(e))
    except Exception as e:
        pass
    
    # Return the processed image with all detected lines 
    # and the original image with the two main lanes drawn on it.
    return processed_img, original_image,m1,m2

def straight():
    PressKey(W)
    ReleaseKey(A)
    ReleaseKey(D)

def left():
    PressKey(A)
    ReleaseKey(W)
    ReleaseKey(D)
    ReleaseKey(A)

def right():
    PressKey(D)
    ReleaseKey(A)
    ReleaseKey(W)
    ReleaseKey(D)


def main():
    start_time = time.time()
    frame_count = 0

    while True:
        # Capture a portion of the screen
        frame = capture_screen_region(0, 40, 800, 600)
        # Process the captured frame (edge detection, ROI, line detection)
        processed_frame, original_frame,m1,m2 = process_img(frame)
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

        
        if m1 < 0 and m2 < 0:
            print(m1,m2,"right")
        elif m1 > 0  and m2 > 0:
            print(m1,m2,"left") 
        else:
            print(m1,m2,"stright")
        """
        if m1 < 0 and m2 < 0:
            right()
        elif m1 > 0  and m2 > 0:
            left()
        else:
            straight()
        
        """""
        # Exit loop and release the key if 'ESC' key is pressed
        if cv2.waitKey(1) == 27:
            break
        
    # Close all OpenCV windows after exiting the loop
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()