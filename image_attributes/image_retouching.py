import cv2
import numpy as np

def gamma_correction(image:np.ndarray, gamma:float = 1.0, auto_gamma:bool = False, mid:float = False)->np.ndarray:
    '''
    Non Linear Tranformation of Pixels means each pixel will be transformed according to it's own initial value. Used in changing the Brightness of the image
    new_pixel_value = ((original_value / 255)^ gamma) * 255
    args:
        image: Numpy Array of Image
        gamma: Gamma value to be applied
        auto_gamma: Whether to use auto Gamma Correction
        mid: Mid point of values to consider. Applies only when auto_gamma is True
    '''
    if auto_gamma and mid: return auto_gamma_correction(image, mid)

    lut = np.empty((1,256), np.uint8) # Create a lookup table because we need value changes only in range 0-255
    
    for i in range(256):
        lut[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255) # change the original value by a factor of Gamma
    return cv2.LUT(image, lut)


def auto_gamma_correction(image:np.ndarray, mid:float = 0.5)->np.ndarray:
    '''
    Infer the Gamma value using: gamma = log(mid*255)/log(mean)
    args:
        image: nummby BGR image
        mid: Mid point of values to consider
    '''
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hue, sat, val = cv2.split(hsv)

    mean = np.mean(val) # Mean pixel value of "value" channel
    gamma = math.log(mid*255)/math.log(mean) # Infer Gamma
    
    val_gamma = np.power(val, gamma).clip(0,255).astype(np.uint8) # gamma correction on value channel

    hsv_gamma = cv2.merge([hue, sat, val_gamma]) # Merge the 3 channels
    return cv2.cvtColor(hsv_gamma, cv2.COLOR_HSV2BGR)


def change_brightness_contrast(image, alpha:float = 1, beta:float = 0,)-> np.ndarray:
    '''
    Contrast is defined as the separation between the darkest and brightest areas of the image
    Brightness: Amount of Whiteness or Blackness present in a pixel. Brightness is Subjective and can not be calculated (but can be scaled in %) but you can calculate Luminance
    
    Pixel g(i,j) can be represented as: g(x) = α * f(x) + β or more precisely: α * f(i,j) + β  where: alpha == gain == contrast  AND beta == bias == brightness
    It means adding / subtracting (adding < 0) a value to all the pixels in the image will increase / decrease the Brightness and multiplying/dividing(multiplying by a value < 1) will
    control the Contrast
    args:
        image: Image as numpy array with BGR format
        alpha: Amount of contrast you want to change
        beta: Amount of brightness you want to change
    '''
    return cv.convertScaleAbs(image, alpha=alpha, beta=beta) # can also use a nested loop


def change_sharpness(image:np.ndarray, kernel_size:tuple=(5, 5), sigma:float=1.0, amount:float=1.0, threshold:float=0, return_minimal:bool = True)-> np.ndarray:
    '''
    Sharpness is edge contrast i.e. the contrast along edges in a photo. Increase sharpness, increase the contrast only along/near edges while leaving smooth areas alone
    Use Gaussian smoothing filter and subtract the smoothed version from the original image in a weighted way so the values of a constant area remain constant
    args:
        image: Numpy image array in BGR format
        kernel_size: Size of Gaussian Filter to smoothen the image
        sigma: STD or sigma value to be used for Smoothening
        amount: amount of Sharpness to be aplied to the image. More amount -> More sharpened image
        threshold: Threshold for the low-contrast mask. Pixels for which the difference between the input and blurred images is less than threshold will remain unchanged
        return_minimal: Wheturn the minimal sharpened image or the more processed version of it
    return:
        numpy array of BGR format    
    '''
    
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred # Weighted Subtracted Version
    
    if return_minimal: return sharpened

    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
        
    return sharpened


def change_hue_saturation_value(image:np.ndarray, h_a:float = 1,s_a:float = 1,v_a:float = 1 ):
    '''
    Hue == Main indication of color. It is the value actually telling you which color it is or the value that lets you go "red" when you see a red object. A pure Hue is completely saturated, meaning no white light is added
    Saturation == Chroma == Intensity of a color (Hue) and higher the saturation of a color, the more vivid it is. The lower the saturation of a color, the closer it is to gray
    Value == Lightness == Tone == Amplitude of colour. Colour with low value is close to black, while one with high value is close to white. 
    
    args:
        image: Numpy array of BGR format
        h_a: Hue amount to alter
        s_a: Saturation amount to alter
        v_a: Value amount to alter
    '''
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    h += h_a # change hue
    s += s_a # change saturation
    v += v_a # change value or lightness
    return cv2.cvtColor(cv2.merge((h, s, v)), cv2.COLOR_HSV2BGR) # Merge altered H-S-V -> convert to BGR



def apply_hist_equ(image:np.ndarray, CLAHE:bool = True, **kwargs)-> np.ndarray:
    '''
    Apply Histogram Equalization or Contrast Limited Adaptive Histogram Equalization. See: https://docs.opencv.org/4.x/d5/daf/tutorial_py_histogram_equalization.html
    args:
        image:  Numpy array of BGR format
        clahe: whether to use CLAHE or simple Histogram Equalization
        **kwargs: Dictonary containing arguments of either cv2.equalizeHist() or cv.createCLAHE depending if CLAHE argument is True of false
    '''  
    assert len(image.shape) == 2, "Grayscale Images are used for these operations"
    
    if CLAHE:
        clahe = cv2.createCLAHE(**kwargs)
        return clahe.apply(image)
    else: return cv2.equalizeHist(image, **kwargs)
