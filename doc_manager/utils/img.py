from PIL import Image, ExifTags
import os


def resize_image_to_size(image_path, output_path, max_size_mb=5):
    """
    Resize and compress an image to ensure it is just under the specified size in MB.

    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the resized and compressed image.
        max_size_mb (float): Maximum image size in MB (default: 5).

    Returns:
        bool: True if the resize and compression were successful, False otherwise.
    """
    max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes

    try:
        with Image.open(image_path) as img:
            img = correct_exif_orientation(img)
            # Ensure the image uses RGB or keep the original mode for compatibility
            img = img.convert("RGB") if img.mode != "RGB" else img

            # Initial save with high quality
            img.save(output_path, "JPEG", quality=95)

            # Check the initial size
            while os.path.getsize(output_path) > max_size_bytes:
                # Calculate scaling factor
                scaling_factor = (max_size_bytes / os.path.getsize(output_path)) ** 0.5

                # New dimensions
                new_width = int(img.width * scaling_factor)
                new_height = int(img.height * scaling_factor)

                # Resize and save with lower quality incrementally
                img = img.resize((new_width, new_height), Image.LANCZOS)
                img.save(output_path, "JPEG", quality=85)  # Adjust quality

            return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def correct_exif_orientation(img):
    """
    1. **EXIF Orientation Data**: Many images contain metadata called EXIF,
    which includes orientation information about how the image should be displayed.
    If the image contains an EXIF tag for orientation and this tag is not properly handled
    when processing the image, it might result in unintended transformations (like flipping or rotation)
    :param img:
    :return:
    """
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == "Orientation":
                break
        exif = img._getexif()
        if exif and orientation in exif:
            if exif[orientation] == 3:  # 180-degree rotation
                img = img.rotate(180, expand=True)
            elif exif[orientation] == 6:  # 90-degree rotation
                img = img.rotate(270, expand=True)
            elif exif[orientation] == 8:  # 270-degree rotation
                img = img.rotate(90, expand=True)
    except Exception:
        pass
    return img
