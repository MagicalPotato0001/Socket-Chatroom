import tkinter as tk
import customtkinter
from messaging_client import MessagingClient
from audio_client import AudioClient

class Client:
    def __init__(self,
                 use_gui = True,
                 verbose = True,
                 local = False):
        
        self.msg = None
        self.vc = None
        self.gui = use_gui
        self.voice = False
        self.verbose = verbose
        self.local = local

        if self.gui:
            customtkinter.set_appearance_mode("System")
            customtkinter.set_default_color_theme("blue")

            self.app = customtkinter.CTk()
            self.app.geometry("800x500")
            self.app.title("Chat Client")

            self.connect_frame = customtkinter.CTkFrame(self.app)
            self.connect_frame.pack(fill=tk.BOTH, expand=True)

            #IP Input
            self.ip_l = customtkinter.CTkLabel(self.connect_frame, text="IP Address:")
            self.ip_l.pack(pady=(10, 0))
            self.ip_in = customtkinter.CTkEntry(self.connect_frame)
            self.ip_in.insert(0, "127.0.0.1")
            self.ip_in.pack()

            #Messaging Port Input
            self.m_port_l = customtkinter.CTkLabel(self.connect_frame, text="Messaging Port(TCP):")
            self.m_port_l.pack(pady=(10,0))
            self.m_port_in = customtkinter.CTkEntry(self.connect_frame)
            self.m_port_in.insert(0, "5050")
            self.m_port_in.pack()

            #Voice Port Input
            self.v_port_l = customtkinter.CTkLabel(self.connect_frame, text="Voice Port(UDP):")
            self.v_port_l.pack(pady=(10,0))
            self.v_port_in = customtkinter.CTkEntry(self.connect_frame)
            self.v_port_in.insert(0, "12345")
            self.v_port_in.pack()

            #Username Input
            self.user_l = customtkinter.CTkLabel(self.connect_frame, text="Username:")
            self.user_l.pack(pady=(10,0))
            self.user_in = customtkinter.CTkEntry(self.connect_frame)
            self.user_in.insert(0, "ANON")
            self.user_in.pack()

            #Password Input
            self.pass_l = customtkinter.CTkLabel(self.connect_frame, text="Password:")
            self.pass_l.pack(pady=(10,0))
            self.pass_in = customtkinter.CTkEntry(self.connect_frame)
            self.pass_in.insert(0, "12345")
            self.pass_in.pack()

            #Connect Button
            self.connect_b = customtkinter.CTkButton(self.connect_frame, text="Connect", command=self.connect)
            self.connect_b.pack(pady=10)

            #Main Frame
            self.main_frame = customtkinter.CTkFrame(self.app)

            #Chat Frame
            self.chat_frame = customtkinter.CTkFrame(self.main_frame)
            self.chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            #Chat Log
            self.chat_l = customtkinter.CTkLabel(self.chat_frame, text="Chat:")
            self.chat_l.pack()
            self.chat_t = tk.Text(self.chat_frame, height=20, width=60, bg="#000000", fg="#FFFFFF")
            self.chat_t.pack()

            #Chat Input
            self.input_frame = customtkinter.CTkFrame(self.chat_frame)
            self.input_frame.pack(fill=tk.X, padx=10, pady=10)

            #Message Input
            self.msg_in = customtkinter.CTkEntry(self.input_frame, width=400)
            self.msg_in.pack(side=tk.LEFT, padx=(0, 5))

            #Send Button
            self.send_b = customtkinter.CTkButton(self.input_frame, text="Send", command=self.send_message)
            self.send_b.pack(side=tk.RIGHT)

            #Disconnect
            self.disconnect_b = customtkinter.CTkButton(self.chat_frame, text="Disconnect", command=self.disconnect)
            self.disconnect_b.pack(fill=tk.X, padx=10, pady=10)

            # Chatters Frame (right side)
            self.chatters_frame = customtkinter.CTkFrame(self.main_frame)
            self.chatters_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

            # Connected Chatters List
            self.c_chatters_l = customtkinter.CTkLabel(self.chatters_frame, text="Active(MSG)")
            self.c_chatters_l.pack()
            self.c_chatters_lb = tk.Listbox(self.chatters_frame, bg="#000000", fg="#FFFFFF")
            self.c_chatters_lb.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            # Voice Chatters List
            self.cv_chatters_l = customtkinter.CTkLabel(self.chatters_frame, text="Active(VC)")
            self.cv_chatters_l.pack()
            self.cv_chatters_lb = tk.Listbox(self.chatters_frame, bg="#000000", fg="#FFFFFF")
            self.cv_chatters_lb.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

            # Voice Connect/Disconnect Button
            self.voice_button = customtkinter.CTkButton(self.chatters_frame, text="Connect Voice", command=self.toggle_voice_connection)
            self.voice_button.pack(padx=10, pady=10)

            # Bind Enter key to send message function
            self.app.bind('<Return>', self.send_message)

            #Start Loop
            self.app.mainloop()
    

    def connect(self):
        self.msg = MessagingClient(server=(self.ip_in.get(), int(self.m_port_in.get())), username=self.user_in.get(), parent=self, server_pass=self.pass_in.get().encode("utf-8"), verbose=self.verbose)
        self.msg.connect()
        print("Connected Successfully")
        self.connect_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def disconnect(self):
        self.msg.disconnect()
        self.main_frame.pack_forget()
        self.connect_frame.pack(fill=tk.BOTH, expand=True)

    def send_message(self, event=None):
        message = self.msg_in.get()
        if message:
            self.msg.send(message)
            self.msg_in.delete(0, tk.END)

    def update_chat(self, msg):
        self.chat_t.insert(tk.END, msg + "\n")

    def update_list(self, data):
        self.c_chatters_lb.delete(0, tk.END)
        self.cv_chatters_lb.delete(0, tk.END)
        connected_clients = data.get("Connected Clients", [])
        for user in connected_clients:
            self.c_chatters_lb.insert(tk.END, user)
        voice_clients = data.get("Voice Clients", [])
        for user in voice_clients:
            self.c_chatters_lb.insert(tk.END, user)

    def voice_connect(self):
        self.voice = True
        self.vc = AudioClient(local=self.local)
        self.vc.start_streaming()

    def voice_disconnect(self):
        self.voice = False
        self.vc.terminate()

    def toggle_voice_connection(self):
        if self.voice:
            self.voice_disconnect()
            self.voice_button.configure(text="Connect Voice")
        else:
            self.voice_connect()
            self.voice_button.configure(text="Disconnect Voice")
    
if __name__ == "__main__":
    client = Client(local=True)


