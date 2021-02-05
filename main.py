import os
from threading import Thread
from android.runnable import run_on_ui_thread
from flask import Flask, redirect, render_template
from android.runnable import run_on_ui_thread
from jnius import autoclass
from android.permissions import Permission, request_permissions
import requests

request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

app = Flask(__name__)
app.config.from_object(__name__)


def change_statusbar_color(statuscolor, icons_color="Light"):
    Color = autoclass("android.graphics.Color")
    WindowManager = autoclass("android.view.WindowManager$LayoutParams")
    activity = autoclass("org.kivy.android.PythonActivity").mActivity
    View = autoclass("android.view.View")

    def statusbar(*args):
        color = statuscolor[:7]
        window = activity.getWindow()

        if icons_color == "Dark":
            window.getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
            )
        elif icons_color == "Light":
            window.getDecorView().setSystemUiVisibility(0)

        window.clearFlags(WindowManager.FLAG_TRANSLUCENT_STATUS)
        window.addFlags(WindowManager.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS)
        window.setStatusBarColor(Color.parseColor(color))
        window.setNavigationBarColor(Color.parseColor(color))

    status = run_on_ui_thread(statusbar)

    return status()


change_statusbar_color("#90caf9ff")

webview = autoclass('org.kivy.android.PythonActivity').mWebView
getAppRoot = autoclass('org.kivy.android.PythonActivity').getAppRoot

data_gone = False


def check_network_lost_internet_access(host="https://google.com", port=80, timeout=1):
    global data_gone
    try:
        requests.get("https://google.com", timeout=3)
        print("connected")
        return True
    except (requests.ConnectionError, requests.Timeout):
        print("Not Connected")
        return False

current_url = None


@run_on_ui_thread
def change_data_error():
    global data_gone, current_url
    print(webview.getUrl())
    if webview.getUrl().endswith("error.html"):
        return
    current_url = webview.getUrl()
    webview.loadUrl(f"file:///{getAppRoot()}/templates/error.html")
    print("loaded")


@run_on_ui_thread
def change_data_noerror():
    global data_gone, current_url
    if not webview.getUrl().endswith("error.html"):
        return
    webview.loadUrl(current_url)
    print("me me me")


def check_network():
    global data_gone, current_url
    while True:
        if not check_network_lost_internet_access():
            print(data_gone)
            change_data_error()
        else:
            change_data_noerror()


Thread(target=check_network).start()
print(f"file:///{getAppRoot()}/assets/error.html")


def get_file(filename):  # pragma: no cover
    try:
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        html = open(filename).read()
        html = html.replace("acbt_internet.jpg", f"{getAppRoot()}/assets/error.jpg")
        return html
    except IOError as exc:
        return str(exc)


@app.route('/')
def hello():
    return redirect('https://acbt.i.ng/verify_access')


@app.route('/error')
def error():
    print("hoooo")
    # content = get_file("templates/error.html")
    return render_template("error.html")


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
