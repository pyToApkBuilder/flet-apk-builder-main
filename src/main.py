import flet as ft
import yfinance as yf


def main(page: ft.Page):
    page.title= "stock viewer"
    page.vertical_alignment= ft.MainAxisAlignment.CENTER
    page.horizontal_alignment=ft.CrossAxisAlignment.CENTER
    def getprice(e):
        try:
            sym = str(st_in.value.strip().upper())
            ress.value = sym
            try:
                data = yf.Ticker(sym).history(period="1y")
                inf= yf.Ticker(sym).info

                ress.value= f"{inf["longName"]} : {data.iloc[-1].Close:.2f}"
                st_in.value=""
            except Exception as er:
                ress.value = f"{sym}: {er}"

        except Exception as er:
            ress.value=f"inputerror{er}"
        page.update()

    st_in = ft.TextField(label="enter stock sympol")
    btn= ft.ElevatedButton(text="Fetch", on_click=getprice)
    ress = ft.Text("stock prive: N/A")

    page.add(ft.Column([st_in,btn,ress],horizontal_alignment=ft.CrossAxisAlignment.CENTER))


ft.app(main)
