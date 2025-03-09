import socket
from threading import Thread
from kivy.clock import mainthread
from kivymd.app import MDApp
from kivymd.uix.progressindicator import MDLinearProgressIndicator
from kivymd.uix.menu import MDDropdownMenu
from myutils import snackbar, get_wifi_addr, add_prog_bar


class Server:
    def __init__(self):
        self.server: socket.socket | None = None
        self.handle_connection_thread: Thread | None = None
        self.receive_data_thread: Thread | None = None
        self.stop_thread: bool = False

        self.nickname: str | None = "P1"

        self.menu_win: MDDropdownMenu | None = None
        self.menu_lose: MDDropdownMenu | None = None

        self.count: int = 0
        self.n_players: int = 1

        # Create lists for clients, nicknames, and players_score
        self.clients: list[socket] = []
        self.nicknames: list[str] = []
        self.players_score: list[int] = [0]
        self.prog_bars: list[MDLinearProgressIndicator] = []

        # Get WIFI IP address if connected
        self.ip_addr: str = get_wifi_addr()
        print(f"Server IP: {self.ip_addr}")

        if self.ip_addr.startswith("Not connected"):
            MDApp.get_running_app().root.ids.ip_label.text = self.ip_addr
        else:
            MDApp.get_running_app().root.ids.ip_label.text = f"Your IP: {self.ip_addr}"


    # ================== START SERVER ===================================
    def start_server(self):
        try:
            # Create socket, bind IP/port, set to listen mode and connection timeout
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.server.bind((self.ip_addr, 55555))
            self.server.listen()
            self.server.settimeout(1)

            try:
                # Start new thread to run handle_connection()
                self.handle_connection_thread = Thread(target=self.handle_connection)
                self.handle_connection_thread.start()
                snackbar("Server is listening!")
            except Exception as e:
                print(f"Error starting handle_connection thread on server: {e}")

        except Exception as e:
            print(f"Error starting server: {e}")


    # ================== THREAD-1: RECEIVE CONNECTION FROM NEW CLIENT ====
    def handle_connection(self):
        while True:
            if self.stop_thread:
                break
            try:
                # Wait for new incoming connections
                client, (addr, port) = self.server.accept()
                print(f"Connected with ({addr}, {port})")

                # Append client socket, nickname, and score to lists
                nickname = f"P{(len(self.nicknames) + 2)}"
                self.clients.append(client)
                self.nicknames.append(nickname)
                self.players_score.append(0)
                self.n_players += 1

                # Send nickname to client
                client.send(f"{nickname}&".encode('ascii'))
                print(f'{nickname} connected!')
                self.update_snackbar(f"{nickname} connected!")

                try:
                    # Start new thread to run receive_data()
                    self.receive_data_thread = Thread(target=self.receive_data, args=(client,))
                    self.receive_data_thread.start()
                except Exception as e:
                    print(f"Error starting receive_data thread on server: {e}")

                # Update number of player on clients
                self.broadcast(f'NPLAYERS: {self.n_players}&')

            except TimeoutError:
                    pass
            except Exception as e:
                print(f"Exception caught in receive_connection: {e}")


    # ================== THREAD-2: HANDLE COMMUNICATION WITH CLIENT =====
    def receive_data(self, client):
        while True:
            if self.stop_thread:
                break
            try:
                # Wait for data from client and deal with buffered data
                msg_recv = client.recv(1024).decode('ascii')
                msg_recv = msg_recv.split('&')[:-1]

                for msg in msg_recv:
                    print(f"msg from client: {msg}")
                    match msg:
                        # Start game
                        case s if s.startswith('STARTED_BY_CLIENT'):
                            self.broadcast(f'STARTED_BY_CLIENT&')
                            self.start_game_screen()
                        # Receive client score
                        case s if s.startswith('COUNT'):
                            self.broadcast(f"{msg}&")
                            idx = int(msg[7]) - 1
                            count = int(msg[10:])
                            self.players_score[idx] = count
                            self.update_counter(count, idx)
                        # Open lose menu
                        case s if s.startswith('LOSE'):
                            self.broadcast(f"{msg}&")
                            self.update_menu_lose()
                        # Reset score and progress bars
                        case s if s.startswith('RESET'):
                            self.broadcast(f"{msg}&")
                            self.update_reset()
                        # Remove everything and stop thread
                        case s if s.startswith('RESTARTED_BY_CLIENT'):
                            self.broadcast(f"{msg}&")
                            self.update_reset()
                            self.update_back_home()
                            self.close_connection(close_clients=False)
                        # Close connection, remove everything, and stop thread
                        case s if s.startswith('CLOSED_BY_CLIENT'):
                            nickname = self.nicknames[self.clients.index(client)]
                            self.clients.remove(client)
                            self.nicknames.remove(nickname)
                            client.send('CLOSED_BY_CLIENT_ACK&'.encode('ascii'))
                            self.update_snackbar(f"{nickname} disconnected!")
                            print(f"{nickname} disconnected!")
                        # Acknowledge from client
                        case s if s.startswith('CLOSED_BY_SERVER_ACK'):
                            client.close()
                            self.stop_thread = True
                        # Any other message is broadcast to clients
                        case _:
                            self.broadcast(msg)

            except TimeoutError:
                pass
            except Exception as e:
                print(f"Exception caught in receive_data: {e}")
                break


    # ================== SEND MESSAGE TO ALL CLIENTS ====================
    def broadcast(self, message):
        print(f"Broadcasting: {message}")
        for client in self.clients:
            client.send(message.encode('ascii'))


    # ================== CLOSE SERVER SOCKET =============================
    def close_connection(self, close_clients=True):
        if close_clients:
            clients = self.clients.copy()
            for client in clients:
                index = self.clients.index(client)
                nickname = self.nicknames[index]
                self.clients.remove(client)
                self.nicknames.remove(nickname)
                print(f"Disconnecting client {nickname}")
                client.send('CLOSED_BY_SERVER&'.encode('ascii'))

        self.stop_thread = True
        self.handle_connection_thread.join()
        self.server.close()


    # ================== FUNCTIONS EXECUTED ON MAIN THREAD ================
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
    def update_snackbar(self, message):
        snackbar(message)

    @mainthread
    def update_counter(self, count: int, idx: int):
        self.prog_bars[idx].value = count * 10
        if idx == 0:
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
    def update_back_home(self):
        # Remove progress bars from MDGridLayout
        prog_bar_grid = MDApp.get_running_app().root.ids.prog_bar_grid
        children = prog_bar_grid.children.copy()
        for child in children:
            prog_bar_grid.remove_widget(child)
        self.prog_bars = []

        MDApp.get_running_app().root.ids.nickname_label.text = ""
        MDApp.get_running_app().root.current = "screen A"


