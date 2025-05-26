
from PIL import Image
import pytesseract
import sys

image_path = sys.argv[1]
img = Image.open(image_path)
text = pytesseract.image_to_string(img, config='--psm 7')
print(text.strip())
