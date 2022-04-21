'''
How to run: Open terminal and run the command:-> python image_resize.py
'''

from io import BytesIO
import base64
from flask import Flask, request, jsonify
from requests import get as get_request
from os import stat
from PIL import Image


app = Flask(__name__)  # Flask App

MIN_SIZE = 32 # Smallest dimension must not be less than 32 while performing in loop
STEP = 32 # Decrease the pixels by 32 while in loop


def open_image(path:str = False)-> tuple:
    '''
    Open the image
    args:
        url: Url of image over http / https 
    return:
        (PIL Image object, size of image in kb)   
    '''
    if isinstance(path,str):
        # if : return Image.open(path), stat(path).st_size / 1024
        buffer = BytesIO(get_request(path).content)
        return Image.open(buffer), buffer.getbuffer().nbytes / 1024


def resize(image:Image, current_size:tuple, new_width_height:float)->Image:
    '''
    Resize and return Given Image
    args:
        image: Image object
        current_size: Image size as (width, height)
        new_width_height = Reshaped image's width and height. If integer is given, it'll keep the aspect ratio as it is by shrinking the Bigger dimension (width or height) to the max of new_width_height  and then shring the smaller dimension accordingly 
    '''
    fixed_size = True if isinstance(new_width_height, int) else False
    w, h = current_size

    if fixed_size:
        if h > w:
            fixed_height = new_width_height
            height_percent = (fixed_height / float(h))
            width_size = int((float(w) * float(height_percent)))
            image = image.resize((width_size, fixed_height), Image.ANTIALIAS) # # Try Image.NEAREST

        else:
            fixed_width = new_width_height
            width_percent = (fixed_width / float(w))
            height_size = int((float(h) * float(width_percent)))
            image = image.resize((fixed_width, height_size), Image.ANTIALIAS) 

    else:
        w, h = int(new_width_height[0]), int(new_width_height[1])
        image = image.resize((w,h), Image.NEAREST)

    return image


def resize_under_kb(image:Image, size:tuple, size_kb: float, desired_size:float)-> Image:
    '''
    Resize the image under given size in KB
    args:
        Image: Pil Image object
        size: Image size as (width, height)
        size_kb: Current size of image in kb
        desired_size: Final desired size asked by user
    '''
    new_width_height = max(size) - STEP # Decrease the pixels for first pass

    while new_width_height > MIN_SIZE and size_kb > desired_size: # either the image reaches minimun dimension possible or the desired possible size
        image = resize(image, size, new_width_height)

        image.save("test.jpeg", quality = 100, optimize = True) # Does not save but acts like an image saved to disc
        size_kb = stat("test.jpeg").st_size / 1024

        size = image.size # Current resized pixels
        new_width_height = max(size) - STEP # Dimensions for next iteration

    return image


def resize_in_percentages(image, size:tuple, percentage:float):
    '''
    args:
        image: PIL image object
        size: Image size as (width, height)
        percentage: Reduce the image size / quality by this much %. 30% means the resulting image will be of size 70KB if original size was 100KB
    '''
    w,h = size
    return resize(image, size, (w * percentage/ 100, h * percentage / 100))


@app.route('/resize', methods = ['POST'])
def resize_image():
    """
    Resize Image based on user specified parameters
    """
    try:
        buffer = BytesIO(request.files["img"].read())
        image = Image.open(buffer)
        size = image.size # width, height
        size_kb = buffer.getbuffer().nbytes / 1024

         # mode = image.mode # RGB, RGBA, L
        # format_ = image.format # JPEG, PNG, JPG etc

        percentage = request.form.get('percentage')
        desired_size = request.form.get('desired_size') # must be a Tuple / list

        custom_width_height = request.form.get('custom_wh')
        if isinstance(custom_width_height, str):
            custom_width_height  = custom_width_height.split(',')


    except Exception as e:
        return jsonify([f"Image Reading error: {e}"]),400

    try:
        if percentage: image = resize_in_percentages(image, size, float(percentage))
        if desired_size: image = resize_under_kb(image, size, size_kb, float(desired_size))
        if custom_width_height: image = resize(image, size, custom_width_height)
        
        buffer = BytesIO()
        image.save(buffer, "jpeg", optimize = True, quality = 100) # Convert to JPEG and load without saving to disk
        
        buffer.seek(0)
        data = buffer.read()
        data = base64.b64encode(data).decode()

        return jsonify({'img': data})
            
    except Exception as e:
         return jsonify([f"Resizing error: {e}"]),400


if __name__ == "__main__":
    app.run(debug = True, host = '0.0.0.0')
