import socket
from threading import Thread
from kivy.clock import mainthread
from kivymd.app import MDApp
from kivymd.uix.progressindicator import MDLinearProgressIndicator
from kivymd.uix.menu import MDDropdownMenu
from myutils import snackbar, get_wifi_addr, add_prog_bar


class Client:
    """Client class for network communication and game state management."""
    def __init__(self):
        self.client: socket.socket | None = None
        self.receive_data_thread: Thread | None = None
        self.stop_thread: bool = False

        self.idx: int | None = None
        self.nickname: str | None = None
        self.server_addr: str | None = None
        self.is_connected: bool = False
        self.count: int = 0
        self.n_players: int = 0

        self.menu_win: MDDropdownMenu | None = None
        self.menu_lose: MDDropdownMenu | None = None

        self.players_score: list[int] = []
        self.prog_bars: list[MDLinearProgressIndicator] = []
        self.colors: list[str] = ["#ff1717", "#17ff17", "#1717ff", "#ffff17", '#17ffff', '#8817ff']

        # Get WIFI IP address if connected
        self.ip_addr = get_wifi_addr()
        print(f"Client IP: {self.ip_addr}")

        self.app = MDApp.get_running_app()
        if self.ip_addr.startswith("Not connected"):
            self.app.root.ids.ip_label.text = self.ip_addr
        else:
            self.app.root.ids.ip_label.text = f"Your IP: {self.ip_addr}"

    def start_client(self):
        """Initialize client socket and connect to server."""
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

    def receive_data(self):
        """Thread function to receive and process messages from the server."""
        while not self.stop_thread:
            try:
                # Get data from server
                msg_recv = self.client.recv(1024).decode('ascii')
                messages = msg_recv.split('&')[:-1]
                for msg in messages:
                    print(f"msg from server: {msg}")
                    self.process_message(msg)

            except TimeoutError:
                pass
            except Exception as e:
                print(f"Exception caught in receive_data: {e}")
                self.client.close()
                self.is_connected = False
                break

    def process_message(self, msg):
        """Process incoming messages based on their type."""
        # Get nickname
        if msg.startswith('P'):
            self.nickname = msg
            self.idx = int(msg[1]) - 1
            print(f"Client connected as {self.nickname}")
            self.update_snackbar()

        # Max score
        elif msg.startswith('MAX_SCORE'):
            max_score = int(msg[11:])
            self.app.max_score = max_score

        # Start game
        elif msg.startswith('STARTED_BY_SERVER') or msg.startswith('STARTED_BY_CLIENT'):
            self.players_score = [0 for _ in range(self.n_players)]
            self.start_game_screen()

        # Get number of players
        elif msg.startswith('NPLAYERS'):
            self.n_players = int(msg[10])
            self.players_score = [0 for _ in range(self.n_players)]

        # Receive server score
        elif msg.startswith('COUNT'):
            idx = int(msg[7]) - 1
            count = int(msg[10:])
            self.players_score[idx] = count
            self.update_counter(count, idx)

        # Open lose menu
        elif msg.startswith('LOSE'):
            if self.count < self.app.max_score:
                self.update_menu_lose()

        # Reset score and progress bars
        elif msg.startswith('RESET'):
            self.update_reset()

        # Remove everything and stop thread
        elif msg.startswith('RESTARTED_BY_SERVER') or msg.startswith('RESTARTED_BY_CLIENT'):
            self.update_reset()
            self.close_connection(by_client=True)
            self.update_back_home()
            self.stop_thread = True

        # Close connection, remove everything, and stop thread
        elif msg.startswith('CLOSED_BY_SERVER'):
            self.client.send('CLOSED_BY_SERVER_ACK&'.encode('ascii'))
            self.client.close()
            self.is_connected = False
            self.update_back_home()
            self.stop_thread = True

        # Ack message used to Stop thread
        elif msg.startswith('CLOSED_BY_CLIENT_ACK'):
            self.stop_thread = True

    def close_connection(self, by_client=False):
        """Close the client socket connection."""
        if self.is_connected and not by_client:
            self.client.send('CLOSED_BY_CLIENT&'.encode('ascii'))
            self.receive_data_thread.join()

        self.client.close()
        self.is_connected = False


    # UI update methods (executed on main thread)
    @mainthread
    def start_game_screen(self):
        """Add progress bar widgets and switch to game screen."""
        for i in range(self.n_players):
            prog_bar, panel = add_prog_bar(num=i, max_score=self.app.max_score)
            self.prog_bars.append(prog_bar)
            self.app.root.ids.prog_bar_grid.add_widget(panel)
        # Change to game screen (screen B)
        self.app.root.current = "screen B"

    @mainthread
    def update_snackbar(self):
        """Display connection status notification."""
        snackbar(f"Connected to server!")

    @mainthread
    def update_counter(self, count, idx):
        """Update progress bar and score display."""
        self.prog_bars[idx].value = count
        if idx == self.idx:
            self.app.root.ids.count_label.text = str(count)

    @mainthread
    def update_menu_lose(self):
        """Show the lose menu."""
        self.menu_lose.open()

    @mainthread
    def update_reset(self):
        """Reset all game state variables and UI elements."""
        self.count = 0
        self.app.root.ids.count_label.text = "0"
        if self.prog_bars:
            for i in range(self.n_players):
                self.prog_bars[i].value = 0

        # Dismiss win and lose menu
        if self.menu_win:
            self.menu_win.dismiss()
        if self.menu_lose:
            self.menu_lose.dismiss()

    @mainthread
    def update_back_home(self):
        """Remove progress bars widgets and return to home screen."""
        prog_bar_grid = self.app.root.ids.prog_bar_grid
        children = prog_bar_grid.children.copy()
        for child in children:
            prog_bar_grid.remove_widget(child)
        self.prog_bars = []

        self.app.root.ids.nickname_label.text = ""
        self.app.root.current = "screen A"

