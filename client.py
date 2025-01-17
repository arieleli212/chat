

import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter.scrolledtext import ScrolledText

HOST = '127.0.0.1'
PORT = 5000

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Python Chat Client")
        self.master.geometry("600x400")  # Set a default window size

        self.socket = None
        self.username = None
        self.user_list = []

        # ---------------------
        # Top frame: connection info + user dropdown
        # ---------------------
        self.frame_top = tk.Frame(master)
        self.frame_top.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.label_user = tk.Label(self.frame_top, text="Connecting...")
        self.label_user.pack(side=tk.LEFT, padx=5)

        self.label_to = tk.Label(self.frame_top, text="Recipient:")
        self.label_to.pack(side=tk.LEFT, padx=5)

        # Initialize a StringVar with a placeholder
        self.selected_user = tk.StringVar(master)
        self.selected_user.set("Select a user")

        # Create OptionMenu with at least one placeholder item
        self.dropdown_recipients = tk.OptionMenu(
            self.frame_top,
            self.selected_user,
            "Select a user"
        )
        self.dropdown_recipients.pack(side=tk.LEFT, padx=5)

        self.refresh_button = tk.Button(self.frame_top, text="Refresh", command=self.refresh_user_list)
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        # ---------------------
        # Middle frame: chat display
        # ---------------------
        self.frame_middle = tk.Frame(master)
        self.frame_middle.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.text_area = ScrolledText(self.frame_middle, height=15, width=50, wrap=tk.WORD)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.DISABLED)

        # ---------------------
        # Bottom frame: message entry + send button
        # ---------------------
        self.frame_bottom = tk.Frame(master)
        self.frame_bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.label_message = tk.Label(self.frame_bottom, text="Enter Message:")
        self.label_message.pack(side=tk.LEFT, padx=5)

        self.entry_message = tk.Entry(self.frame_bottom, width=40)
        self.entry_message.pack(side=tk.LEFT, padx=5)
        # Bind "Enter" key to send message
        self.entry_message.bind("<Return>", self.send_message_event)

        self.send_button = tk.Button(self.frame_bottom, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=5)

        # Clean up on close
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Begin connection
        self.connect_to_server()

    def connect_to_server(self):
        """
        Prompt for a username and connect to the server.
        """
        self.username = simpledialog.askstring("Username", "Enter a username:", parent=self.master)
        if not self.username:
            messagebox.showerror("Error", "Username cannot be empty.")
            self.master.destroy()
            return

        self.label_user.config(text=f"Connected as: {self.username}")

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST, PORT))
            # Register with the server
            register_msg = f"/register {self.username}"
            self.socket.sendall(register_msg.encode())
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {e}")
            self.master.destroy()
            return

        # Start a background thread to listen for messages
        listen_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        listen_thread.start()

    def listen_for_messages(self):
        """
        Continuously listen for incoming messages from the server.
        """
        try:
            while True:
                data = self.socket.recv(4096)
                if not data:
                    break  # Server disconnected

                message = data.decode().strip()
                # Check for server shutdown message
                if "[Server]: The server is shutting down." in message:
                    messagebox.showinfo("Server Shutdown", "The server has been shut down. Please try reconnecting later.")
                    break
                # Check for special commands from server
                if message.startswith("/userlist"):
                    # e.g. "/userlist ['Alice', 'Bob', 'Charlie']"
                    try:
                        userlist_str = message.replace("/userlist ", "")
                        self.user_list = eval(userlist_str)  # For a real app, consider ast.literal_eval
                        self.refresh_user_list()
                    except Exception as e:
                        print(f"[!] Error parsing user list: {e}")
                else:
                    # Normal chat message
                    self.append_text(message)
        except Exception as e:
            print(f"[!] Error in listen_for_messages: {e}")
        finally:
            self.socket.close()
            self.master.quit()

    def refresh_user_list(self):
        """
        Updates the dropdown of recipients with the current user list.
        """
        menu = self.dropdown_recipients["menu"]
        menu.delete(0, "end")

        # Populate the dropdown menu
        for user in self.user_list:
            if user != self.username:  # Hide yourself as a recipient
                menu.add_command(
                    label=user,
                    command=lambda value=user: self.selected_user.set(value)
                )

        # Optionally set a default selection if there's at least one other user
        if self.user_list:
            possible_recipients = [u for u in self.user_list if u != self.username]
            if possible_recipients:
                self.selected_user.set(possible_recipients[0])
            else:
                self.selected_user.set("Select a user")
        else:
            self.selected_user.set("Select a user")

    def send_message_event(self, event):
        """
        This allows hitting 'Enter' in the message Entry to send the message.
        """
        self.send_message()

    def send_message(self):
        """
        Sends a message to the selected recipient.
        """
        recipient = self.selected_user.get()
        msg_body = self.entry_message.get().strip()
        if not recipient or recipient == "Select a user":
            messagebox.showwarning("Warning", "No recipient selected.")
            return
        if not msg_body:
            return

        msg = f"/msg {recipient} {msg_body}"
        try:
            self.socket.sendall(msg.encode())
            # Show the message in the local chat window
            self.append_text(f"[You -> {recipient}]: {msg_body}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not send message: {e}")

        # Clear the entry field
        self.entry_message.delete(0, tk.END)

    def append_text(self, msg):
        """
        Appends a message to the chat window (ScrolledText).
        """
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, msg + "\n")
        self.text_area.config(state=tk.DISABLED)
        # Automatically scroll to the end
        self.text_area.yview(tk.END)

    def on_closing(self):
        """
        Clean up when the user closes the window.
        """
        try:
            self.socket.close()
        except:
            pass
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
