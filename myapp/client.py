import socket
from threading import Thread
from kivy.clock import mainthread
from kivymd.app import MDApp
from kivymd.uix.progressindicator import MDLinearProgressIndicator
from kivymd.uix.menu import MDDropdownMenu
from myutils import snackbar, get_wifi_addr, add_prog_bar


class Client:
    def __init__(self):
        self.client: socket.socket | None = None
        self.receive_data_thread: Thread | None = None
        self.stop_thread: bool = False

        self.idx: int | None = None
        self.nickname: str | None = None
        self.server_addr: str | None = None
        self.is_connected: bool = False

        self.menu_win: MDDropdownMenu | None = None
        self.menu_lose: MDDropdownMenu | None = None

        self.count: int = 0
        self.n_players: int = 0

        self.players_score: list[int] = []
        self.prog_bars: list[MDLinearProgressIndicator] = []

        # Get WIFI IP address if connected
        self.ip_addr = get_wifi_addr()
        print(f"Client IP: {self.ip_addr}")

        if self.ip_addr.startswith("Not connected"):
            MDApp.get_running_app().root.ids.ip_label.text = self.ip_addr
        else:
            MDApp.get_running_app().root.ids.ip_label.text = f"Your IP: {self.ip_addr}"


    # ================== START CLIENT ===================================
    def start_client(self):
        try:
            # Create socket for client and connect to server
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.client.settimeout(2)
            self.client.connect((self.server_addr, 55555))

            self.is_connected = True
            print("Client is connected: True - start_client")
            MDApp.get_running_app().root.ids.ip_label.text = f"Your IP: {self.ip_addr}"

            # Start new thread to run receive_data()
            try:
                self.receive_data_thread = Thread(target=self.receive_data)
                self.receive_data_thread.start()
            except Exception as e:
                print(f"Error starting receive_data thread on client: {e}")

        except ConnectionRefusedError:
            snackbar("Connection refused!")
        except Exception as e:
            print(f"Error starting client: {e}")


    # ================== THREAD: RECEIVE DATA FROM SERVER ===============
    def receive_data(self):
        while True:
            if self.stop_thread:
                break
            try:
                # Get data from server
                msg_recv = self.client.recv(1024).decode('ascii')
                msg_recv = msg_recv.split('&')[:-1]
                for msg in msg_recv:
                    print(f"msg from server: {msg}")
                    match msg:
                        # Get nickname
                        case s if s.startswith('P'):
                            self.nickname = msg
                            self.idx = int(msg[1]) - 1
                            print(f"Client connected as {self.nickname}")
                            self.update_snackbar()
                        # Start game
                        case s if s.startswith('STARTED_BY_SERVER'):
                            self.n_players = int(msg[19])
                            self.players_score = [0 for _ in range(self.n_players)]
                            self.start_game_screen()
                        # Get number of players
                        case s if s.startswith('NPLAYERS'):
                            self.n_players = int(msg[10])
                            self.players_score = [0 for _ in range(self.n_players)]
                        # Receive server score
                        case s if s.startswith('COUNT'):
                            idx = int(msg[7]) - 1
                            count = int(msg[10:])
                            self.players_score[idx] = count
                            self.update_counter(count, idx)
                        # Open lose menu
                        case s if s.startswith('LOSE'):
                            self.update_menu_lose()
                        # Reset score and progress bars
                        case s if s.startswith('RESET'):
                            self.update_reset()
                        # Remove everything and stop thread
                        case s if s.startswith('RESTART'):
                            self.back_home()
                            self.stop_thread = True
                        # Close connection, remove everything, and stop thread
                        case s if s.startswith('CLOSED_BY_SERVER'):
                            self.client.send('CLOSED_BY_SERVER_ACK&'.encode('ascii'))
                            self.client.close()
                            self.is_connected = False
                            print("Client is connected: False - CLOSED_BY_SERVER")
                            self.back_home()
                            self.stop_thread = True
                        # Stop thread
                        case s if s.startswith('CLOSED_BY_CLIENT_ACK'):
                            print('CLOSED_BY_CLIENT_ACK')
                            self.stop_thread = True

            except TimeoutError:
                pass
            except Exception as e:
                print(f"Exception caught in receive_data: {e}")
                self.client.close()
                self.is_connected = False
                print("Client is connected: False - Exception in receive_data")
                break


    # ================== CLOSE CLIENT SOCKET ============================
    def close_connection(self):
        if self.is_connected:
            self.client.send('CLOSED_BY_CLIENT&'.encode('ascii'))
            self.receive_data_thread.join()

        self.client.close()
        self.is_connected = False
        print("Client is connected: False - close_connection")


    # ================== RUN ON MAIN THREAD ============================
    @mainthread
    def start_game_screen(self):
        # Add progress bar panel widgets to prog_bar_grid (screen B)
        for i in range(self.n_players):
            prog_bar, panel = add_prog_bar(num=i)
            self.prog_bars.append(prog_bar)
            MDApp.get_running_app().root.ids.prog_bar_grid.add_widget(panel)
        # Change to game screen (screen B)
        MDApp.get_running_app().root.current = "screen B"

    @mainthread
    def update_snackbar(self):
        snackbar(f"Connected to server!")

    @mainthread
    def update_counter(self, count, idx):
        self.prog_bars[idx].value = count * 10
        if idx == self.idx:
            MDApp.get_running_app().root.ids.count_label.text = str(count)

    @mainthread
    def update_menu_lose(self):
        self.menu_lose.open()

    @mainthread
    def update_reset(self):
        self.count = 0
        MDApp.get_running_app().root.ids.count_label.text = "0"
        for i in range(self.n_players):
            self.prog_bars[i].value = 0

        self.menu_win.dismiss()
        self.menu_lose.dismiss()

    @mainthread
    def back_home(self):
        prog_bar_grid = MDApp.get_running_app().root.ids.prog_bar_grid
        children = prog_bar_grid.children.copy()
        print(children)
        for child in children:
            print(child)
            prog_bar_grid.remove_widget(child)

        self.prog_bars = []
        MDApp.get_running_app().root.ids.nickname_label.text = ""
        MDApp.get_running_app().root.current = "screen A"

