from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import yfinance as yf


class StockPriceApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        self.input = TextInput(hint_text="Enter Stock Symbol (e.g., AAPL)", size_hint=(1, 0.2))
        layout.add_widget(self.input)

        self.button = Button(text="Get Latest Price", size_hint=(1, 0.2))
        self.button.bind(on_press=self.get_stock_price)
        layout.add_widget(self.button)

        self.result = Label(text="Stock Price will appear here", size_hint=(1, 0.6))
        layout.add_widget(self.result)

        return layout

    def get_stock_price(self, instance):
        symbol = self.input.text.strip().upper()
        try:
            stock = yf.Ticker(symbol)
            price = stock.history(period="1d")['Close'].iloc[-1]
            self.result.text = f"{symbol} Latest Price: ${price:.2f}"
        except:
            self.result.text = "Error: Invalid Stock Symbol or Network Issue"


if __name__ == "__main__":
    StockPriceApp().run()
