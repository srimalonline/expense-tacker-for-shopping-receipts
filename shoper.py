import cv2
import pytesseract
import re
import sys
import os
import csv
from datetime import datetime

# Adding tesseract executable in the PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


def preprocess_image(image_path):
    # Load image
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply a slight blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # Apply adaptive thresholding for better OCR accuracy
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    return binary


def extract_text(image):
    # Use Tesseract to do OCR on the processed image
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, config=custom_config)
    return text


def parse_receipt_text(text):
    lines = text.split('\n')
    summary = {
        'Items': [],
        'Subtotal': None,
        'Cash': None,
        'Change': None
    }

    item_pattern = re.compile(r'([A-Za-z\s]+)\s+(\d+)\s+(\d+\.\d+)')

    for line in lines:
        line = line.strip()

        match = item_pattern.match(line)
        if match:
            name = match.group(1).strip()
            qty = match.group(2).strip()
            total = match.group(3).strip()
            summary['Items'].append(f"{name},{qty},{total}")  # CSV-friendly format

        elif 'Sub Total' in line or 'Subtotal' in line:
            subtotal = re.findall(r'\d+\.\d+', line)
            if subtotal:
                summary['Subtotal'] = subtotal[0]

        elif 'Cash' in line:
            cash = re.findall(r'\d+\.\d+', line)
            if cash:
                summary['Cash'] = cash[0]

        elif 'Change' in line:
            change = re.findall(r'\d+\.\d+', line)
            if change:
                summary['Change'] = change[0]

    return summary


def save_to_csv(summary, image_path):
    # Create 'logs' folder if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Generate a CSV filename based on the image file's name and current timestamp
    filename = os.path.splitext(os.path.basename(image_path))[0]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f'logs/{filename}_{timestamp}.csv'

    # Write data to the CSV file
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Item', 'Quantity', 'Total'])

        for item in summary['Items']:
            writer.writerow(item.split(','))

        writer.writerow(['Subtotal', summary['Subtotal']])
        writer.writerow(['Cash', summary['Cash']])
        writer.writerow(['Change', summary['Change']])

    print(f"Receipt details saved to {csv_filename}")


def main(image_path):
    # Preprocess the image
    processed_image = preprocess_image(image_path)

    # Extract text from the processed image
    text = extract_text(processed_image)

    # Optional: Print the raw text for debugging
    print("Raw OCR Text:\n", text)

    # Parse the extracted text
    summary = parse_receipt_text(text)

    # Save the summary to a CSV file in the logs folder
    save_to_csv(summary, image_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python shoper.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    main(image_path)
