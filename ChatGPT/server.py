import socket
import threading

HOST = '127.0.0.1'  # or '0.0.0.0' for all interfaces
PORT = 5000

# Global dictionary to store clients: {username: (conn, address)}
clients = {}

def broadcast_user_list():
    """
    Sends the current user list to all connected clients
    so they know who is online.
    """
    user_list = list(clients.keys())
    for username, (conn, addr) in clients.items():
        try:
            conn.sendall(f"/userlist {user_list}".encode())
        except Exception as e:
            print(f"[!] Error sending user list to {username}: {e}")

def handle_client(conn, addr):
    username = None
    try:
        # First message from client should be the chosen username
        initial_data = conn.recv(1024).decode().strip()
        if initial_data.startswith("/register"):
            # expected format: "/register <username>"
            _, username = initial_data.split()
            # Store the connection
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
                # format: "/msg <recipient_username> <message>"
                parts = message.split(" ", 2)
                if len(parts) < 3:
                    continue
                _, recipient, msg_body = parts
                if recipient in clients:
                    r_conn, r_addr = clients[recipient]
                    try:
                        r_conn.sendall(f"[{username} -> {recipient}]: {msg_body}".encode())
                    except Exception as e:
                        print(f"[!] Error sending message to {recipient}: {e}")
                else:
                    # If recipient no longer online
                    conn.sendall(f"[Server]: User '{recipient}' not found.".encode())
            else:
                # Unrecognized command or message
                conn.sendall("[Server]: Unrecognized command.".encode())

    except Exception as e:
        print(f"[!] Exception in handle_client for {username}: {e}")
    finally:
        # Cleanup on disconnect or error
        if username and username in clients:
            del clients[username]
            print(f"[-] {username} disconnected.")
            broadcast_user_list()
        conn.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"[Server] Listening on {HOST}:{PORT}")

        while True:
            conn, addr = server_socket.accept()
            # Each new client is handled by a separate thread
            client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            client_thread.start()
    except Exception as e:
        print(f"[!] Server error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
