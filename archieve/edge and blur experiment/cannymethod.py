import cv2
def edge_detection(image_path):
    # Load the image from the file path
    image = cv2.imread(image_path)
    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Canny edge detector
    edges = cv2.Canny(gray_image, 100, 250)    
    return edges

edges = edge_detection('C:/Users/MKPD/Downloads/test1/blurred_output.jpg')
cv2.imshow('Edges', edges)
cv2.waitKey(0)
cv2.destroyAllWindows()
