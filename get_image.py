from utils import *
from PIL import Image

path = "images/"
url = "https://pytorch.org/docs/stable/nn.html"

image, image_file = get_img_from_url(url)

image.save(path + "pytorch.png")
image_file.close()


# upload the image to the bucket emulator
from firebase_admin import storage

bucket = storage.bucket()
blob = bucket.blob("images/pytorch.png")
blob.upload_from_filename(path + "pytorch.png")
