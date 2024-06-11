import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Cliente de Chat")

        self.nickname = None
        self.ip = None
        self.port = None
        self.client = None
        self.connected = False

        self.create_login_interface()

    def create_login_interface(self):
        self.clear_window()

        self.label_ip = tk.Label(self.master, text="Dirección IP:")
        self.label_ip.pack(pady=5)

        self.ip_entry = tk.Entry(self.master)
        self.ip_entry.pack(pady=5)

        self.label_port = tk.Label(self.master, text="Puerto:")
        self.label_port.pack(pady=5)

        self.port_entry = tk.Entry(self.master)
        self.port_entry.pack(pady=5)

        self.label_nickname = tk.Label(self.master, text="Elige un nickname:")
        self.label_nickname.pack(pady=5)

        self.nickname_entry = tk.Entry(self.master)
        self.nickname_entry.pack(pady=5)

        self.accept_button = tk.Button(self.master, text="Aceptar", bg="green", fg="white", command=self.accept_info)
        self.accept_button.pack(pady=5)

    def create_chat_interface(self):
        self.clear_window()

        self.chat_area = scrolledtext.ScrolledText(self.master)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_area.config(state=tk.DISABLED)

        self.message_entry = tk.Entry(self.master)
        self.message_entry.pack(pady=5, fill=tk.X, padx=10)

        self.send_button = tk.Button(self.master, text="Enviar", bg="light blue", command=self.send_message)
        self.send_button.pack(pady=5)

        self.connect_to_server()

    def clear_window(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def accept_info(self):
        self.ip = self.ip_entry.get()
        self.port = int(self.port_entry.get())
        self.nickname = self.nickname_entry.get()
        if self.ip and self.port and self.nickname:
            self.create_chat_interface()

    def connect_to_server(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.ip, self.port))
            self.client.send(self.nickname.encode('utf-8'))
            self.connected = True
            self.receive_thread = threading.Thread(target=self.receive)
            self.receive_thread.start()
        except Exception as e:
            self.log_message(f"Error al conectar al servidor: {e}")

    def log_message(self, message):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, message + '\n')
        self.chat_area.yview(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def receive(self):
        while self.connected:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message == 'NICK':
                    continue
                self.log_message(message)
            except Exception as e:
                self.log_message(f"Un error ha ocurrido: {e}")
                self.client.close()
                self.connected = False
                break

    def send_message(self):
        if self.connected:
            message = f'{self.nickname}: {self.message_entry.get()}'
            try:
                self.client.send(message.encode('utf-8'))
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                self.log_message(f"Error al enviar el mensaje: {e}")
                self.client.close()
                self.connected = False

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()

