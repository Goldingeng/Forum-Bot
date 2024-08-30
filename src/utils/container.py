from ..config import BAD_WORDS
import io
import cv2
import numpy as np
from PIL import Image
import re

URL_PATTERN = re.compile(r'https?://(?!t\.me\/)[\w./?=&-]+')

def contains_bad_words(text):
    if text:
        return any(bad_word in text.lower() for bad_word in BAD_WORDS)

def contains_forbidden_links(text):
    if text:
        return bool(URL_PATTERN.search(text))

def contains_nudity(image_data):
    """ Проверка изображения на наличие неподобающего контента. """
    try:

        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        np_image = np.array(image)


        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        

        hsv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2HSV)
        

        skin_mask = cv2.inRange(hsv_image, lower_skin, upper_skin)
        

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
        

        skin_pixel_count = np.sum(skin_mask > 0)
        total_pixel_count = np_image.shape[0] * np_image.shape[1]
        

        if (skin_pixel_count / total_pixel_count) > 0.1:
            return True
        

        gray_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray_image, 100, 200)
        edge_pixel_count = np.sum(edges > 0)
        
        if (edge_pixel_count / total_pixel_count) > 0.05:
            return True


        for symbol in ['swastika_pattern']:
            if contains_specific_symbol(np_image, symbol):
                return True
        
        return False

    except Exception as e:
        print(f"Error in contains_nudity: {e}")
        return False

def contains_specific_symbol(np_image, symbol):
    """Проверка наличия конкретного символа в изображении с использованием сопоставления шаблонов."""

    symbol_template = cv2.imread(f'{symbol}_template.png', cv2.IMREAD_GRAYSCALE)
    if symbol_template is None:
        print(f"Ошибка загрузки шаблона: {symbol}_template.png")
        return False


    gray_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
    

    result = cv2.matchTemplate(gray_image, symbol_template, cv2.TM_CCOEFF_NORMED)
    

    threshold = 0.8
    loc = np.where(result >= threshold)
    

    if len(loc[0]) > 0:
        return True

    return False