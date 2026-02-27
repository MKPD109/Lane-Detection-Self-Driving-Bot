from PIL import Image
import numpy as np

def gaussian_kernel(size, sigma=1):
    """
    Generates a Gaussian kernel.
    """
    size = int(size) // 2
    x, y = np.mgrid[-size:size+1, -size:size+1]
    normal = 1 / (2.0 * np.pi * sigma**2)
    g =  np.exp(-((x**2 + y**2) / (2.0*sigma**2))) * normal
    return g    

def gaussian_blur(image, kernel_size, sigma):
    """
    Applies Gaussian blur to a given image.
    """
    kernel = gaussian_kernel(kernel_size, sigma)
    d = int(kernel_size // 2)
    gaussian = np.zeros_like(image, dtype=float)

    # Padding the image to handle borders
    padded_image = np.pad(image, ((d, d), (d, d)), mode='reflect')
    
    # Convolution
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            x = i + d
            y = j + d
            gaussian[i, j] = np.sum(padded_image[x - d:x + d + 1, y - d:y + d + 1] * kernel)
    
    return gaussian


image_path = 'C:/Users/MKPD/Downloads/test1/input.jpg'

# Load the image
original_image = Image.open(image_path)

# Convert the image to grayscale
grayscale_image = original_image.convert('L')

# Convert the grayscale image to a numpy array
image_array = np.array(grayscale_image)

# Apply Gaussian blur
blurred_image_array = gaussian_blur(image_array, kernel_size=3, sigma=1)

# Convert the array back to an image
blurred_image = Image.fromarray(np.uint8(blurred_image_array))

# Save the blurred image
output_path = 'C:/Users/MKPD/Downloads/test1/blurred_output.jpg'
blurred_image.save(output_path)
print(f"Blurred image saved to {output_path}")
