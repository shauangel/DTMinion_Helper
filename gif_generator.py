import numpy as np
from PIL import Image
import imageio

# Load the two input frames
img1 = Image.open("images/Boom-0.png").convert("RGBA")
img2 = Image.open("images/Boom-1.png").convert("RGBA")

# Convert to numpy for interpolation
arr1 = np.array(img1).astype(np.float32)
arr2 = np.array(img2).astype(np.float32)

# Simple linear interpolation for in-between frame
interpolated = (arr1 * 0.5 + arr2 * 0.5).astype(np.uint8)
interpolated_img = Image.fromarray(interpolated)

# Create smooth sequence: open → halfway → closed → halfway → open
frames = [img1, interpolated_img, img2, interpolated_img, img1]

# Save as smoother blinking GIF
smooth_gif_path = "images/blinking_smooth.gif"

natural_durations = [500, 100, 120, 100, 1500]  # open → half → closed → half → open

# Save the updated "natural" blinking gif
frames[0].save(
    smooth_gif_path,
    save_all=True,
    append_images=frames[1:],
    duration=natural_durations,
    loop=0,
    disposal=2
)
