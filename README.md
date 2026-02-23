# OCR-Text-Scrape

## Description
Scrapes text from an image and sends text to main program.

## Requesting Data
To request data, a ZeroMQ context server must be opened on a selected port on the client-side. 
The server-side will then listen on the selected port expecting a certain message to begin it's OCR processing, in this case the message "scrape".

```
# Opens ZeroMQ context on port 5555 and sends a request.

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

socket.send_string("scrape")


```




## Receiving Data
The data is received on the client-side from the server in the form of text. In this case the OCR microservice (server) will return the text scraped
from an image. At this point the received data is a regular string and can be manipulated by the main program (client) freely.

```
# Receives response from server-side on port 5555
message = socket.recv()
```

