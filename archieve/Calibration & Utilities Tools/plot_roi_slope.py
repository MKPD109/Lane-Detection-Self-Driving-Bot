import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from matplotlib.patches import Polygon

# Load your image
image_path = 'E:\Downloads\Slope.png'  
#image's path
img = mpimg.imread(image_path)

# Define vertices 
vertices = np.array([[10, 500], [28, 360], [350, 320], [450, 320], [750, 360], [800, 500]], np.int32)
vertices = vertices.reshape((-1, 1, 2))  # Reshape for Polygon patch

# Plotting
fig, ax = plt.subplots()
ax.imshow(img)

# Create a Polygon patch from the vertices and add it to the plot
polygon = Polygon(vertices.reshape(-1, 2), linewidth=1, edgecolor='r', facecolor='none')
ax.add_patch(polygon)

# Display the plot
plt.show()
