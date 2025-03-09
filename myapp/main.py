import random
from kivy.lang import Builder
from kivy.core.text import LabelBase
from kivy.core.window import Window
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


"""======================================================================
                    CUSTOM LAYOUT CLASSES USED IN MAIN
======================================================================"""
class MenuHeader(MDBoxLayout):
    """An instance of the class that will be added to the menu header."""


class MenuWin(MDBoxLayout):
    """An instance of the class that will be added to the menu header."""


class MenuLose(MDBoxLayout):
    """An instance of the class that will be added to the menu header."""


"""======================================================================
                            MAIN CLASS
======================================================================"""
class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.server: Server | None = None
        self.client: Client | None = None

        self.server_ip_dialog: MDDialog | None = None
        self.prog_bars: list[MDLinearProgressIndicator] = []

        self.count: int = 0
        self.last_id: int = 0
        self.single_player: bool = True
        self.stop_flow = True

        # Add nasalization font
        self.add_nasa_font()

        # Create screen object
        self.screen = Builder.load_file('layout.kv')

        # Define menu items
        self.menu_items = self.menu_items()

        # Create top bar menu object
        self.top_menu = self.menu_header()

        # Create menu displayed at finish
        self.menu_finish = self.menu_win()


    """
    ==================== START SERVER ===================================
    """
    def start_server(self):
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

    """
    ==================== START CLIENT ===================================
    """
    def start_client(self):
        if self.server:
            snackbar("Already running as server!")
        elif self.client:
            snackbar("Already running as client!")
        else:
            self.client = Client()
            self.server_ip_dialog = self.dialog_box()
            self.server_ip_dialog.open()

    # ================== Server IP Dialog Box ===========================
    def dialog_box(self):
        dialog = MDDialog(
            MDDialogHeadlineText(text="Enter Server IP"),
            MDDialogContentContainer(
                MDBoxLayout(
                    MDTextField(                                    # TODO: text_field
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

    # ================== CONNECT BUTTON =================================
    def dialog_connect(self):
        self.client.server_addr = self.server_ip_dialog.get_ids().text_field.text
        self.server_ip_dialog.dismiss()
        self.client_connect()

    # ================== CLOSE BUTTON ===================================
    def dialog_close(self):
        self.server_ip_dialog.dismiss()
        self.client = None

    # ================== CONNECT CLIENT TO SERVER =======================
    def client_connect(self):
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

    """
    ==================== GAME FUNCTIONS =================================
    """
    # ================== RANDOMLY SELECT NEXT HIGHLIGHTED BUTTON ========
    def random_id(self):
        btn_id = random.sample(range(1, 5), 1)[0]
        self.last_id = btn_id
        self.change_button_color(btn_id, 1)

    # ================== CHANGE BUTTON COLOR ============================
    def change_button_color(self, btn_id: int, val: float):
        match btn_id:
            case 1:
                self.root.ids.btn1.md_bg_color[3] = val
            case 2:
                self.root.ids.btn2.md_bg_color[3] = val
            case 3:
                self.root.ids.btn3.md_bg_color[3] = val
            case 4:
                self.root.ids.btn4.md_bg_color[3] = val

    """
    ==================== UIX FUNCTIONS ==================================
    """
    # ================== ADD NASALIZATION FONT ==========================
    def add_nasa_font(self):
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

    # ================== DEFINE MENU ITEMS ==============================
    def menu_items(self):
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

    # ================== CREATE TOP BAR MENU OBJECT =====================
    def menu_header(self):
        menu = MDDropdownMenu(
            header_cls=MenuHeader(),
            caller=self.screen.ids.menu_btn,
            items=self.menu_items,
        )
        return menu

    # ================== DEFINE MENU WIN ================================
    def menu_win(self):
        menu_win = MDDropdownMenu(
            header_cls=MenuWin(),
            caller=self.screen.ids.count_label,
            position='center',
            items=self.menu_items,
        )
        return menu_win

    # ================== DEFINE MENU LOSE ===============================
    def menu_lose(self):
        menu_lose = MDDropdownMenu(
            header_cls=MenuLose(),
            caller=self.screen.ids.count_label,
            position='center',
            items=self.menu_items,
        )
        return menu_lose

    # ================== RESET VALUES ON THE SCREEN =====================
    def reset_uix_values(self):
        self.root.ids.count_label.text = "0"
        if self.server:
            for i in range(self.server.n_players):
                self.server.prog_bars[i].value = 0
        elif self.client:
            for i in range(self.client.n_players):
                self.client.prog_bars[i].value = 0
        else:
            for i in range(len(self.prog_bars)):
                self.prog_bars[i].value = 0

    # ================== REMOVE PROGRESS BARS ===========================
    def remove_prog_bars(self):
        if self.server:
            # Remove progress bars from MDGridLayout
            prog_bar_grid = self.root.ids.prog_bar_grid
            children = prog_bar_grid.children.copy()
            for child in children:
                prog_bar_grid.remove_widget(child)
            self.server.prog_bars = []
        else:
            # Remove progress bars from MDGridLayout
            prog_bar_grid = self.root.ids.prog_bar_grid
            children = prog_bar_grid.children.copy()
            for child in children:
                prog_bar_grid.remove_widget(child)
            self.prog_bars = []

    """
    ==================== PRESSING APP BUTTONS ===========================
    """
    #  ================== ON DISPLAYING SCREEN A ========================
    def on_home_screen(self):
        if self.server:
            self.server = None
        elif self.client:
            self.client = None

    # ================== ON START BUTTON ================================
    def on_start_btn(self):
        if self.server and self.server.clients:
            self.server.broadcast(f'STARTED_BY_SERVER: {self.server.n_players}&')
            self.server.start_game_screen()
        elif self.client:
            self.client.client.send('STARTED_BY_CLIENT&'.encode('ascii'))
        else:
            # Single Player
            if self.server:
                self.server.close_connection(close_clients=False)
                self.server = None
                self.single_player = True
            # Add progress bar and change to screen B
            prog_bar, panel = add_prog_bar(num=0)
            self.prog_bars.append(prog_bar)
            self.root.ids.prog_bar_grid.add_widget(panel)
            self.root.current = "screen B"

        # self.build_bars_panel()
        # self.root.current = "screen B"

    # ================== ON PRESS THE GAME BUTTON =======================
    def on_press(self, btn_id: int):
        # Remove button color intensity
        self.change_button_color(self.last_id, .2)

        # Pressing the correct button
        if btn_id == self.last_id:
            # Single Player
            if self.single_player:
                self.count += 1
                # Update counter and progress bar
                self.root.ids.count_label.text = str(self.count)
                self.prog_bars[0].value = self.count * 10
                # Verify if won
                if self.count == 10:
                    self.menu_finish.open()
            # Server mode
            elif self.server and self.server.clients:
                self.server.count += 1
                self.server.update_counter(self.server.count, 0)
                self.server.players_score[0] = self.server.count
                # Send count to all clients
                message = f"COUNT-{self.server.nickname}: {self.server.count}&"
                self.server.broadcast(message)
                print(f"To Client: {message}")
                # Check if won
                if self.server.count == 10:
                    self.server.menu_win.open()
                    self.server.broadcast('LOSE&')
            # Client mode
            elif self.client:
                # Update counter
                self.client.count += 1
                # Send count to server
                message = f"COUNT-{self.client.nickname}: {self.client.count}&"
                self.client.client.send(message.encode('ascii'))
                print(f"To Server: {message}")
                # Check if won
                if self.client.count == 10:
                    self.client.menu_win.open()
                    # TODO: modify for multiple clients
                    self.client.client.send('LOSE&'.encode('ascii'))

        # Generate next button with high intensity color
        self.random_id()

    # ================== ON RESET: RESET COUNTER ========================
    def on_reset(self):
        if self.single_player:
            self.count = 0
            self.reset_uix_values()
            self.top_menu.dismiss()
            self.menu_finish.dismiss()
        elif self.server:
            self.server.count = 0
            self.reset_uix_values()
            self.top_menu.dismiss()
            self.server.menu_win.dismiss()
            self.server.menu_lose.dismiss()
            self.server.broadcast('RESET&')
        elif self.client:
            self.top_menu.dismiss()
            if self.client.is_connected:
                self.client.client.send('RESET&'.encode('ascii'))

    # ================== ON BACK TO HOME: RETURN TO HOME SCREEN ========================
    def on_back_home(self):
        # Terminate single player
        if self.single_player:
            self.on_reset()
            self.remove_prog_bars()
            self.top_menu.dismiss()
            self.root.ids.nickname_label.text = ""
            self.root.current = "screen A"
        # Terminate server
        elif self.server:
            self.server.broadcast('RESTARTED_BY_SERVER&')
            self.server.update_reset()
            self.server.update_back_home()
            self.server.close_connection(close_clients=False)
            self.server = None
            self.top_menu.dismiss()
        # Terminate client
        elif self.client:
            self.top_menu.dismiss()
            if self.client.is_connected:
                self.client.client.send('RESTARTED_BY_CLIENT&'.encode('ascii'))
            self.client = None

    # ================== ON EXIT: CLOSE SERVER/CLIENT/APP ===============
    def on_exit(self):
        if self.server:
            self.server.close_connection(close_clients=True)
            print("Server closed!")
        elif self.client:
            self.client.close_connection(by_client=False)
            print("Client closed!")

        # Close app
        self.stop()
        print("App closed!")


    """
    ==================== BUILDING APP ===================================
    """
    # ================== ON START: STARTING THE APP =====================
    def on_start(self):
        # Generate random id for the first highlighted button
        self.random_id()

    # ================== BUILD THE LAYOUT ===============================
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        Window.size = (300, 600)    # Comment this when generating the APK file

        return self.screen


MainApp().run()