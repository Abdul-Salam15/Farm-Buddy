"""
Image processing utilities for plant disease detection
"""
from PIL import Image
import io
import os


def validate_image(file):
    """
    Validate uploaded image file
    Returns: (is_valid, error_message)
    """
    # Check file size (5MB limit)
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        return False, f"Image too large. Maximum size is 5MB, your file is {file.size / (1024*1024):.1f}MB"
    
    # Check file format
    allowed_formats = ['JPEG', 'JPG', 'PNG', 'WEBP']
    try:
        img = Image.open(file)
        if img.format.upper() not in allowed_formats:
            return False, f"Invalid format. Allowed formats: {', '.join(allowed_formats)}"
        # Do not close img here as it might close the underlying file
        file.seek(0)  # Reset file pointer
        return True, None
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"


def compress_image(image_file, max_size=(1024, 1024), quality=85):
    """
    Compress image for storage and transmission
    Returns: compressed image bytes
    """
    try:
        # Open image
        img = Image.open(image_file)
        
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img
        
        # Resize if larger than max_size
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Compress to bytes
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        return output
    except Exception as e:
        raise Exception(f"Error compressing image: {str(e)}")


def prepare_image_for_gemini(image_path):
    """
    Prepare image for Gemini Vision API
    Returns: PIL Image object
    """
    try:
        img = Image.open(image_path)
        return img
    except Exception as e:
        raise Exception(f"Error loading image: {str(e)}")
