import zmq

"""
Light-weight template for demonstrating how to trigger the OCR.
"""

# Opens ZeroMQ context on port 5555 and sends a request.
context = zmq.Context()
print("Client attempting to connect to server...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
print(f"Sending a request...")



while True:
    
    command = input("Enter a command: ")

    # Sends messages to port 5555 to be received by server-side
    socket.send_string(command)

    # Receives response from server-side on port 5555
    message = socket.recv()

    print(f"Server sent back: \n{message.decode()}")
  
    if message.decode() == "Q":
        break
