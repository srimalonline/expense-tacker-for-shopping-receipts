import cv2
import pytesseract
import re
import os
import sys
from datetime import datetime

# Ensure the path to Tesseract is correctly set
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'  # Update to your Tesseract-OCR path


def preprocess_image(image_path):
    """
    Preprocess the image to enhance OCR accuracy.
    """
    # Load image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Perform OTSU thresholding to binarize the image
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Define a kernel for dilation
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    # Dilate the image to connect text regions
    dilated = cv2.dilate(thresh, kernel, iterations=1)

    return image, dilated


def extract_text_from_image(image, dilated):
    """
    Extract text from the image using contours to identify text regions.
    """
    # Find contours on the dilated image
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # List to hold extracted text
    extracted_text = []

    # Iterate through contours and apply OCR on each detected text region
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Crop the text block from the original image
        cropped = image[y:y + h, x:x + w]

        # Apply OCR on the cropped image
        text = pytesseract.image_to_string(cropped, config='--psm 6')

        # Clean the extracted text
        clean_text = clean_extracted_text(text)

        # Append clean text to the list if it's not empty
        if clean_text:
            extracted_text.append(clean_text)

    return extracted_text


def clean_extracted_text(text):
    """
    Clean and filter the extracted text.
    """
    # Remove any unwanted characters or empty lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Join lines into a single string with proper formatting
    clean_text = '\n'.join(lines)

    return clean_text


def save_text_output(extracted_text, image_path):
    """
    Save the formatted text to a .txt file.
    """
    # Create 'output' folder if it doesn't exist
    if not os.path.exists('output'):
        os.makedirs('output')

    # Generate a text filename based on the image file's name and current timestamp
    filename = os.path.splitext(os.path.basename(image_path))[0]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    txt_filename = f'output/{filename}_{timestamp}.txt'

    # Write the extracted text to the text file
    with open(txt_filename, mode='w') as file:
        for text_block in extracted_text:
            file.write(text_block + "\n\n")  # Separate text blocks for clarity

    print(f"Formatted text saved to {txt_filename}")


def main(image_path):
    """
    Main function to process the receipt image and generate a summary.
    """
    # Preprocess the image
    image, dilated = preprocess_image(image_path)

    # Extract text from the processed image using contours
    extracted_text = extract_text_from_image(image, dilated)

    # Print the extracted text for debugging
    print("Extracted OCR Text Blocks:\n", extracted_text)

    # Save the summary to a formatted text file in the output folder
    save_text_output(extracted_text, image_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python shoper.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    main(image_path)
