import socket
from threading import Thread
from kivy.clock import mainthread
from kivymd.app import MDApp
from myutils import snackbar, get_wifi_addr


class Server:
    def __init__(self):
        self.server: socket.socket | None = None
        self.handle_connection_thread: Thread | None = None
        self.receive_data_thread: Thread | None = None
        self.nickname: str | None = "P1"
        self.stop_thread: bool = False
        self.is_running: bool = False
        self.menu_win = None
        self.menu_lose = None
        self.count = 0

        # Create lists for clients, nicknames, and players_count
        self.clients: list[socket] = []
        self.nicknames: list[str] = []
        self.players_count: list[int] = [0, 0]

        # Get WIFI IP address if connected
        self.ip_addr = get_wifi_addr()

        self.start_server()

    # ================== START SERVER ===================================
    def start_server(self):
        # Create socket, bind IP/port, set to listen mode and connection timeout
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.ip_addr, 55555))
        self.server.listen()
        self.server.settimeout(2)       # For any socket operation
        self.is_running = True

        # Start new thread to run receive_connection()
        try:
            self.handle_connection_thread = Thread(target=self.handle_connection)
            self.handle_connection_thread.start()
        except Exception as e:
            print(f"Error starting handle_connection thread on server: {e}")

        snackbar("Server is listening")

    # ================== THREAD-1: RECEIVE CONNECTION FROM NEW CLIENT ====
    def handle_connection(self):
        while True:
            if self.stop_thread:
                break
            try:
                # Accept new incoming connections
                client, (addr, port) = self.server.accept()
                print(f"Connected with ({addr}, {port})")

                # Append client socket and nickname to lists
                nickname = "P" + str(len(self.nicknames) + 2)
                self.clients.append(client)
                self.nicknames.append(nickname)
                self.players_count.append(0)

                # Send nickname to client
                client.send(nickname.encode('ascii'))
                print(f'{nickname} connected!')
                self.update_snackbar(f"{nickname} connected!")

                # Start new thread to run handle_communication()
                try:
                    self.receive_data_thread = Thread(target=self.receive_data, args=(client,))
                    self.receive_data_thread.start()
                except Exception as e:
                    print(f"Error starting receive_data thread on server: {e}")
            except TimeoutError as e:
                pass
            except Exception as e:
                print(f"Exception caught in receive_connection: {e}")

    # ================== THREAD-2: HANDLE COMMUNICATION WITH CLIENT =====
    def receive_data(self, client):
        while True:
            try:
                # Receive data from client
                msg = client.recv(1024).decode('ascii')

                if msg.startswith('START'):
                    client.send(f'START: {len(self.players_count)}'.encode('ascii'))
                    self.update_screen()
                elif msg.startswith('COUNT'):
                    print(f"From Client: {msg}")
                    i = int(msg[6])
                    count = int(msg[9:])
                    self.players_count[i] = count
                    self.update_counter(count)
                elif msg.startswith('LOSE'):
                    self.update_menu_lose()
                elif msg.startswith('RESET'):
                    self.update_reset()
                elif msg.startswith('CLOSED_BY_CLIENT'):
                    index = self.clients.index(client)
                    nickname = self.nicknames[index]
                    self.clients.remove(client)
                    self.nicknames.remove(nickname)
                    client.send('CLOSED_BY_CLIENT'.encode('ascii'))        # Free client communication thread
                    client.close()
                    print(f"{nickname} disconnected!")
                    break
                elif msg.startswith('CLOSED_BY_SERVER'):
                    client.close()
                    break
                else:
                    self.broadcast(msg)
            except TimeoutError as e:
                pass
            except Exception as e:
                print(f"Exception caught in receive_data: {e}")
                break

    @mainthread
    def update_screen(self):
        MDApp.get_running_app().root.current = "screen B"

    @mainthread
    def update_snackbar(self, message):
        snackbar(message)

    @mainthread
    def update_counter(self, count: int):
        MDApp.get_running_app().root.ids.count_label_2.text = str(count)
        MDApp.get_running_app().root.ids.prog_bar_2.value = count * 10

    @mainthread
    def update_menu_lose(self):
        self.menu_lose.open()

    @mainthread
    def update_reset(self):
        self.count = 0
        MDApp.get_running_app().root.ids.prog_bar_1.value = 0
        MDApp.get_running_app().root.ids.count_label_1.text = "0"
        MDApp.get_running_app().root.ids.prog_bar_2.value = 0
        MDApp.get_running_app().root.ids.count_label_2.text = "0"
        self.menu_win.dismiss()
        self.menu_lose.dismiss()

    # ================== SEND MESSAGE TO ALL CLIENTS ====================
    def broadcast(self, message):
        for client in self.clients:
            client.send(message.encode('ascii'))

    # ================== CLOSE SERVER SOCKET =============================
    def close_connection(self):
        if self.is_running:
            clients = self.clients.copy()
            for client in clients:
                index = self.clients.index(client)
                nickname = self.nicknames[index]
                self.clients.remove(client)
                self.nicknames.remove(nickname)

                print(f"Disconnecting client {nickname}")
                client.send('CLOSED_BY_SERVER'.encode('ascii'))

            self.stop_thread = True
            self.handle_connection_thread.join()

        self.server.close()


