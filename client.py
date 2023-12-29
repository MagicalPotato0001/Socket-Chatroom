import socket
import threading
import tkinter as tk
import customtkinter
import time
import rsa

FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
KEY_SWAP_MESSAGE = "!SWAP"
MESSAGE_SIZE = 2048
KEY_SIZE = 512

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

public_key, private_key = rsa.newkeys(KEY_SIZE)
public_partner = None

# GUI
app = customtkinter.CTk()
app.geometry("500x500")
app.title("Chat Client")

# Connection Frame
connection_frame = customtkinter.CTkFrame(app)
connection_frame.pack(fill=tk.BOTH, expand=True)

# IP Address Input
ip_label = customtkinter.CTkLabel(connection_frame, text="IP Address:")
ip_label.pack(pady=(10, 0))
ip_input = customtkinter.CTkEntry(connection_frame, placeholder_text="127.0.0.1")
ip_input.insert(0, "127.0.0.1")
ip_input.pack()

# Port Input
port_label = customtkinter.CTkLabel(connection_frame, text="Port:")
port_label.pack(pady=(10, 0))
port_input = customtkinter.CTkEntry(connection_frame, placeholder_text="5050")
port_input.insert(0, "5050")
port_input.pack()

# Username Input
username_label = customtkinter.CTkLabel(connection_frame, text="Username:")
username_label.pack(pady=(10, 0))
username_input = customtkinter.CTkEntry(connection_frame)
username_input.pack()

# Function to send an encrypted message
def send_encrypted(client, msg):
    client.send(rsa.encrypt(msg.encode(FORMAT), public_partner))

def decrypt(message):
    return rsa.decrypt(message, private_key).decode(FORMAT)

# Connect Button
def connect():
    global client
    global public_partner
    SERVER = ip_input.get()
    PORT = int(port_input.get())
    ADDR = (SERVER, PORT)


    # Connect using the SSL context
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(ADDR)
        public_partner = rsa.PublicKey.load_pkcs1(client.recv(MESSAGE_SIZE))
        client.send(public_key.save_pkcs1("PEM"))
        send_encrypted(client, username_input.get())
        threading.Thread(target=receive, daemon=True).start()
        switch_to_chat()
    except Exception as e:
        print(f"Failed to connect: {e}")

connect_button = customtkinter.CTkButton(connection_frame, text="Connect", command=connect)
connect_button.pack(pady=10)

# Send Button
def send_message(event=None):
    message = message_input.get()
    if message:
        send_encrypted(client, message)
        message_input.delete(0, tk.END)

# Disconnect Button
def disconnect():
    send_encrypted(client, DISCONNECT_MESSAGE)
    time.sleep(0.5)
    client.close()
    switch_to_connect()

# Switch to Chat Frame
def switch_to_chat():
    connection_frame.pack_forget()
    chat_frame.pack(fill=tk.BOTH, expand=True)

# Switch to Connection Frame
def switch_to_connect():
    chat_frame.pack_forget()
    connection_frame.pack(fill=tk.BOTH, expand=True)

#Encrypt message
def encrypt_message(message, partner_key):
    return rsa.encrypt(message.encode(FORMAT), partner_key)

# Receive Function
def receive():
    global public_partner
    global public_key, private_key
    while True:
        try:
            msg = decrypt(client.recv(MESSAGE_SIZE))
            if msg and msg != KEY_SWAP_MESSAGE:
                chat_text.insert(tk.END, msg + "\n")
            if msg == DISCONNECT_MESSAGE:
                switch_to_connect()
                break
            if msg == KEY_SWAP_MESSAGE:
                public_key, private_key = rsa.newkeys(KEY_SIZE)
                public_partner = rsa.PublicKey.load_pkcs1(client.recv(MESSAGE_SIZE))
                client.send(public_key.save_pkcs1("PEM"))

        except:
            client.close()
            switch_to_connect()
            break

# Chat Frame (Initially Hidden)
chat_frame = customtkinter.CTkFrame(app)

# Chat Display
chat_label = customtkinter.CTkLabel(chat_frame, text="Chat:")
chat_label.pack()
chat_text = tk.Text(chat_frame, height=20, width=60, bg="#000000", fg="#FFFFFF")
chat_text.pack()

# Frame for input and send button
input_frame = customtkinter.CTkFrame(chat_frame)
input_frame.pack(fill=tk.X, padx=10, pady=10)

# Message Input
message_input = customtkinter.CTkEntry(input_frame, width=400)
message_input.pack(side=tk.LEFT, padx=(0, 10))

send_button = customtkinter.CTkButton(input_frame, text="Send", command=send_message)
send_button.pack(side=tk.RIGHT)


disconnect_button = customtkinter.CTkButton(chat_frame, text="Disconnect", command=disconnect)
disconnect_button.pack(fill=tk.X, padx=10, pady=10)

# Bind Enter key to send message function
app.bind('<Return>', send_message)

# Start the GUI
app.mainloop()
