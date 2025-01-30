import cv2
import pytesseract
import os
import requests
import numpy as np

# Language mapper from ISO standard to OCR
# refer to language files here: https://github.com/tesseract-ocr/tessdata
lang_map = {
    'en': 'eng',
    'de': 'deu',
    'bu': 'bul',
    'ru': 'rus',
    'ro': 'ron',
}

class OCRProcessor:
    def __init__(self, config: str):
        """
        Initialize the OCR Processor.

        Args:
            tessdata_prefix (str): Path to the Tesseract language data files (TESSDATA_PREFIX).
            language (str): Language to use for OCR. Default is English ('eng', 'deu', 'bul').
        """
        self.config = config
        os.environ['TESSDATA_PREFIX'] = self.config['tessdata_prefix']
        self.download_lang_files()

    def download_lang_files(self):
        for lang in self.config['document_languages']:
            ocr_lang_code = lang_map[lang]
            url = f"https://github.com/tesseract-ocr/tessdata/raw/main/{ocr_lang_code}.traineddata"
            download_path = f"{self.config['tessdata_prefix']}{ocr_lang_code}.traineddata"

            # Download the language file if needed
            self.download_language_file(url, download_path)

    def preprocess(self, image):
        """
        Preprocess the image for better OCR results.

        Args:
            image (numpy.ndarray): The input image.

        Returns:
            numpy.ndarray: The preprocessed image.
        """

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
        kernel_sharpening = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(denoised, -1, kernel_sharpening)
        _, thresholded = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        kernel_erosion = np.ones((2, 2), np.uint8)
        eroded_image = cv2.erode(thresholded, kernel_erosion, iterations=1)
        return eroded_image



    def load_img_file_and_perform_ocr(self, image_path, language = "deu"):
        """
        Perform OCR on the given image.

        Args:
            image_path (str): Path to the input image.
            language (str): Language to use for OCR.

        Returns:
            str: Extracted text from the image.
        """
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found at {image_path}")

        # Preprocess the image
        preprocessed_image = self.preprocess(image)

        # Perform OCR
        text = pytesseract.image_to_string(preprocessed_image, lang=language) # TODO, this should be trying all languages
        return text.strip()

    def perform_ocr_from_image(self, image, language = "deu"):
        # Preprocess the image
        preprocessed_image = self.preprocess(image)

        # Perform OCR
        text = pytesseract.image_to_string(preprocessed_image, lang=language) # TODO, this should be trying all languages
        return text.strip()


    def remove_extra_spaces(self, text_list):
        """
        Remove extra spaces from a list of text strings.

        Args:
            text_list (list of str): The list of text strings to clean.

        Returns:
            list of str: Cleaned text strings.
        """
        return [' '.join(text.split()) for text in text_list]

    def download_language_file(self, url, download_path):
        """
        Download the specified Tesseract language file if it does not already exist.

        Args:
            url (str): URL of the Tesseract language file.
            download_path (str): Local path to save the file.
        """
        if not os.path.exists(download_path):
            print(f"File not found at {download_path}. Downloading...")
            response = requests.get(url)
            response.raise_for_status()
            with open(download_path, 'wb') as f:
                f.write(response.content)
            print(f"File downloaded and saved to {download_path}.")
        else:
            print(f"File already exists at {download_path}. No download needed.")

