from io import BytesIO
from pdf2image import convert_from_path
from PIL import Image

def pdf_to_page_imgs(file_path: str) -> list:
    # Convert PDF to a list of PIL Image objects, one for each page
    images_of_pages = convert_from_path(file_path)

    # Initialize a list to store the binary images
    image_bytes_list = []

    # Save each page as an image file
    for page_num, page in enumerate(images_of_pages, 1):
        # Convert the page to grayscale first
        gray_image = page.convert('L')  # 'L' mode means grayscale

        # Apply a binary threshold to the grayscale image
        image_binary = gray_image.point(lambda x: 0 if x < 128 else 255, '1')  # Convert to binary (1-bit pixels)
        # Convert the `Image` object into a bytes-like object using BytesIO
        image_buffer = BytesIO()
        image_binary.save(image_buffer, format='PNG')  # Save the image in PNG format (or other desired format)
        image_buffer.seek(0)  # Move to the start of the BytesIO buffer

        # Append to the list
        image_bytes_list.append(image_buffer.getvalue())

    # Return the list of binary images
    return image_bytes_list

def pdf_to_combined_img(file_path: str):
    """
    Converts a PDF file into a single long image where all the pages of the PDF
    are vertically stacked. The resulting image is returned as binary data.

    Args:
        file_path (str): The path to the PDF file to be converted.

    Returns:
        bytes: Binary data of the combined image in PNG format.

    Example:
        file_path = "example.pdf"
        combined_image_bytes = pdf_to_combined_img(file_path)

        # Save the combined image to verify
        with open("combined_image.png", "wb") as image_file:
            image_file.write(combined_image_bytes)
    """
    # Convert PDF to a list of PIL Image objects, one per page
    images_of_pages = convert_from_path(file_path)

    # Convert each page to grayscale and binary, and gather dimensions
    processed_images = []
    total_height = 0
    max_width = 0

    for page in images_of_pages:
        # Convert the page to grayscale
        gray_image = page.convert('L')  # 'L' mode means grayscale

        # Apply binary threshold
        image_binary = gray_image.point(lambda x: 0 if x < 128 else 255, '1')  # Binary image

        # Collect processed image
        processed_images.append(image_binary)

        # Update total height and maximum width
        total_height += image_binary.height
        max_width = max(max_width, image_binary.width)

    # Create a blank "tall" image with combined dimensions
    combined_image = Image.new("1", (max_width, total_height), color=1)  # '1' mode for binary, default white

    # Paste each binary image onto the tall image
    current_y = 0
    for image in processed_images:
        combined_image.paste(image, (0, current_y))
        current_y += image.height

    # Convert the combined image to binary data
    image_buffer = BytesIO()
    combined_image.save(image_buffer, format='PNG')  # Save as PNG
    image_buffer.seek(0)

    # Return the binary image data
    return image_buffer.getvalue()