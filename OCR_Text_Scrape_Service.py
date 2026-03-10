import zmq
import pytesseract
import cv2

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")


def deskew_image(image):
    """
    Purpose: Takes image, modifies resolution and other characteristics for higher OCR accuracy.
    Params: image - an image with text on it for the OCR to scrape from.
    Returns: gray - the same image tweaked for better text scraping
    """
    # Converts to grayscale, estimates image rotation from foreground pixels, and rotates image upright
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    inv = 255 - bw
    coords = cv2.findNonZero(inv)
    if coords is None:
        return gray

    return gray


def get_image(filename):
    """
    Purpose: Takes in filename, searches for image of said filename in Resource directory and validates it.
    Params: filename - a string, the name of the image to be scraped.
    Returns: image - an image object.
    """
    filepath = fr"{filename}"

    image = cv2.imread(filepath)
    if image is None:
        return f'ERROR: Could not read image: {filepath}'

    return image


def create_pdf(image):
    """
    Purpose: Takes image, and creates a PDF from it.
    Params: image - an image with text on it to be turned into PDF.
    Returns: None
    """
    # Get a searchable PDF
    pdf = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
    with open('test.pdf', 'w+b') as f:
        f.write(pdf)  # pdf type is bytes by default

    return None


def ocr_scrape(filename):
    """
    Purpose: Main function. Takes an image and scrapes text from it.
    Params: image - an image object to scrape text from.
    Returns: text - a string containing the text from the scraped image.
    """
    print("Starting OCR")

    image = get_image(filename)
    # Get a searchable PDF
    create_pdf(image)
    # Deskews image before OCR to improve text extraction on rotated scans/photos
    deskewed_image = deskew_image(image)

    # Timeout/terminate the tesseract job after a period of time
    try:
        text = pytesseract.image_to_string(deskewed_image, timeout=2)
        print("\nOCR extraction successful!\n")
        print(f"OCR INTERPRETATION:\n{text}")  # Timeout after 2 seconds
        return text

    except RuntimeError as timeout_error:
        # Tesseract processing is terminated
        print("timed out")
        print(timeout_error)
        return f'ERROR: {timeout_error}'



def main():
    while True:
        print('Running OCR')
        message = socket.recv()
        print(f"Received message: {message.decode()}")

        if len(message) > 0:
            if message.decode() == "Q":
                socket.send_string("Q")
                break

            elif message.decode() == "scrape":
                print("Scrape request received, scraping...")
                # Begin scraping
                text = ocr_scrape(f"Resource/img.png")

                print(f"Scrape successful, sending back text")
                socket.send_string(text)

            else:

                socket.send_string(f"Command '{message.decode()}' not recognized")

if __name__ == "__main__":
    main()