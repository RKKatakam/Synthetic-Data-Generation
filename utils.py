
import base64
import io
import time
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

Image.MAX_IMAGE_PIXELS = None

def get_img_from_url(url):
    options = Options()
    options.add_argument("--window-size=1920,1080")  
    options.add_argument("--start-maximized")
    options.add_argument("--headless=new")  
    options.add_argument("--disable-gpu")

    # Use a context manager for automatic driver cleanup
    with webdriver.Chrome(options=options) as driver: 
        driver.get(url)

        # Allow the page to fully load (adjust the time if necessary)
        time.sleep(2)  
        
        # Use JavaScript to get the full width and height of the webpage
        width = driver.execute_script("return Math.max( document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth );")
        height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")

        # Set the window size to match the entire webpage
        driver.set_window_size(width, height)

        # Optimized way to capture the entire page
        image_base64 = driver.get_screenshot_as_base64()
        
        # Efficient base64 decoding and image processing
        img_bytes = base64.b64decode(image_base64)
        img_file = io.BytesIO(img_bytes)
        image = Image.open(img_file)
    
    return image, img_file