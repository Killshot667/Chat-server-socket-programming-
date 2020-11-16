import socket
import select # for handling multiple sockets at OS level

HEADER_LENGTH = 10 # header of 10 bytes
IP = '127.0.0.1'  # localhost
PORT = 9999
FORMAT = 'utf-8' # common format for encoding and decoding
ADDR = (IP,PORT) # server socket address
DISCONNECT = "exit "

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # first parameter - address family( eg IPv4 or IPv6 etc). second parameter - type of network protocol
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # can use same IP and port for different sockets

server_socket.bind(ADDR)

sockets_list = [server_socket] # list of all sockets

clients = {} # ditionary of all clients active

# Handles message receiving
def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH) # contains the length of the incoming message
        if not len(message_header): # when client closes properly
            return False
        message_length = int(message_header.decode(FORMAT).strip())
        data = client_socket.recv(message_length) # recieve the actual encoded message
        if data.decode(FORMAT) == DISCONNECT:
            return False
        return {'header': message_header, 'data': data}


    except:   # Something went wrong like empty message or client exited abruptly.
        return False

def start():
    server_socket.listen()
    print("[LISTENING] server listening at {}:{}".format(ADDR[0],ADDR[1]))

    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list) # get the subset of read, write and error sockets which are ready
        for notified_socket in read_sockets:
            
            if notified_socket == server_socket: # in case of new connection
                client_socket, client_address = server_socket.accept() # new client socket
                user = receive_message(client_socket) # the first message the client sends is their username
                if user is False:
                    continue
                username = user['data'].decode(FORMAT)
                sockets_list.append(client_socket) # saving the client socket to list of sockets
                clients[client_socket] = user # saving the client
                print(f'Accepted new connection from {client_address[0]}:{client_address[1]}, username: {username}')

            else: # the notified_socket has sent a new chat message
                message = receive_message(notified_socket)
                user = clients[notified_socket]
                username = clients[notified_socket]['data'].decode(FORMAT)
                if message is False: # client has left the chat
                    print(f'Closed connection from: {username}')
                    sockets_list.remove(notified_socket) # removing socket from the list
                    del clients[notified_socket] # removing socket from clients
                    notified_socket.close()
                    continue

                print(f'Received message from {username}: {message["data"].decode(FORMAT)}')

                # Iterate over connected clients and broadcast message
                for client_socket in clients:

                    # But don't sent it to sender
                    if client_socket != notified_socket:

                        # Send user and message (both with their headers)
                        # We are reusing here message header sent by sender, and saved username header send by user when he connected
                        client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

        # if some socket has exception, remove them
        for notified_socket in exception_sockets:

            # Remove from list for socket.socket()
            sockets_list.remove(notified_socket)

            # Remove from our list of users
            del clients[notified_socket]
            
            print(f'Closed connection from: {username}')
            notified_socket.close()



print("[STARTING] chat server is starting...")
start()

