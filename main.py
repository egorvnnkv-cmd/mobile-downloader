import flet as ft
import os
import threading
from yt_dlp import YoutubeDL

def main(page: ft.Page):
    page.title = "Video Downloader"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # Поле ввода
    url_input = ft.TextField(label="Ссылка на видео", width=350)
    status_text = ft.Text(value="Готов к работе", color="white")
    
    def download_video(url):
        # Путь для Android (папка Загрузки)
        path = "/storage/emulated/0/Download"
        if not os.path.exists(path):
            path = "./" 

        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{path}/%(title)s.%(ext)s',
            'nocheckcertificate': True,
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            status_text.value = "Успешно скачано в папку Download!"
            status_text.color = "green"
        except Exception as e:
            status_text.value = f"Ошибка: {str(e)}"
            status_text.color = "red"
        
        page.update()

    def on_click(e):
        if url_input.value:
            status_text.value = "Скачивание началось..."
            status_text.color = "yellow"
            page.update()
            threading.Thread(target=download_video, args=(url_input.value,), daemon=True).start()

    # Добавляем элементы на страницу
    page.add(
        ft.Column(
            [
                ft.Icon(ft.icons.DOWNLOAD_FOR_OFFLINE, size=50, color="blue"),
                url_input,
                ft.ElevatedButton("Скачать", on_click=on_click),
                status_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

ft.app(target=main)
