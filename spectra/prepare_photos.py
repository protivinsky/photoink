import os
from PIL import Image
import numpy as np


# 6-color palette for GDEP073E01 Spectra E6 display
palette = [
    (0, 0, 0),       # Black
    (255, 255, 255), # White
    (255, 255, 0),   # Yellow
    (255, 0, 0),     # Red
    (0, 0, 255),     # Blue
    (0, 255, 0),     # Green
]


def resize_and_truncate(image, target_size=(800, 480)):
    """Resize the image to fit the target size and truncate symmetrically"""
    # Calculate the aspect ratio
    aspect_ratio = image.width / image.height
    target_aspect_ratio = target_size[0] / target_size[1]

    # Resize the image proportionally
    if aspect_ratio > target_aspect_ratio:
        # Resize by height and then truncate the width symmetrically
        resized_image = image.resize((int(target_size[1] * aspect_ratio), target_size[1]), Image.LANCZOS)
        left_margin = (resized_image.width - target_size[0]) // 2
        right_margin = (resized_image.width - target_size[0] + 1) // 2
        top_margin = 0
        bottom_margin = 0

    else:
        # Resize by width and then truncate the height symmetrically
        resized_image = image.resize((target_size[0], int(target_size[0] / aspect_ratio)), Image.LANCZOS)
        left_margin = 0
        right_margin = 0
        top_margin = (resized_image.height - target_size[1]) // 2
        bottom_margin = (resized_image.height - target_size[1] + 1) // 2

    # Truncate symmetrically from both sides to fit the target size
    truncated_image = resized_image.crop((left_margin, top_margin, resized_image.width - right_margin, resized_image.height - bottom_margin))
    return truncated_image


def get_image_data(file):
    """Resize and convert an image to the 7-color palette and return the image data"""
    image = Image.open(file)
    # image = image.resize((800, 480))
    image = resize_and_truncate(image)
    palette_img = Image.new('P', (1, 1))
    palette_img.putpalette([col for p in palette for col in p] + [0] * (256 - len(palette)) * 3)
    # Convert the image to the custom palette
    image = image.convert('RGB').quantize(palette=palette_img)
    image_data = np.array(image)
    # Number 4 is not used in Spectra, blue and green are 5 and 6
    image_data = np.where(image_data < 4, image_data, image_data + 1)
    return image_data


if __name__ == "__main__":
    source_dir = "photos"
    dest_dir = "ready"
    for filename in os.listdir(source_dir):
        print(f"Processing {filename}")
        image_data = get_image_data(os.path.join(source_dir, filename))
        colors = image_data[:, 1::2] + 16 * image_data[:, ::2]
        byte_seq = colors.tobytes()
        dest_fullname = f'{dest_dir}/{filename.split(".")[0]}.bin'
        with open(dest_fullname, 'wb') as f:
            f.write(byte_seq)

