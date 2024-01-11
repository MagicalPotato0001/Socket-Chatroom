import socket
import threading
import rsa
import tkinter as tk
import customtkinter
import json
from cryptography.fernet import Fernet

class Server:
    def __init__(self,
                 address = 'localhost',
                 tcp_port = 5050,
                 udp_port = 12345,
                 messaging = True,
                 voice = True,
                 key_size = 2048,
                 message_size = 4096,
                 disconnect_message = "!DISCONNECT",
                 voice_join_message = "!VOICEJOIN",
                 voice_leave_message = "!VOICELEAVE",
                 update_active_message = "!UPDATE_LIST",
                 audio_chunk = 1024,
                 audio_buffer = 2,
                 use_gui = True,
                 color_theme = "blue",
                 default_key = b"glZmhsq8UqjpJ0_WKMMc60p07zHxvU4lGRWBJFBnfkI="):
        
        self.tcp = (address, tcp_port)
        self.udp = (address, udp_port)

        self.passw = default_key
        self.cipher = Fernet(self.passw)

        self.gui = use_gui
        self.msg = messaging
        self.voice = voice

        self.key_size = key_size
        self.msg_size = message_size

        self.chunk = audio_chunk
        self.buffer = audio_buffer

        self.format = 'utf-8'
        self.d_msg = disconnect_message
        self.vj_msg = voice_join_message
        self.vl_msg = voice_leave_message
        self.update_msg = update_active_message

        self.usernames = {}
        self.v_usernames = {}
        self.partner_keys = {}

        self.clients = set()
        self.clients_lock = threading.Lock()

        self.v_clients = set()
        self.v_clients_lock = threading.Lock()

        self.m_server = None

        self.a_server = None

        self.m_running = True
        self.a_running = True

        self.error_log = []
        if self.gui:
            #App Settings
            customtkinter.set_appearance_mode("System")
            customtkinter.set_default_color_theme(color_theme)
            self.app = customtkinter.CTk()
            self.app.geometry("600x400")
            self.app.title("Server")
            self.frame = customtkinter.CTkFrame(self.app)
            self.frame.pack(fill=tk.BOTH, expand=True)

            #Ip
            self.ip_l = customtkinter.CTkLabel(self.frame, text="Server IP:")
            self.ip_l.pack(pady=(10,0))
            self.ip_in = customtkinter.CTkEntry(self.frame)
            self.ip_in.insert(0, "localhost")
            self.ip_in.pack()

            #Messaging Port
            self.m_port_l = customtkinter.CTkLabel(self.frame, text="Messaging Port(TCP):")
            self.m_port_l.pack(pady=(10,0))
            self.m_port_in = customtkinter.CTkEntry(self.frame)
            self.m_port_in.insert(0, "5050")
            self.m_port_in.pack()

            #Voice Port
            self.v_port_l = customtkinter.CTkLabel(self.frame, text="Voice Port(UDP):")
            self.v_port_l.pack(pady=(10,0))
            self.v_port_in = customtkinter.CTkEntry(self.frame)
            self.v_port_in.insert(0, "12345")
            self.v_port_in.pack()

            #Key
            self.key_l = customtkinter.CTkLabel(self.frame, text="Key")
            self.key_l.pack(pady=(10,0))
            self.key_in = customtkinter.CTkEntry(self.frame)
            self.key_in.insert(0, self.passw.decode("utf-8"))
            self.key_in.pack()

            #Client list
            self.c_frame = customtkinter.CTkFrame(self.app)
            self.c_list_l = customtkinter.CTkLabel(self.c_frame, text="Connected Clients:")
            self.c_list_l.pack()
            self.c_list_bo = tk.Listbox(self.c_frame, bg="#000000", fg="#FFFFFF")
            self.c_list_bo.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            #Generate New Key
            self.gen = customtkinter.CTkButton(self.frame, text="Generate Key", command = self.new_key)
            self.gen.pack(pady=10)

            #Host
            self.host_b = customtkinter.CTkButton(self.frame, text="Host Server", command=self.start_server)
            self.host_b.pack(pady=10)

            #Stop
            self.stop_b = customtkinter.CTkButton(self.c_frame, text="Stop Hosting", command=self.stop_server)
            self.stop_b.pack(pady=10)
            self.app.mainloop()

    def new_key(self):
        self.passw = Fernet.generate_key()
        self.key_in.delete(0, tk.END)
        self.key_in.insert(0, self.passw.decode("utf-8"))

    def voice_handler(self):
        try:
            while self.a_running:
                data, addr = self.a_server.recvfrom(self.chunk * self.buffer)
                if not data:
                    self.error_log.append(f"[No audio data from {addr}]")
                    print(self.error_log[-1])
                    break
                with self.v_clients_lock:
                    for v in self.v_clients:
                        tmp_addr = v.getpeername()[0]
                        if addr[0] != tmp_addr:
                            self.a_server.sendto(data, (tmp_addr, self.udp))
        except Exception as e:
            self.error_log.append(f"[Error handling voice client] {e}")
            print(self.error_log[-1])


    def encrypt(self, msg, partner):
        return rsa.encrypt(msg.encode(self.format), partner)
    
    def decrypt(self, msg, private):
        return rsa.decrypt(msg, private).decode(self.format)
    
    def update(self):
        # Create a dictionary with connected clients and voice clients
        update_users = {
            "Connected Clients": list(self.usernames.values()),
            "Voice Clients": list(self.v_usernames.values())
        }

        update_data = self.update_msg + '\n' + json.dumps(update_users, indent=4)

        # Send the update message to all connected clients
        with self.clients_lock:
            for c in self.clients:
                partner_key = self.partner_keys.get(c.getpeername())
                c.send(self.encrypt(update_data, partner_key))



    def messaging_handler(self, conn, addr):
        public_key, private_key = rsa.newkeys(self.key_size)
        conn.send(self.cipher.encrypt(public_key.save_pkcs1("PEM")))
        partner_key = rsa.PublicKey.load_pkcs1(conn.recv(self.msg_size))
        self.partner_keys[addr] = partner_key

        username = self.decrypt(conn.recv(self.msg_size), private_key)
        self.usernames[addr] = username
        self.c_list_bo.insert(tk.END, f"{username} ({addr[0]}:{addr[1]})")
        self.update()
        with self.clients_lock:
            for c in self.clients:
                c.send(self.encrypt(f"[Server] {username} Connected!", self.partner_keys.get(c.getpeername())))
        try:
            connected = True
            while connected:
                try:
                    msg = self.decrypt(conn.recv(self.msg_size), private_key)
                    if not msg:
                        break
                    if msg == self.d_msg:
                        connected = False
                        break
                    if msg == self.vj_msg:
                        self.v_usernames[addr] = username
                        with self.v_clients_lock:
                            self.v_clients.add(conn)
                    if msg == self.vl_msg:
                        self.v_usernames.pop(addr, None)
                        with self.v_clients_lock:
                            self.v_clients.remove(conn)
                    with self.clients_lock:
                        for c in self.clients:
                            c.send(self.encrypt(f"[{username}] {msg}", self.partner_keys.get(c.getpeername())))
                except Exception as e:
                    self.error_log.append(f"[Error handling messaging client ({username})] {e}")
                    print(self.error_log[-1])
                    break
        finally:
            with self.clients_lock:
                self.clients.remove(conn)
                self.c_list_bo.delete(self.c_list_bo.get(0, tk.END).index(f"{username} ({addr[0]}:{addr[1]})"))
                for c in self.clients:
                    c.send(self.encrypt(f"[SERVER] {username} Disconnected!", self.partner_keys.get(c.getpeername())))
                self.partner_keys.pop(addr, None)
                self.usernames.pop(addr, None)
                if addr in self.v_usernames:
                    self.v_usernames.pop(addr, None)
            conn.close()


    def tcp_connection_handler(self):
        while self.m_running:
            try:
                conn, addr = self.m_server.accept()
                with self.clients_lock:
                    self.clients.add(conn)
                threading.Thread(target=self.messaging_handler, args=(conn, addr), daemon=True).start()
            except Exception as e:
                self.error_log.append(f"[Error accepting incoming connection] {e}")
                print(self.error_log[-1])

    def start_messaging_server(self):
        try:
            self.m_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.m_server.bind(self.tcp)
            self.m_server.listen()
            threading.Thread(target=self.tcp_connection_handler, daemon=True).start()
        except Exception as e:
            self.error_log.append(f"[Error starting messaging server] {e}")
            print(self.error_log[-1])

    def start_voice_server(self):
        try:
            self.a_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.a_server.bind(self.udp)
            threading.Thread(target=self.voice_handler, daemon=True)
        except Exception as e:
            self.error_log.append(f"[Error starting voice server] {e}")
            print(self.error_log[-1])
    
    def start_server(self):
        self.start_messaging_server()
        self.start_voice_server()
        self.switch_to_client()

    def stop_voice_server(self):
        try:
            self.a_running = False
            with self.v_clients_lock:
                self.v_clients.clear()
            self.a_server.close()
        except Exception as e:
            self.error_log.append(f"[Error stopping voice server] {e}")
            print(self.error_log[-1])
    
    def stop_messaging_server(self):
        try:
            self.m_running = False
            with self.clients_lock:
                for c in self.clients:
                    tmp_key = self.partner_keys.get(c.getpeername())
                    c.send(self.encrypt(self.d_msg, tmp_key))
                self.clients.clear
        except Exception as e:
            self.error_log.append(f"[Error stopping messaging server] {e}")
            print(self.error_log[-1])

    def stop_server(self):
        self.stop_voice_server()
        self.stop_messaging_server()
        self.switch_to_host()
    
    def switch_to_client(self):
        self.frame.pack_forget()
        self.c_frame.pack(fill=tk.BOTH, expand=True)

    def switch_to_host(self):
        self.c_list_bo.delete(0, tk.END)
        self.c_frame.pack_forget()
        self.frame.pack(fill=tk.BOTH, expand=True)


if __name__ == '__main__':
    server = Server()