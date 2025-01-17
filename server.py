# imports:
# socket- for handling connections 
# threading- for handling multiple clients librarys
# json- for handling json files
# signal- for handling signals
# sys- for handling system functions

import socket
import threading
import json
import signal
import sys

# chooses the host and port for the server to run on
HOST = '127.0.0.1'  
PORT = 5000

# dictionary for users  in the structure of {username: (conn, address)}
clients = {}
# control the server socket from outside the start_server function
server_socket = None
# event to signal the server to shutdown
shutdown_event = threading.Event()

# file to store user messages and recieve them from
MESSAGES_FILE = "messages.json"

# reads the messages from the JSON file
def read_messages():
    try:
        # opens the file in read mode
        with open(MESSAGES_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# writes the messages to the JSON file
def write_messages(messages):
    # opens the file in write mode
    with open(MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=4)

# notifies all connected clients with a message aka: Server Broadcast
def notify_clients(message):
    for username, (conn, addr) in clients.items():
        try:
            conn.sendall(f"[Server]: {message}".encode())
        except Exception as e:
            print(f"[!] Error notifying {username}: {e}")

# broadcasts the user list to the clients
def broadcast_user_list():

    user_list = list(clients.keys()) # creates list from the 'clients' dictionary 

    # tries to send the user list to the clients per client. if fails- prints an error message 
    # sendall- sends all the info to said client
    for username, (conn, addr) in clients.items():
        try:
            conn.sendall(f"/userlist {user_list}".encode()) #encode= translates strings into bits
        except Exception as e:
            print(f"[!] Error sending user list to {username}: {e}")

# handles the client connection
def handle_client(conn, addr):
    username = None
    try:
        # waits for the client to send the username 
        # recv- recives tthe date in 1024 chuncks
        # decode- translates the bits to letters
        # strip- removes spaces in the beginning and at the end of the string
        initial_data = conn.recv(1024).decode().strip() 
        
        if initial_data.startswith("/register"):
            # splits the data given by the client, expecting the format: "/register <username>"
            _, username = initial_data.split()
            # Stores the connection in the clients dictionary
            clients[username] = (conn, addr)
            print(f"[+] {username} connected from {addr}")
            broadcast_user_list()

            # read from history and send previous messages to the user
            messages = read_messages().get(username, [])
            for msg in messages:
                conn.sendall(f"[History]: {msg}\n".encode())
        else:
            conn.close()
            return

        # waits for the client to send data while there is no SIGINT signal or server shutdown
        while not shutdown_event.is_set():
            data = conn.recv(1024)
            if not data:
                break  # client disconnected

            message = data.decode().strip()
            if message.startswith("/msg"):
                # split- splits a string into a list ('parts') where each word is a list item
                # expecting the format: "/msg <recipient_username> <message>"
                # splits the actual message from the "/msg <recipient_username>" by the 2 spaces after each one
                parts = message.split(" ", 2) 
                if len(parts) < 3: # len= length
                    continue
                _, recipient, msg_body = parts
                if recipient in clients:
                    r_conn, r_addr = clients[recipient] # finds the recipent in the clients list and defines it's conn and addr parameters
                    try:
                        # sends coded (into bits) message to the recipient containing the data mentioned below
                        r_conn.sendall(f"[{username} -> {recipient}]: {msg_body}".encode())

                        # write the message to the history with check if the recipient is in the messages list
                        messages = read_messages()
                        if recipient not in messages:
                            messages[recipient] = []
                        messages[recipient].append(f"[{username}]: {msg_body}")
                        write_messages(messages)
                    except Exception as e:
                        print(f"[!] Error sending message to {recipient}: {e}")
                else:
                    # username is not found in the clients list so not online and can't recieve the message
                    conn.sendall(f"[Server]: User '{recipient}' not found.".encode())
            else:
                # Unrecognized command or message
                conn.sendall("[Server]: Unrecognized command.".encode())
    
    # when fails to get any initial data
    except Exception as e:
        print(f"[!] Exception in handle_client for {username}: {e}")
    finally:
        # Cleanup on disconnect or error
        # deletes users connected and on the client list from the client list
        if username and username in clients:
            del clients[username]
            print(f"[-] {username} disconnected.")
            broadcast_user_list()
        conn.close()

def start_server():
    global server_socket
    # AF_INET- address family, SOCK_STREAM- the sockets uses a TCP connection
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # sets socket parameters for the local network. 
    try:
        server_socket.bind((HOST, PORT)) #binds the socket to the host and the prot 
        server_socket.listen(5) #socket listens for connections
        print(f"[Server] Listening on {HOST}:{PORT}")

        while not shutdown_event.is_set():
            try:
                # check if the server is alive
                server_socket.settimeout(1)
                conn, addr = server_socket.accept() # approves every new connection and saves the conn and addr parameters
                # opens a new process (tied to the server) that runs the 'handle_client' function wuth the 'conn'& 'addr' arguments
                client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                client_thread.start()
            except socket.timeout:
                continue
    except Exception as e:
        notify_clients("The server is shutting down due to an error.")
        print(f"[!] Server error: {e}")
    finally:
        notify_clients("The server is shutting down due to an error.")
        server_socket.close()
        print("[Server] Shutdown complete.")

def signal_handler(sig, frame):
    print("\n[Server] Shutting down...")
    notify_clients("The server is shutting down. Please reconnect later.")
    shutdown_event.set()
    if server_socket:
        server_socket.close()
    # close the server in a controlled way
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    start_server() #calls the start_server function
