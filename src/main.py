import flet as ft
from tradingview_ta import TA_Handler, Interval
from datetime import datetime
import pytz
import time
import math


def date():
    india_tz = pytz.timezone('Asia/Kolkata')
    return datetime.now(india_tz).strftime('%Y-%m-%d %H:%M:%S')

def percentage_difference(num1, num2):
  if not isinstance(num1, (int, float)) or not isinstance(num2, (int, float)):
    return None

  if num1 == 0 and num2 == 0:
    return 0.0

  try:
    return ((num1 - num2)/num2)*100
  except ZeroDivisionError:
      return float('inf')


def get_close(symbol, exchange="NSE", screener="india"):
    try:
        handler = TA_Handler(
            symbol=symbol,
            exchange=exchange,
            screener=screener,
            interval=Interval.INTERVAL_1_DAY
        )
        data = handler.get_indicators(['description','close','change','volume','RSI','ADX','price_52_week_high','price_52_week_low','EMA50','EMA200'])
        recom = handler.get_analysis().summary["RECOMMENDATION"]
        return [data,recom]
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


def main(page: ft.Page):
    page.title = "stockSence"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    text_field = ft.TextField(label="Enter Stock Symbol", expand=True,autofocus=False, bgcolor="#1E1E1E", color="white")
    dropdown = ft.Dropdown(
        label="Select Direction",
        options=[ft.dropdown.Option("Long"), ft.dropdown.Option("Short")],
        value="Long",
        expand=True,
        bgcolor="#1E1E1E",
        color="white",
    )
    info_box = ft.Text()
    note = ft.TextField(label="Add Note",multiline=True,bgcolor="#1E1E1E", color="white")

    result_column = ft.ListView(spacing =10,auto_scroll =True,expand=True)
    error_message = ft.Text(value="", color="red")

    def save_data(data):
        page.client_storage.set("stocks", data)

    def load_data():
        value = page.client_storage.get("stocks")
        return value if value else []


    def screenupdate(_=None):
        result_column.controls.clear()
        stockList = load_data()

        for listitem in stockList:
            try:
                if len(listitem) < 4:
                    raise IndexError("Incomplete stock data.")

                stock_name = listitem[0][0]
                saved_price = listitem[1]
                saved_date = listitem[2]
                saved_direction = listitem[3]
                current_data = get_close(stock_name) if len(listitem[0]) == 1 else get_close(listitem[0][0], listitem[0][1], listitem[0][2])

                if current_data is None:
                    continue

                current_price = current_data[0]['close']
                day_change = current_data[0]["change"]

                if dropdown.value.lower() == "long":
                    change = percentage_difference(current_price, saved_price)
                elif dropdown.value.lower() == "short":
                    change = percentage_difference(saved_price, current_price)
                else:
                    change = 0

                result_column.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=ft.padding.all(18),
                            border_radius=10,
                            gradient=ft.LinearGradient(
                                colors=[
                                    "#2b2c45","#05050f","#0b0c33","#1920c2"
                                ],
                                tile_mode=ft.GradientTileMode.MIRROR,
                                rotation=math.pi / 3,
                            ),
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(saved_date, weight="bold"),
                                    ft.TextButton(content=ft.Text(stock_name, size=20, weight="bold"),on_click=show_info,data=listitem[0])
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Row([
                                    ft.Text(f"Saved: {saved_price}"),
                                    ft.Text(f"{saved_direction}"),
                                    ft.Text(f"Current: {current_price}")
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Row([
                                    ft.Text(f"Day Change: {day_change:.2f}% | Movement: {change:.2f}%"),
                                    ft.IconButton(icon=ft.Icons.DELETE, on_click=delete_card, data=listitem)
                                ], alignment=ft.MainAxisAlignment.CENTER)
                            ])
                        )
                    )
                )
            except IndexError as e:
                continue
        page.update()


    dlg_show_info = ft.AlertDialog(

        modal=True,
        title=ft.Text("Stock Info"),
        bgcolor="#411661",
        content=ft.Column([ft.Container(
            content=info_box,padding=10,),
        ],horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        actions=[
            ft.TextButton("OK", on_click=lambda e: page.close(dlg_show_info)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,

    )



    def show_info(e):
        symbol= e.control.data
        data = get_close(symbol[0]) if len(symbol)==1 else get_close(symbol[0],symbol[1],symbol[2])
        stocksList = load_data()
        index = next((i for i,item in enumerate(stocksList) if item[0] == symbol),-1)

        description = data[0]["description"]
        close = data[0]["close"]
        change = data[0]["change"]
        rsi = data[0]["RSI"]
        adx = data[0]["ADX"]
        ema50 = data[0]["EMA50"]
        ema200 = data[0]["EMA200"]
        price_52_week_high = data[0]["price_52_week_high"]
        price_52_week_low = data[0]["price_52_week_low"]
        recom = data[1]
        stocknote = stocksList[index][4]

        info_box.value = (f"{description} \nprice:  {close:.2f}({change:.2f}%) \nRsi:  {rsi:.2f} \nAdx:  {adx:.2f} \nema200:   {ema200:.2f}({percentage_difference(close,ema200):.2f}%) \nema50:   {ema50:.2f}({percentage_difference(close,ema50):.2f}%)  \n52weekhigh:  {price_52_week_high:.2f}({percentage_difference(close,price_52_week_high):.2f}%) \n52weeklow:  {price_52_week_low:.2f}({percentage_difference(close,price_52_week_low):.2f}%) \nadvice:  {recom}\nnote: {stocknote}").upper()
        page.open(dlg_show_info)



    def delete_card(e):
        card_to_del = e.control.data
        data = load_data()
        if card_to_del in data:
            data.remove(card_to_del)
            save_data(data)
            screenupdate()

    def add_stock(e):
        error_message.value = ""
        note.value = ""
        stock = [item.strip().upper() for item in text_field.value.split("/")]
        stocks_data = load_data()
        if not stock or not stock[0]:
            error_message.value = "Please enter a valid stock symbol."
            text_field.value = ""
            page.update()
            return
        if any(stock[0] == item[0][0] for item in stocks_data):
            error_message.value = "Stock already exists in the list."
            text_field.value = ""
            page.update()
            return
        try:


            data = get_close(stock[0]) if len(stock) == 1 else get_close(stock[0], stock[1], stock[2])

            if data is None:
                error_message.value = "Could not retrieve stock data. Please check the symbol and try again."
                text_field.value = ''
                page.update()
                return
            description = data[0]["description"]
            close = data[0]["close"]
            change = data[0]["change"]
            rsi = data[0]["RSI"]
            adx = data[0]["ADX"]
            ema50 = data[0]["EMA50"]
            ema200 = data[0]["EMA200"]
            price_52_week_high = data[0]["price_52_week_high"]
            price_52_week_low = data[0]["price_52_week_low"]
            recom = data[1]


            info_box.value = (f"{description} \nprice:  {close:.2f}({change:.2f}%) \nRsi:  {rsi:.2f} \nAdx:  {adx:.2f} \nema200:   {ema200:.2f}({percentage_difference(close,ema200):.2f}%) \nema50:   {ema50:.2f}({percentage_difference(close,ema50):.2f}%)  \n52weekhigh:  {price_52_week_high:.2f}({percentage_difference(close,price_52_week_high):.2f}%) \n52weeklow:  {price_52_week_low:.2f}({percentage_difference(close,price_52_week_low):.2f}%) \nadvice:  {recom}").upper()
            page.open(dlg_add_data)


        except Exception as er:
            error_message.value = f"An error occurred: {er}"
            page.update()

    def add_card(e):
        page.close(dlg_add_data)
        if e.control.text == "Add":
            stocks_data = load_data()
            stock = [item.strip().upper() for item in text_field.value.split("/")]
            data = get_close(stock[0]) if len(stock) == 1 else get_close(stock[0], stock[1], stock[2])
            direction = dropdown.value
            stocknote = note.value
            stocks_data.insert(0,[stock, data[0]['close'], date(), direction,stocknote])
            save_data(stocks_data)
            text_field.value = ""
            screenupdate()
        text_field.value = ""
        entry_box.visible = False
        search_box.visible = True
        page.update()



    dlg_add_data = ft.AlertDialog(

        modal=True,
        title=ft.Text("Stock Info"),
        bgcolor="#411661",
        content=ft.Column([ft.Container(
            content=info_box,padding=10,),
            note,
            dropdown,
        ],horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        actions=[
            ft.TextButton("Add", on_click=add_card),
            ft.TextButton("Cancel", on_click=add_card),
        ],
        actions_alignment=ft.MainAxisAlignment.END,

    )


    def updatefunc():
        while True:
            screenupdate()
            time.sleep(60)


    def clear_data(e):
        page.close(dlg_clear_data)
        if e.control.text == "Yes":
            page.client_storage.clear()
            screenupdate()


    dlg_clear_data = ft.AlertDialog(
        modal=True,
        title=ft.Text("Please confirm"),
        content=ft.Text("Do you really want to delete all those?"),
        actions=[
            ft.TextButton("Yes", on_click=clear_data),
            ft.TextButton("No", on_click=clear_data),
        ],
        actions_alignment=ft.MainAxisAlignment.END,

    )

    def scarch_click(e):
        search_box.visible = False
        entry_box.visible = True
        page.update()

    def back_click(e):
        entry_box.visible = False
        search_box.visible = True
        page.update()



    button = ft.ElevatedButton("Enter", on_click=add_stock, bgcolor="#6200EE", color="white")
    search_box = ft.Row([
        ft.IconButton(icon=ft.Icons.SEARCH,on_click=scarch_click, icon_color="white"),
        ft.PopupMenuButton(items=[
            ft.PopupMenuItem(content=ft.Row([
                ft.Icon(ft.Icons.CLEAR),
                ft.Text("Clear")]),on_click=lambda e: page.open(dlg_clear_data)),
        ])
    ],visible=True,alignment=ft.MainAxisAlignment.END)
    entry_box = ft.Row([ft.IconButton(icon=ft.Icons.KEYBOARD_BACKSPACE,on_click=back_click),text_field,button],visible=False)


    page.add(ft.Container(
        expand=True,
        padding=ft.padding.only(top=15),
        gradient=ft.LinearGradient(
                colors=[
                   "#1f202e","#141636"
                ],
                tile_mode=ft.GradientTileMode.MIRROR,
                rotation=math.pi / 3,
            ),
        content=ft.Column([
            error_message,
            search_box,
            entry_box,
            result_column
            ], expand=True)
    ))

    page.run_task(updatefunc())


ft.app(target=main)
