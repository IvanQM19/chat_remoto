import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class ChatServerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Servidor de Chat")

        self.server = None
        self.clients = []
        self.nicknames = []

        self.create_interface()

    def create_interface(self):
        self.host_label = tk.Label(self.master, text="Host:")
        self.host_label.pack(pady=5)

        self.host_entry = tk.Entry(self.master)
        self.host_entry.pack(pady=5)
        self.host_entry.insert(0, '127.0.0.1')  # Default host

        self.port_label = tk.Label(self.master, text="Puerto:")
        self.port_label.pack(pady=5)

        self.port_entry = tk.Entry(self.master)
        self.port_entry.pack(pady=5)
        self.port_entry.insert(0, '55555')  # Default port

        self.connect_button = tk.Button(self.master, text="Conectar", bg="green", fg="white", command=self.start_server)
        self.connect_button.pack(pady=5)

        self.disconnect_button = tk.Button(self.master, text="Desconectar", bg="red", fg="white", command=self.stop_server)
        self.disconnect_button.pack(pady=5)

        self.log_area = scrolledtext.ScrolledText(self.master)
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.log_area.config(state=tk.DISABLED)

    def log_message(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + '\n')
        self.log_area.yview(tk.END)
        self.log_area.config(state=tk.DISABLED)

    def start_server(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()

        self.log_message(f"Servidor corriendo en {host}:{port}")

        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()

    def stop_server(self):
        if self.server:
            for client in self.clients:
                client.close()
            self.server.close()
            self.log_message("Servidor desconectado")
            self.server = None

    def broadcast(self, message):
        for client in self.clients:
            client.send(message)

    def handle(self, client):
        while True:
            try:
                message = client.recv(1024)
                self.broadcast(message)
            except:
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.broadcast(f'{nickname} salió del chat'.encode('utf-8'))
                self.nicknames.remove(nickname)
                break

    def receive(self):
        while self.server:
            try:
                client, address = self.server.accept()
                self.log_message(f"Conectado con {str(address)}")

                client.send('Nick'.encode('utf-8'))
                nickname = client.recv(1024).decode('utf-8')
                self.nicknames.append(nickname)
                self.clients.append(client)

                self.log_message(f'El nombre del cliente es: {nickname}')
                self.broadcast(f'{nickname} entró al chat'.encode('utf-8'))
                client.send('Conectado al servidor'.encode('utf-8'))

                thread = threading.Thread(target=self.handle, args=(client,))
                thread.start()
            except Exception as e:
                self.log_message(f"Error en la recepción: {e}")
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatServerGUI(root)
    root.mainloop()
