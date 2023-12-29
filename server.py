import socket
import threading
import tkinter as tk
import customtkinter
import rsa

FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
KEY_SWAP_MESSAGE = "!SWAP"
MESSAGE_SIZE = 2048
KEY_SIZE = 1024

# Server Setup
server = None
clients = set()
clients_lock = threading.Lock()
usernames = {}
partner_keys = {}

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# Generate or load RSA keys
#public_key, private_key = rsa.newkeys(1024)

# GUI
app = customtkinter.CTk()
app.geometry("400x300")
app.title("Potato Server")

# Host Frame
host_frame = customtkinter.CTkFrame(app)
host_frame.pack(fill=tk.BOTH, expand=True)

# Server IP Input
ip_label = customtkinter.CTkLabel(host_frame, text="Server IP:")
ip_label.pack(pady=(10, 0))
ip_input = customtkinter.CTkEntry(host_frame)
ip_input.insert(0, "localhost")  # Default value
ip_input.pack()

# Server Port Input
port_label = customtkinter.CTkLabel(host_frame, text="Server Port:")
port_label.pack(pady=(10, 0))
port_input = customtkinter.CTkEntry(host_frame)
port_input.insert(0, "5050")  # Default value
port_input.pack()

# Client List Frame (Initially Hidden)
client_frame = customtkinter.CTkFrame(app)
client_list_label = customtkinter.CTkLabel(client_frame, text="Connected Clients:")
client_list_label.pack()
client_list_box = tk.Listbox(client_frame, bg="#000000", fg="#FFFFFF")
client_list_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

#Decrypt message
def decrypt(message, private_key):
    return rsa.decrypt(message, private_key).decode(FORMAT)

#Encrypt message
def encrypt_message(message, partner_key):
    return rsa.encrypt(message.encode(FORMAT), partner_key)

#Send encrypted messages
def send_e_message(client, message):
    partner_key = partner_keys.get(client.getpeername())
    if partner_key:
        encrypted_msg = encrypt_message(message, partner_key)
        client.send(encrypted_msg)

# Start Server Function
def start_server():
    global server
    SERVER = ip_input.get()
    PORT = int(port_input.get())
    ADDR = (SERVER, PORT)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()

    threading.Thread(target=run_server, daemon=True).start()
    switch_to_client_list()

def run_server():
    print("[SERVER STARTED]")
    while True:
        try:
            conn, addr = server.accept()
            with clients_lock:
                clients.add(conn)
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
        except:
            break

def handle_client(conn, addr):
    public_key, private_key = rsa.newkeys(KEY_SIZE)
    conn.send(public_key.save_pkcs1("PEM"))
    partner_key = rsa.PublicKey.load_pkcs1(conn.recv(MESSAGE_SIZE))
    partner_keys[addr] = partner_key

    username = decrypt(conn.recv(MESSAGE_SIZE), private_key) # Receive the username first
    usernames[addr] = username

    print(f"[NEW CONNECTION] {username} connected from {addr}")
    client_list_box.insert(tk.END, f"{username} ({addr[0]}:{addr[1]})")
    with clients_lock:
        for c in clients:
            send_e_message(c, f"[Server] {username} Connected!")
    try:
        connected = True
        while connected:
            msg = decrypt(conn.recv(MESSAGE_SIZE), private_key)
            if not msg or msg == DISCONNECT_MESSAGE:
                connected = False
                break
            if msg != KEY_SWAP_MESSAGE:
                with clients_lock:
                    for c in clients:
                        send_e_message(c, f"[{username}] {msg}")
            
            public_key, private_key = rsa.newkeys(KEY_SIZE)
            send_e_message(conn, KEY_SWAP_MESSAGE)
            conn.send(public_key.save_pkcs1("PEM"))
            partner_key = rsa.PublicKey.load_pkcs1(conn.recv(MESSAGE_SIZE))
            partner_keys[addr] = partner_key

    finally:
        with clients_lock:
            clients.remove(conn)
            client_list_box.delete(client_list_box.get(0, tk.END).index(f"{username} ({addr[0]}:{addr[1]})"))
            for c in clients:
                send_e_message(c, f"[Server] {username} Disconnected!")
            partner_keys.pop(addr, None)
        conn.close()

# Host Button
host_button = customtkinter.CTkButton(host_frame, text="Host Server", command=start_server)
host_button.pack(pady=10)

# Stop Server Function
def stop_server():
    global server
    with clients_lock:
        for client in clients:
            send_e_message(client, DISCONNECT_MESSAGE)
            client.close()
        clients.clear()
    server.close()
    server = None
    switch_to_host()

# Stop Hosting Button
stop_button = customtkinter.CTkButton(client_frame, text="Stop Hosting", command=stop_server)
stop_button.pack(pady=10)

# Switch to Client List
def switch_to_client_list():
    host_frame.pack_forget()
    client_frame.pack(fill=tk.BOTH, expand=True)

# Switch to Host
def switch_to_host():
    client_list_box.delete(0, tk.END)
    client_frame.pack_forget()
    host_frame.pack(fill=tk.BOTH, expand=True)

# Start the GUI
app.mainloop()
