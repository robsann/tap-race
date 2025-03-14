import random
from kivy.lang import Builder
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.progressindicator import MDLinearProgressIndicator
from server import Server
from client import Client
from myutils import snackbar, add_prog_bar


if platform == 'android' or platform == 'ios':
   # Mobile-specific settings
   pass
else:
   # Desktop-specific settings
   Window.size = (300, 600)


class MenuHeader(MDBoxLayout):
    """An instance of the class that will be added to the menu header."""
    pass


class MenuWin(MDBoxLayout):
    """An instance of the class that will be added to the menu header."""
    pass


class MenuLose(MDBoxLayout):
    """An instance of the class that will be added to the menu header."""
    pass


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.server: Server | None = None
        self.client: Client | None = None

        self.server_ip_dialog: MDDialog | None = None
        self.prog_bars: list[MDLinearProgressIndicator] = []

        self.count: int = 0
        self.max_score = 10
        self.last_id: int = 0
        self.single_player: bool = True
        self.stop_flow = True

        # Add nasalization font
        self.add_nasa_font()

        # Create screen object
        self.screen = Builder.load_file('layout.kv')

        # Define menu items and create menus
        self.menu_items_settings = self.settings_menu_items()
        self.settings = self.settings_menu()

        self.menu_items = self.menu_items()
        self.top_menu = self.menu_header()
        self.menu_finish = self.menu_win()

    def start_server(self):
        """Start the server if not already running as server or client."""
        if self.server:
            snackbar("Already running as server!")
        elif self.client:
            snackbar("Already running as client!")
        else:
            self.server = Server()
            self.server.start_server()
            self.server.menu_win = self.menu_win()
            self.server.menu_lose = self.menu_lose()
            self.root.ids.nickname_label.text = \
                f"Nickname: [color=#ff0000][b]{self.server.nickname}[/b][/color]"
            self.single_player = False

    def start_client(self):
        """Start the client if not already running as server or client."""
        if self.server:
            snackbar("Already running as server!")
        elif self.client:
            snackbar("Already running as client!")
        else:
            self.client = Client()
            self.server_ip_dialog = self.dialog_box()
            self.server_ip_dialog.open()

    def dialog_box(self):
        """Create a dialog box for server IP input."""
        dialog = MDDialog(
            MDDialogHeadlineText(text="Enter Server IP"),
            MDDialogContentContainer(
                MDBoxLayout(
                    MDTextField(
                        MDTextFieldHintText(text="Server IP"),
                        id="text_field",
                        mode="outlined",
                        pos_hint={"center_x": .5, "top": 1},
                        size_hint_x=.8,
                    ),
                    MDBoxLayout(
                        MDButton(
                            MDButtonText(text="Connect"),
                            on_release=lambda obj: self.dialog_connect(),
                        ),
                        MDButton(
                            MDButtonText(text="Close"),
                            on_release=lambda obj: self.dialog_close(),
                        ),
                        adaptive_height=True,
                        adaptive_width=True,
                        spacing = "8dp",
                        pos_hint = {'center_x': .5},
                    ),
                    orientation="vertical",
                    adaptive_height=True,
                    spacing="12dp",
                ),
            ),
            size_hint=(.1, .1),
        )
        return dialog

    def dialog_connect(self):
        """Handle connect button in dialog."""
        self.client.server_addr = self.server_ip_dialog.get_ids().text_field.text
        self.server_ip_dialog.dismiss()
        self.client_connect()

    def dialog_close(self):
        """Handle close button in dialog."""
        self.server_ip_dialog.dismiss()
        self.client = None

    def client_connect(self):
        """Connect client to server using provided IP."""
        print(f"Server IP provided: {self.client.server_addr}")
        self.client.start_client()
        if self.client.is_connected:
            self.client.menu_win = self.menu_win()
            self.client.menu_lose = self.menu_lose()
            color = self.client.colors[self.client.idx]
            self.root.ids.nickname_label.text = \
                f"Nickname: [color={color}][b]{self.client.nickname}[/b][/color]"
            self.single_player = False
        else:
            self.client = None
            snackbar("Connection refused!")

    def random_id(self):
        """Randomly select the next highlighted button."""
        btn_id = random.sample(range(1, 5), 1)[0]
        self.last_id = btn_id
        self.change_button_color(btn_id, 1)

    def change_button_color(self, btn_id: int, val: float):
        """Change the color intensity of a button."""
        match btn_id:
            case 1:
                self.root.ids.btn1.md_bg_color[3] = val
            case 2:
                self.root.ids.btn2.md_bg_color[3] = val
            case 3:
                self.root.ids.btn3.md_bg_color[3] = val
            case 4:
                self.root.ids.btn4.md_bg_color[3] = val

    def add_nasa_font(self):
        """Register and configure the nasalization font."""
        LabelBase.register(
            name="nasalization",
            fn_regular="nasalization.ttf",
        )
        self.theme_cls.font_styles["nasalization"] = {
            "large": {
                "line-height": 1.64,
                "font-name": "nasalization",
                "font-size": "45sp",
            },
            "small": {
                "line-height": 1.44,
                "font-name": "nasalization",
                "font-size": "36sp",
            },
        }

    def set_max_score(self, score: int):
        self.max_score = score
        self.settings.dismiss()
        snackbar(f"Max Score: {score}")

    def settings_menu_items(self):
        menu_items = [
            {
                "text": f"Max Score: {i}",
                "on_release": lambda score=i: self.set_max_score(score)
            } for i in [10, 25, 50, 100]
        ]
        return menu_items

    def settings_menu(self):
        menu = MDDropdownMenu(
            # header_cls=MenuHeader(),
            caller=self.screen.ids.settings,
            items=self.menu_items_settings,
        )
        return menu

    def menu_items(self):
        """Define the menu items."""
        menu_items = [
            {
                "text": "Back to Home",
                "on_release": lambda: self.on_back_home(),
            },
            {
                "text": "Reset",
                "on_release": lambda: self.on_reset(),
            },
            {
                "text": "Exit",
                "on_release": lambda: self.on_exit(),
            },
            {}
        ]
        return menu_items

    def menu_header(self):
        """Create the top bar menu object."""
        menu = MDDropdownMenu(
            header_cls=MenuHeader(),
            caller=self.screen.ids.menu_btn,
            items=self.menu_items,
        )
        return menu

    def menu_win(self):
        """Create the win menu."""
        menu_win = MDDropdownMenu(
            header_cls=MenuWin(),
            caller=self.screen.ids.count_label,
            position='center',
            items=self.menu_items,
        )
        return menu_win

    def menu_lose(self):
        """Create the lose menu."""
        menu_lose = MDDropdownMenu(
            header_cls=MenuLose(),
            caller=self.screen.ids.count_label,
            position='center',
            items=self.menu_items,
        )
        return menu_lose

    def reset_uix_values(self):
        """Reset values on the screen."""
        self.root.ids.count_label.text = "0"

        # Reset progress bar values based on mode
        if self.server:
            for i in range(self.server.n_players):
                self.server.prog_bars[i].value = 0
        elif self.client:
            for i in range(self.client.n_players):
                self.client.prog_bars[i].value = 0
        else:
            for i in range(len(self.prog_bars)):
                self.prog_bars[i].value = 0

    def remove_prog_bars(self):
        """Remove progress bars from the grid layout."""
        prog_bar_grid = self.root.ids.prog_bar_grid
        children = prog_bar_grid.children.copy()
        for child in children:
            prog_bar_grid.remove_widget(child)

        if self.server:
            self.server.prog_bars = []
        else:
            self.prog_bars = []

    """
    ==================== APP EVENTS =====================================
    """
    def on_start_btn(self):
        """Handle start button press."""
        # For server mode
        if self.server and self.server.clients:
            self.server.broadcast(f'MAX_SCORE: {self.max_score}&')
            self.server.broadcast(f'STARTED_BY_SERVER&')
            self.server.start_game_screen()
        # For client mode
        elif self.client:
            self.client.client.send(f'MAX_SCORE: {self.max_score}&'.encode('ascii'))
            self.client.client.send('STARTED_BY_CLIENT&'.encode('ascii'))
        # For single player mode
        else:
            if self.server:
                self.server.close_connection(close_clients=False)
                self.server = None
                self.single_player = True

            # Add progress bar and change to screen B
            prog_bar, panel = add_prog_bar(num=0, max_score=self.max_score)
            self.prog_bars.append(prog_bar)
            self.root.ids.prog_bar_grid.add_widget(panel)
            self.root.current = "screen B"

    def on_press(self, btn_id: int):
        """Handle game button press."""
        # Remove button color intensity
        self.change_button_color(self.last_id, .2)

        print(f"Max score: {self.max_score}")

        # Pressing the correct button
        if btn_id == self.last_id:
            # For single player mode
            if self.single_player:
                self.count += 1
                # Update counter and progress bar
                self.root.ids.count_label.text = str(self.count)
                self.prog_bars[0].value = self.count
                # Verify if won
                if self.count == self.max_score:
                    self.menu_finish.open()
            # For server mode
            elif self.server and not self.single_player:
                self.server.count += 1
                self.server.update_counter(self.server.count, 0)
                self.server.players_score[0] = self.server.count
                # Send count to all clients
                message = f"COUNT-{self.server.nickname}: {self.server.count}&"
                self.server.broadcast(message)
                print(f"To Client: {message}")
                # Check if won
                if self.server.count == self.max_score:
                    self.server.menu_win.open()
                    self.server.broadcast('LOSE&')
            # For client mode
            elif self.client:
                # Update counter
                self.client.count += 1
                # Send count to server
                message = f"COUNT-{self.client.nickname}: {self.client.count}&"
                self.client.client.send(message.encode('ascii'))
                print(f"To Server: {message}")
                # Check if won
                if self.client.count == self.max_score:
                    self.client.menu_win.open()
                    self.client.client.send('LOSE&'.encode('ascii'))

        # Generate next button with high intensity color
        self.random_id()

    def on_reset(self):
        """Reset counter and UI values."""
        # Reset for single player mode
        if self.single_player:
            self.count = 0
            self.reset_uix_values()
            self.top_menu.dismiss()
            self.menu_finish.dismiss()
        # Reset for server mode
        elif self.server:
            self.server.count = 0
            self.reset_uix_values()
            self.top_menu.dismiss()
            self.server.menu_win.dismiss()
            self.server.menu_lose.dismiss()
            self.server.broadcast('RESET&')
        # Reset for client mode
        elif self.client:
            self.top_menu.dismiss()
            if self.client.is_connected:
                self.client.client.send('RESET&'.encode('ascii'))

    def on_back_home(self):
        """Return to home screen."""
        # For single player mode
        if self.single_player:
            self.on_reset()
            self.remove_prog_bars()
            self.top_menu.dismiss()
            self.root.ids.nickname_label.text = ""
            self.root.current = "screen A"
        # For  server mode
        elif self.server:
            self.server.broadcast('RESTARTED_BY_SERVER&')
            self.server.update_reset()
            self.server.update_back_home()
            self.server.close_connection(close_clients=False)
            self.server = None
            self.top_menu.dismiss()
        # For client mode
        elif self.client:
            self.top_menu.dismiss()
            if self.client.is_connected:
                self.client.client.send('RESTARTED_BY_CLIENT&'.encode('ascii'))
            self.client = None

    def on_exit(self):
        """Close server/client/app."""
        # Close Server
        if self.server:
            self.server.close_connection(close_clients=True)
            print("Server closed!")
        # Close client
        elif self.client:
            self.client.close_connection(by_client=False)
            print("Client closed!")

        # Close app
        self.stop()
        print("App closed!")

    def on_home_screen(self):
        """Reset server/client when returning to home screen."""
        if self.server:
            self.server = None
        elif self.client:
            self.client = None

    def on_start(self):
        """Run on app initialization."""
        # Generate random id for the first highlighted button
        self.random_id()

    def build(self):
        """Build the app layout."""
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"

        return self.screen


if __name__ == "__main__":
    MainApp().run()
