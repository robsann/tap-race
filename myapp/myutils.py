import netifaces as ni
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText


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
def snackbar(message):
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


