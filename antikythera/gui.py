from kivy.app import App

from kivy.uix.button import Button

class MetricDisplay(App):
    def build(self):
        return Button(text="Find a Stingray!",
                      background_color=(1, 0.125, 0.321, 1),
                      background_normal='',
                      font_size=100)

if __name__ == "__main__":
    MetricDisplay().run()
