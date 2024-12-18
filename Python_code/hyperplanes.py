import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define the grid for plotting
x = np.linspace(-10, 10, 400)
y = np.linspace(-10, 10, 400)
X, Y = np.meshgrid(x, y)

# Define the hyperplanes: ax + by + cz + d = 0
def plane1(X, Y):
    return 2*X + Y - 2  # Example: 2x + y - z - 2 = 0

def plane2(X, Y):
    return Y + 2*Y - 4  # Example: y + 2z - 4 = 0

def plane3(X, Y):
    return X + 3*Y - 6  # Example: x + 3z - 6 = 0

def plane4(X, Y):
    return X - Y + 1    # Example: x - y + z + 1 = 0

# Traditional Japanese color palette
colors = ['#D7003A', '#33A6B8', '#E198B4', '#6A4C9C']  # Kurenai, Asagi, Momo-iro, Kikyo-iro

# Plot 1: Hyperplanes
fig1 = plt.figure(figsize=(12, 8))
ax1 = fig1.add_subplot(111, projection='3d')

# Plot each plane with the selected colors
ax1.plot_surface(X, Y, plane1(X, Y), alpha=0.7, rstride=100, cstride=100, color=colors[0])
ax1.plot_surface(X, Y, plane2(X, Y), alpha=0.7, rstride=100, cstride=100, color=colors[1])
ax1.plot_surface(X, Y, plane3(X, Y), alpha=0.7, rstride=100, cstride=100, color=colors[2])
ax1.plot_surface(X, Y, plane4(X, Y), alpha=0.7, rstride=100, cstride=100, color=colors[3])

# Remove axis labels and ticks
ax1.set_xticks([])
ax1.set_yticks([])
ax1.set_zticks([])
ax1.set_xlabel('')
ax1.set_ylabel('')
ax1.set_zlabel('')

# Set plot title
ax1.set_title('Intersection of Four Hyperplanes in $\mathbb{R}^3$')

# Plot 2: Normal Vectors
fig2 = plt.figure(figsize=(12, 8))
ax2 = fig2.add_subplot(111, projection='3d')

# Define normal vectors for each plane
normals = [
    (2, 1, -1),  # Normal vector for plane1
    (0, 2, -1),  # Normal vector for plane2
    (1, 3, -1),  # Normal vector for plane3
    (1, -1, 1)   # Normal vector for plane4
]

# Define a point on each plane (for simplicity, using the origin)
origin = np.array([0, 0, 0])

# Plot normal vectors with matching colors
for normal, color in zip(normals, colors):
    ax2.quiver(
        origin[0], origin[1], origin[2],  # Starting point
        normal[0], normal[1], normal[2],  # Direction
        length=5, color=color, linewidth=2, arrow_length_ratio=0.1
    )

# Set plot limits for better visualization
ax2.set_xlim([-10, 10])
ax2.set_ylim([-10, 10])
ax2.set_zlim([-10, 10])

# Remove axis labels and ticks
ax2.set_xticks([])
ax2.set_yticks([])
ax2.set_zticks([])
ax2.set_xlabel('')
ax2.set_ylabel('')
ax2.set_zlabel('')

# Set plot title
ax2.set_title('Normal Vectors of the Hyperplanes in $\mathbb{R}^3$')

# Show plots
plt.show()
