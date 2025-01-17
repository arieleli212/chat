# imports:
# socket- for handling connections 
# threading- for handling multiple clients librarys

import socket
import threading 

# chooses the host and port for the server to run on
HOST = '127.0.0.1'  
PORT = 5000

#dictionary for users  in the structure of {username: (conn, address)}
clients = {}

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
        else:
            conn.close()
            return
        
        while True:
            data = conn.recv(1024)
            if not data:
                break  # client disconnected

            message = data.decode().strip()
            if message.startswith("/msg"):
                # split- splits a string into a list ('parts') where each word is a list item
                # expecting the format: "/msg <recipient_username> <message>"
                # splits the actual message from the "/msg <recipient_username>" by the 2 spaces after each one
                parts = message.split(" ", 2) 
                if len(parts) < 3: #len= length
                    continue
                _, recipient, msg_body = parts
                if recipient in clients:
                    r_conn, r_addr = clients[recipient] #finds the recipent in the clients list and defines it's conn and addr parameters
                    try:
                        #sends coded (into bits) message to the recipient containing the data mentioned below
                        r_conn.sendall(f"[{username} -> {recipient}]: {msg_body}".encode()) 
                    except Exception as e:
                        print(f"[!] Error sending message to {recipient}: {e}")
                else:
                    # If recipient no longer online- the other user recives an error
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
# AF_INET- address family, SOCK_STREAM- the sockets uses a TCP connection
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # sets socket parameters for the local network. 
    try:
        server_socket.bind((HOST, PORT)) #binds the socket to the host and the prot 
        server_socket.listen(5) #socket listens for connections
        print(f"[Server] Listening on {HOST}:{PORT}")

        while True:
            conn, addr = server_socket.accept() #approves every new connection and saves the conn and addr parameters
            # opens a new process (tied to the server) that runs the 'handle_client' function wuth the 'conn'& 'addr' arguments
            client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            client_thread.start()
    except Exception as e:
        print(f"[!] Server error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server() #calls the start_server function
