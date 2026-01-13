from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

from database import init_db
from auth import login
from dashboard import Dashboard


class LoginScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)
        self.app = app

        self.title = Label(text="APPLICATION ÉGLISE", font_size=22)
        self.msg = Label(text="", font_size=14)

        self.church = TextInput(hint_text="ID Église (ex: EGLISE001)", multiline=False)
        self.phone = TextInput(hint_text="Téléphone (ex: 0990000000)", multiline=False)
        self.password = TextInput(hint_text="Mot de passe (ex: 1234)", password=True, multiline=False)

        btn = Button(text="Connexion", size_hint=(1, None), height=50)
        btn.bind(on_press=self.do_login)

        self.add_widget(self.title)
        self.add_widget(self.msg)
        self.add_widget(self.church)
        self.add_widget(self.phone)
        self.add_widget(self.password)
        self.add_widget(btn)

        self.add_widget(Label(
            text="Compte test : EGLISE001 / 0990000000 / 1234",
            font_size=12
        ))

    def do_login(self, instance):
        user = login(self.church.text, self.phone.text, self.password.text)

        if user:
            user_id, role = user
            self.app.root.clear_widgets()
            self.app.root.add_widget(Dashboard(user_id, role))
        else:
            self.msg.text = "❌ Échec : ID Église / téléphone / mot de passe incorrect."


class EgliseApp(App):
    def build(self):
        init_db()
        root = BoxLayout()
        root.add_widget(LoginScreen(self))
        return root


if __name__ == "__main__":
    EgliseApp().run()
