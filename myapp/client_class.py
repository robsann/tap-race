import socket
from threading import Thread
from kivy.clock import mainthread
from kivymd.app import MDApp
from myutils import snackbar


class Client:
    def __init__(self):
        self.client: socket.socket | None = None
        self.server_addr = '192.168.0.7'
        self.nickname: str | None = None
        self.players_count: list[int] = []
        self.receive_data_thread: Thread | None = None
        self.is_connected: bool = False
        self.menu_win = None
        self.menu_lose = None
        self.count = 0
        self.start_client()

    # ================== START CLIENT ===================================
    def start_client(self):
        try:
            # Create socket for client and connect to server
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.server_addr, 55555))         # TODO: get server IP and port
            self.is_connected = True

            # Start new thread to run receive_data()
            try:
                self.receive_data_thread = Thread(target=self.receive_data)
                self.receive_data_thread.start()
            except Exception as e:
                print(f"Error starting receive_data thread on client: {e}")
        except ConnectionRefusedError:
            snackbar("Connection refused!")

    # ================== THREAD: RECEIVE DATA FROM SERVER ===============
    def receive_data(self):
        while True:
            try:
                # Get data from server
                msg = self.client.recv(1024).decode('ascii')

                # Get nickname
                if msg.startswith('P'):
                    self.nickname = msg
                    print(f"Client connected as {self.nickname}")
                    self.update_snackbar()
                elif msg.startswith('START'):
                    n_players = int(msg[7])
                    self.players_count = [0 for _ in range(n_players)]
                    self.update_screen()
                elif msg.startswith('COUNT'):
                    print(f"From Server: {msg}")
                    i = int(msg[6])
                    count = int(msg[9:])
                    self.players_count[i] = count
                    self.update_counter(count)
                elif msg.startswith('LOSE'):
                    self.update_menu_lose()
                elif msg.startswith('RESET'):
                    self.update_reset()
                elif msg.startswith('CLOSED_BY_CLIENT'):
                    break
                elif msg.startswith('CLOSED_BY_SERVER'):
                    self.client.send('CLOSED_BY_SERVER'.encode('ascii'))
                    self.client.close()
                    self.is_connected = False
                    break
            except TimeoutError as e:
                pass
            except Exception as e:
                print(f"Exception caught in receive_data: {e}")
                self.client.close()
                self.is_connected = False
                break

    @mainthread
    def update_screen(self):
        MDApp.get_running_app().root.current = "screen B"

    @mainthread
    def update_snackbar(self):
        snackbar(f"Connected to server as {self.nickname}!")
    @mainthread
    def update_counter(self, count):
        MDApp.get_running_app().root.ids.count_label_1.text = str(count)
        MDApp.get_running_app().root.ids.prog_bar_1.value = count * 10

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

    # ================== CLOSE CLIENT SOCKET ============================
    def close_connection(self):
        if self.is_connected:
            self.client.send('CLOSED_BY_CLIENT'.encode('ascii'))
            self.receive_data_thread.join()

        self.client.close()
        self.is_connected = False


