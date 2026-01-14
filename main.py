import flet as ft
import os
import threading
import sys
import ssl
from yt_dlp import YoutubeDL

# Отключаем проверку SSL для стабильности скачивания
ssl._create_default_https_context = ssl._create_unverified_context

def main(page: ft.Page):
    page.title = "Video Downloader"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "adaptive"

    # Поле ввода ссылки
    url_input = ft.TextField(label="Ссылка на видео (YouTube/VK/etc)", expand=True)
    status_text = ft.Text()
    progress_bar = ft.ProgressBar(width=400, color="blue", visible=False)

    def on_download_click(e):
        if not url_input.value:
            status_text.value = "Введите ссылку!"
            page.update()
            return

        status_text.value = "Начинаю скачивание..."
        progress_bar.visible = True
        page.update()

        # Запускаем в отдельном потоке, чтобы интерфейс не завис
        threading.Thread(target=download_video, args=(url_input.value,), daemon=True).start()

    def download_video(url):
        # Путь к папке загрузок на Android
        download_path = "/storage/emulated/0/Download"
        if not os.path.exists(download_path):
            download_path = os.getcwd() # Если папка недоступна, сохраняем в папку программы

        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{download_path}/%(title)s.%(ext)s',
            'noplaylist': True,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            status_text.value = f"Готово! Файл в папке Download"
        except Exception as ex:
            status_text.value = f"Ошибка: {str(ex)}"
        
        progress_bar.visible = False
        page.update()

    # Интерфейс приложения
    page.add(
        ft.Row([url_input]),
        ft.ElevatedButton("Скачать видео", icon=ft.icons.DOWNLOAD, on_click=on_download_click),
        progress_bar,
        status_text
    )

ft.app(target=main)
