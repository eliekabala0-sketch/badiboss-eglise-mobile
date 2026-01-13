from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from presence import marquer_presence


class Dashboard(BoxLayout):
    def __init__(self, user_id, role, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)

        self.add_widget(Label(text=f"TABLEAU DE BORD ({role})", font_size=20))

        btn_arrivee = Button(text="Arrivée", size_hint=(1, None), height=50)
        btn_arrivee.bind(on_press=lambda x: marquer_presence(user_id, "Arrivée"))

        btn_depart = Button(text="Départ", size_hint=(1, None), height=50)
        btn_depart.bind(on_press=lambda x: marquer_presence(user_id, "Départ"))

        self.add_widget(btn_arrivee)
        self.add_widget(btn_depart)

        self.add_widget(Label(text="✅ Présence enregistrée dans la base (eglise.db)", font_size=14))
