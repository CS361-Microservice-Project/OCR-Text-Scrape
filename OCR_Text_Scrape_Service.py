import zmq
import pytesseract
import cv2


context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")



def deskew_image(image):
    # Converts to grayscale, estimates image rotation from foreground pixels, and rotates image upright
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    inv = 255 - bw
    coords = cv2.findNonZero(inv)
    if coords is None:
        return gray

    rect = cv2.minAreaRect(coords)
    angle = rect[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = gray.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(gray, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def get_image(filename):
    filepath = fr"{filename}"

    image = cv2.imread(filepath)
    if image is None:
        return f'ERROR: Could not read image: {filepath}'

    return image


def create_pdf(image):
    # Get a searchable PDF
    pdf = pytesseract.image_to_pdf_or_hocr(deskewed_image, extension='pdf')
    with open('test.pdf', 'w+b') as f:
        f.write(pdf) # pdf type is bytes by default
    
    return None


def ocr_scrape(image):
    print("Starting OCR")

    # Deskews image before OCR to improve text extraction on rotated scans/photos
    deskewed_image = deskew_image(image)

    # Timeout/terminate the tesseract job after a period of time
    try:
        text = pytesseract.image_to_string(deskewed_image, timeout=2)
        print("\nOCR extraction successful!\n")
        print(f"OCR INTERPRETATION:\n{text}") # Timeout after 2 seconds
        return text

    except RuntimeError as timeout_error:
        # Tesseract processing is terminated
        print("timed out")
        print(timeout_error)
        return f'ERROR: {timeout_error}'



while True:
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













































