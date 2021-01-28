from flask import Flask, redirect
from android.runnable import run_on_ui_thread
from jnius import autoclass

app = Flask(__name__)


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


@app.route('/')
def hello():
    return redirect('https://acbt.i.ng/verify_access')


if __name__ == "__main__":
    app.run(debug=False)
