import socket
import threading
import json
import signal
import sys

HOST = '127.0.0.1'  # or '0.0.0.0' for all interfaces
PORT = 5000

# Global dictionary to store clients: {username: (conn, address)}
clients = {}
server_socket = None
shutdown_event = threading.Event()

# File to store user messages
MESSAGES_FILE = "messages.json"

def read_messages():
    """Reads messages from the JSON file."""
    try:
        with open(MESSAGES_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def write_messages(messages):
    """Writes messages to the JSON file."""
    with open(MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=4)

def notify_clients(message):
    """Sends a message to all connected clients."""
    for username, (conn, addr) in clients.items():
        try:
            conn.sendall(f"[Server]: {message}".encode())
        except Exception as e:
            print(f"[!] Error notifying {username}: {e}")

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

            # Send previous messages to the user
            messages = read_messages().get(username, [])
            for msg in messages:
                conn.sendall(f"[History]: {msg}\n".encode())
        else:
            conn.close()
            return
        
        while not shutdown_event.is_set():
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

                        # Save message to history
                        messages = read_messages()
                        if recipient not in messages:
                            messages[recipient] = []
                        messages[recipient].append(f"[{username}]: {msg_body}")
                        write_messages(messages)
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
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"[Server] Listening on {HOST}:{PORT}")

        while not shutdown_event.is_set():
            try:
                server_socket.settimeout(1)  # Check periodically for shutdown
                conn, addr = server_socket.accept()
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
    shutdown_event.set()
    if server_socket:
        server_socket.close()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    start_server()
