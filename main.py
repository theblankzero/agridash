import threading
import time
import webbrowser
import os
import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock

# Import the Flask app
# Ensure the current directory is in path so we can import agri_dash
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agri_dash import app as flask_app

class FlaskThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True

    def run(self):
        # Run Flask app
        # host='0.0.0.0' is important for Android
        flask_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

class AgriDashApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        self.status_label = Label(
            text="Starting AgriDash Server...",
            font_size='20sp',
            halign='center'
        )
        layout.add_widget(self.status_label)

        self.open_button = Button(
            text="Open in Browser",
            size_hint=(1, 0.2),
            disabled=True
        )
        self.open_button.bind(on_press=self.open_browser)
        layout.add_widget(self.open_button)

        # Start Flask in a separate thread
        self.flask_thread = FlaskThread()
        self.flask_thread.start()

        # Schedule browser open
        Clock.schedule_once(self.server_ready, 3)

        return layout

    def server_ready(self, dt):
        self.status_label.text = "Server Running!\nhttp://127.0.0.1:5000"
        self.open_button.disabled = False
        self.open_browser(None)

    def open_browser(self, instance):
        webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    AgriDashApp().run()
