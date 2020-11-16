import socket
import errno # for handling errors
import sys 

HEADER_LENGTH = 10 # gobal variables are same as before 

IP = "127.0.0.1"
PORT = 9999
ADDR = (IP,PORT)
FORMAT = 'utf-8'
my_username = input("Username: ")

print("You are in!!(type 'exit' to get out of the chat server)")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(ADDR) # connecting client socket to the server

client_socket.setblocking(False) # to prevent blocking, but rether return an exception

# Prepare username and header and send them
# We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
username = my_username.encode(FORMAT)
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)

while True:
    
    message = input(f'{my_username} > ') # taking input message

    if message: # if it is a non-empty valid message
        # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
        message = message.encode(FORMAT)
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)

    try:

        while True:

            username_header = client_socket.recv(HEADER_LENGTH)

            if not len(username_header): # we did not recieve any data. this happens when server has close or shutdown
                print('Connection closed by the server') 
                sys.exit()

            username_length = int(username_header.decode(FORMAT).strip())
            username = client_socket.recv(username_length).decode(FORMAT)

            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode(FORMAT).strip())
            message = client_socket.recv(message_length).decode(FORMAT)

            print(f'{username} > {message}')

    except IOError as e:
        # This is normal on non blocking connections - when there are no incoming data, error is going to be raised
        # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
        # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
        # If we got different error code - something happened
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # We just did not receive anything
        continue

    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error: {} '.format(str(e)))
        sys.exit()