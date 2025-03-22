import flet as ft
from tradingview_ta import TA_Handler, Interval

def get_close(symbol, exchange="NSE", screener="india"):
    try:
        handler = TA_Handler(
           symbol=symbol,
           exchange=exchange,
           screener=screener,
           interval=Interval.INTERVAL_1_DAY
           )
        return handler.get_analysis().indicators["close"]
    except Exception as e:
        return e

def main(page: ft.Page):
    page.title= "stock viewer"
    page.vertical_alignment= ft.MainAxisAlignment.CENTER
    page.horizontal_alignment=ft.CrossAxisAlignment.CENTER
    def getprice(e):
        try:
            sym = str(st_in.value.strip().upper())
            ress.value = sym
            try:
                close = get_close(sym)
                ress.value = close
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
