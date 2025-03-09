import netifaces as ni
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.label import MDLabel
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.progressindicator import MDLinearProgressIndicator


# ================== GET WIFI ADDRESS IF CONNECTED ======================
def get_wifi_addr() -> str:
    interfaces = ni.interfaces()                # Get all available interfaces
    wifi_addr = "Not connected to WIFI!"        # Get WIFI address if connected
    for interface in interfaces:
        addr = ni.ifaddresses(interface)        # Get interface info
        is_up = ni.AF_INET in addr              # Check if it has IPv4 addr (is up)
        if is_up and addr[2][0]['addr'].startswith("192.168"):
            wifi_addr = addr[2][0]['addr']      # Check if it is up and if it starts with 192.168
    return wifi_addr


# ================== DISPLAY SNACK BAR AT THE BOTTOM ==================
def snackbar(message: str) -> None:
    MDSnackbar(
        MDSnackbarText(
            text=f"[b]{message}[/b]",
            markup=True,
            theme_text_color="Custom",
            text_color=[0,0,0,1],
            font_style="Title",
        ),
        background_color=[.6,.6,.6,1],
        duration=2,
    ).open()

# ================== PROGRESS BAR WIDGET ===============================
def add_prog_bar(num: int) -> (MDLinearProgressIndicator, MDBoxLayout):
    colors = ["#ff1717", "#17ff17", "#1717ff", "#ffff17", '#17ffff', '#8817ff']
    label = MDLabel(
        markup=True,
        text=f"[color={colors[num]}][b]P{num + 1}[/color][/b]",
        theme_font_size="Custom",
        font_size="20sp",
        adaptive_width=True,
        pos_hint={'center_y': .5},
    )
    prog_bar = MDLinearProgressIndicator(
        value=0,
        size_hint_y=None,
        height="10dp",
        pos_hint={'center_x': .5, 'center_y': .5},
    )
    panel = MDBoxLayout(
        label,
        MDFloatLayout(
            prog_bar,
            size_hint=(1, 1)
        ),
        spacing="8dp"
    )
    return prog_bar, panel



