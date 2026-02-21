import zmq
import pytesseract


context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")


def ocr_scrape(filename):
    print("Starting OCR")
    filepath = fr"{filename}"
    # Timeout/terminate the tesseract job after a period of time
    try:
        text = pytesseract.image_to_string(filepath, timeout=2)
        print("\nOCR extraction successful!\n")
        print(f"OCR INTERPRETATION:\n{text}") # Timeout after 2 seconds

    except RuntimeError as timeout_error:
        # Tesseract processing is terminated
        print("timed out")
        print(timeout_error)
        return f'ERROR: {timeout_error}'





    # Get a searchable PDF
    pdf = pytesseract.image_to_pdf_or_hocr(filepath, extension='pdf')
    with open('test.pdf', 'w+b') as f:
        f.write(pdf) # pdf type is bytes by default

    return text





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











































