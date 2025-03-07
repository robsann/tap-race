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
            self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.client.settimeout(2)
            self.client.connect((self.server_addr, 55555))

            self.is_connected = True
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
            try:
                # Get data from server
                msg = self.client.recv(1024).decode('ascii')
                print(f"msg from server: {msg}")
                match msg:
                    case s if s.startswith('P'):
                        # Get nickname
                        self.nickname = msg
                        self.idx = int(msg[1]) - 1
                        print(f"Client connected as {self.nickname}")
                        self.update_snackbar()
                    case s if s.startswith('STARTED_BY_SERVER'):
                        # Start game
                        self.n_players = int(msg[19])
                        self.players_score = [0 for _ in range(self.n_players)]
                        self.start_game_screen()
                    case s if s.startswith('COUNT'):
                        # Receive server score
                        idx = int(msg[7]) - 1
                        count = int(msg[10:])
                        self.players_score[idx] = count
                        self.update_counter(count, idx)
                    case s if s.startswith('LOSE'):
                        # Open lose menu
                        self.update_menu_lose()
                    case s if s.startswith('RESET'):
                        # Reset score and progress bars
                        self.update_reset()
                    case s if s.startswith('RESTART'):
                        # Remove everything and stop thread
                        self.back_home()
                        break
                    case s if s.startswith('CLOSED_BY_SERVER'):
                        # Close connection, remove everything, and stop thread
                        self.client.send('CLOSED_BY_SERVER_ACK'.encode('ascii'))
                        self.client.close()
                        self.is_connected = False
                        self.back_home()
                        break
                    case s if s.startswith('CLOSED_BY_CLIENT_ACK'):
                        # Stop thread
                        print('CLOSED_BY_CLIENT_ACK')
                        break

            except TimeoutError as e:
                pass
            except Exception as e:
                print(f"Exception caught in receive_data: {e}")
                self.client.close()
                self.is_connected = False
                break


    # ================== CLOSE CLIENT SOCKET ============================
    def close_connection(self):
        if self.is_connected:
            self.client.send('CLOSED_BY_CLIENT'.encode('ascii'))
            self.receive_data_thread.join()

        self.client.close()
        self.is_connected = False


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
        for i in range(self.n_players):
            grid = MDApp.get_running_app().root.ids.prog_bar_grid
            grid.remove_widget(self.prog_bars[i])
        self.prog_bars = []
        MDApp.get_running_app().root.ids.nickname_label.text = ""
        MDApp.get_running_app().root.current = "screen A"

