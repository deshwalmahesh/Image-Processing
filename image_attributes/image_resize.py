def JPEGSaveWithTargetSize(im, filename, target):
   """Save the image as JPEG with the given name at best quality that makes less than "target" bytes"""
   # Min and Max quality
   Qmin, Qmax = 25, 96
   # Highest acceptable quality found
   Qacc = -1
   while Qmin <= Qmax:
      m = math.floor((Qmin + Qmax) / 2)

      # Encode into memory and get size
      buffer = io.BytesIO()
      im.save(buffer, format="JPEG", quality=m)
      s = buffer.getbuffer().nbytes

      if s <= target:
         Qacc = m
         Qmin = m + 1
      elif s > target:
         Qmax = m - 1

   # Write to disk at the defined quality
   if Qacc > -1:
      im.save(filename, format="JPEG", quality=Qacc)
   else:
      print("ERROR: No acceptble quality factor found", file=sys.stderr)


'''
Steps to resize:

1. Try changing the parameter "new_width_height". Lower the number, lower the size
2. Try changing the parameter "save_extension" from png to jpg 
3. Try changing the quality from 100 to below any number
4. set Optimize = True / False based on your requirements
'''


from PIL import Image
import os

def resize(path, new_width_height = 1920, save_extension = "png", quality = 100, optimize = True):
  '''
  Resize and return Given Image
  args:
    path: Image Path: Path of Imaghe relative to the code where it is being deployed
    new_width_height = Reshaped image's width and height. If integer is given, it'll keep the aspect ratio as it is by shrinking the Bigger dimension (width or height) to the max of new_width_height  and then shring the smaller dimension accordingly 
    save_image = Whether to save the image or not
    convert_RGB: Whether to Convert the RGBA image to RGB (by default backgroud is white)
  '''
  name = path.split('/')[-1].split(".")[0]
  out_path = "./output/"+name + "." +save_extension
  image = Image.open(path)
  w, h = image.size

  fixed_size = True if isinstance(new_width_height, int) else False

  if fixed_size:
    if h > w:
      fixed_height = new_width_height
      height_percent = (fixed_height / float(h))
      width_size = int((float(w) * float(height_percent)))
      image = image.resize((width_size, fixed_height), Image.ANTIALIAS)

    else:
      fixed_width = new_width_height
      width_percent = (fixed_width / float(w))
      height_size = int((float(h) * float(width_percent)))
      image = image.resize((fixed_width, height_size), Image.ANTIALIAS) # Try Image.ANTIALIAS inplace of Image.NEAREST

  else:
    image = image.resize(new_width_height)

  image.save(out_path, quality = quality, optimize = optimize)
