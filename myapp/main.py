import random
from kivy.lang import Builder
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.button.button import MDIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from server_class import Server
from client_class import Client
from myutils import get_wifi_addr, snackbar


# ================== TOP BAR MENU =======================================
class MenuHeader(MDBoxLayout):
    """An instance of the class that will be added to the menu header."""


# ================== WIN MENU ===========================================
class MenuWin(MDBoxLayout):
    """An instance of the class that will be added to the menu header."""


# ================== LOSE MENU ==========================================
class MenuLose(MDBoxLayout):
    """An instance of the class that will be added to the menu header."""


"""======================================================================
                            MAIN CLASS
======================================================================"""
class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.count: int = 0
        self.last_id: int = 0
        self.single_player: bool = True
        self.server: Server | None = None
        self.client: Client | None = None

        # Add nasalization font
        self.add_nasa_font()

        # Create screen object
        self.screen = Builder.load_file('layout.kv')

        # Define menu items
        self.menu_items = self.menu_items()

        # Create top bar menu object
        self.menu = self.menu_header()

        # Create menu displayed at finish
        self.menu_finish = self.menu_win()

        # Get WIFI IP address if connected
        self.ip_addr = get_wifi_addr()


    """
    ==================== START SERVER/CLIENT ============================
    """

    # ================== START SERVER ===================================
    def start_server(self):
        self.single_player = False
        if not self.server and not self.client:
            self.server = Server()
            self.server.menu_win = self.menu_win()
            self.server.menu_lose = self.menu_lose()
            self.root.ids.nickname_label.text = \
                f"Nickname: [color=#ff0000][b]{self.server.nickname}[/b][/color]"
        elif self.server:
            snackbar("Already running as server!")
        else:
            snackbar("Already running as client!")

    # ================== START CLIENT ===================================
    def start_client(self):
        self.single_player = False
        if not self.server and not self.client:
            self.client = Client()
            self.client.menu_win = self.menu_win()
            self.client.menu_lose = self.menu_lose()
            self.root.ids.nickname_label.text = \
                f"Nickname: [color=#00ff00][b]{self.client.nickname}[/b][/color]"
            if not self.client.is_connected:
                self.client = None
                self.single_player = True
        elif self.server:
            snackbar("Already running as server!")
        else:
            snackbar("Already running as client!")


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
                "on_release": lambda: self.on_back_to_home(),
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
            caller=self.screen.ids.count_label_1,
            position='center',
            items=self.menu_items,
        )
        return menu_win

    # ================== DEFINE MENU LOSE ===============================
    def menu_lose(self):
        menu_lose = MDDropdownMenu(
            header_cls=MenuLose(),
            caller=self.screen.ids.count_label_1,
            position='center',
            items=self.menu_items,
        )
        return menu_lose

    # ================== RESET VALUES ON THE SCREEN =====================
    def reset_uix_values(self):
        self.root.ids.prog_bar_1.value = 0
        self.root.ids.count_label_1.text = "0"
        self.root.ids.prog_bar_2.value = 0
        self.root.ids.count_label_2.text = "0"


    """
    ==================== PRESSING APP BUTTONS ===========================
    """
    # ================== ON PRESS THE GAME BUTTON =======================
    def on_press(self, btn: MDIconButton, id: int):
        self.change_button_color(self.last_id, .2)  # Uncolor button
        if id == self.last_id:
            if self.single_player:
                self.count += 1
                self.root.ids.count_label_1.text = str(self.count)
                self.root.ids.prog_bar_1.value = self.count * 10
                if self.count == 10:
                    self.menu_finish.open()
            elif self.server and self.server.clients:
                self.server.count += 1
                self.server.players_count[1] = self.server.count
                self.root.ids.count_label_1.text = str(self.server.count)
                self.root.ids.prog_bar_1.value = self.server.count * 10

                # Send count to all clients
                message = f"COUNT{self.server.nickname}: {self.server.count}"
                self.server.broadcast(message)
                print(f"To Client: {message}")

                # Check if client won
                if self.server.count == 10:
                    self.server.menu_win.open()
                    self.server.broadcast('LOSE')
            elif self.client:
                self.client.count += 1
                self.client.players_count[int(self.client.nickname[1])] = self.client.count
                self.root.ids.count_label_2.text = str(self.client.count)
                self.root.ids.prog_bar_2.value = self.client.count * 10

                # Send count to server
                message = f"COUNT{self.client.nickname}: {self.client.count}"
                self.client.client.send(message.encode('ascii'))
                print(f"To Server: {message}")

                # Check if someone won
                if self.client.count == 10:
                    self.client.menu_win.open()
                    self.client.client.send('LOSE'.encode('ascii'))        # TODO: modify for multiple clients
        self.random_id()

    # ================== ON START BUTTON ================================
    def on_start_btn(self):
        if self.server and self.server.clients:
            self.server.broadcast(f'START: {len(self.server.players_count)}')
            self.root.current = "screen B"
        elif self.client:
            self.client.client.send('START'.encode('ascii'))
        else:
            self.single_player = True
            self.root.current = "screen B"

    # ================== ON BACK TO HOME: RETURN TO HOME SCREEN ========================
    def on_back_to_home(self):
        self.on_reset()
        self.root.current = "screen A"

    # ================== ON RESET: RESET COUNTER ========================
    def on_reset(self):
        if self.single_player:
            self.count = 0
            self.reset_uix_values()
            self.menu.dismiss()
            self.menu_finish.dismiss()
        if self.server:
            self.server.count = 0
            self.reset_uix_values()
            self.server.menu_win.dismiss()
            self.server.menu_lose.dismiss()
            self.server.broadcast('RESET')
        elif self.client:
            self.client.count = 0
            self.reset_uix_values()
            self.client.menu_win.dismiss()
            self.client.menu_lose.dismiss()
            self.client.client.send('RESET'.encode('ascii'))

    # ================== ON EXIT: CLOSE SERVER/CLIENT/APP ===============
    def on_exit(self):
        if self.server:
            self.server.close_connection()
            print("Server closed!")
        elif self.client:
            self.client.close_connection()
            print("Client closed!")
        # Close app
        self.stop()
        print("App closed!")


    """
    ==================== BUILDING APP ===================================
    """
    # ================== ON START: STARTING THE APP =====================
    def on_start(self):
        self.random_id()  # Color random button
        print(self.ip_addr)
        self.root.ids.ip_label.text = f"Your IP: {self.ip_addr}"

    # ================== BUILD THE LAYOUT ===============================
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        Window.size = (300, 600)
        return self.screen


MainApp().run()