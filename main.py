import flet as ft
import os
import threading
import sys
import ssl
from yt_dlp import YoutubeDL
from moviepy import VideoFileClip

# Исправление SSL для скачивания
ssl._create_default_https_context = ssl._create_unverified_context

def main(page: ft.Page):
    page.title = "Video Downloader"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "adaptive"

    # ОПРЕДЕЛЕНИЕ ПУТЕЙ ДЛЯ ANDROID
    # На телефоне сохраняем в системную папку документов или загрузок
    if page.platform == ft.PagePlatform.ANDROID:
        save_dir = "/storage/emulated/0/Download" # Папка загрузок
        # Если нет прав доступа, используем внутреннюю папку приложения
        if not os.access(save_dir, os.W_OK):
            save_dir = page.get_upload_dir()
    else:
        save_dir = os.getcwd()

    url_input = ft.TextField(label="Вставьте ссылку сюда", width=400)
    status_text = ft.Text("", weight="bold")
    progress_ring = ft.ProgressRing(visible=False)
    file_list = ft.Column(spacing=15)

    def refresh_files():
        file_list.controls.clear()
        try:
            files = [f for f in os.listdir(save_dir) if f.endswith(".mp4") and not f.startswith("temp_")]
            if not files:
                file_list.controls.append(ft.Text("Список пуст", color="grey"))
            else:
                for file in files:
                    file_list.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(file, size=14, weight="bold"),
                                ft.Row([
                                    ft.ElevatedButton("УДАЛИТЬ", bgcolor="red", color="white",
                                                      on_click=lambda e, f=file: delete_file(f), expand=True),
                                ])
                            ]), bgcolor="#2c2c2c", padding=15, border_radius=10
                        )
                    )
        except: pass
        page.update()

    def delete_file(name):
        try:
            os.remove(os.path.join(save_dir, name))
            refresh_files()
        except: pass

    def process_video(e):
        url = url_input.value
        if not url: return
        status_text.value = "Загрузка..."
        progress_ring.visible = True
        page.update()

        def run_logic():
            temp_name = os.path.join(save_dir, "temp_download.mp4")
            try:
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'outtmpl': temp_name,
                    'noplaylist': True,
                    'nocheckcertificate': True,
                    'quiet': True,
                }
                # На Android ffmpeg обычно уже прописан в системе
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                seg = int(cut_options.value)
                if seg > 0:
                    status_text.value = "Нарезка..."
                    page.update()
                    clip = VideoFileClip(temp_name)
                    start, part = 0, 1
                    while start < clip.duration:
                        end = min(start + seg, clip.duration)
                        new_part = clip.subclip(start, end)
                        out_p = os.path.join(save_dir, f"part_{part}.mp4")
                        new_part.write_videofile(out_p, codec="libx264", audio_codec="aac", logger=None)
                        start, part = end, part + 1
                    clip.close()
                    os.remove(temp_name)
                else:
                    final_name = os.path.join(save_dir, "video.mp4")
                    os.rename(temp_name, final_name)
                status_text.value = "Готово! Проверьте папку Загрузки"
            except Exception as ex:
                status_text.value = f"Ошибка: {str(ex)}"
            finally:
                progress_ring.visible = False
                refresh_files()
                page.update()

        threading.Thread(target=run_logic, daemon=True).start()

    cut_options = ft.RadioGroup(content=ft.Row([
        ft.Radio(value="0", label="Нет"),
        ft.Radio(value="60", label="1 мин"),
        ft.Radio(value="120", label="2 мин"),
    ], alignment="center"))
    cut_options.value = "0"

    page.add(ft.Column([
        ft.Text("DOWNLOADER MOBILE", size=25, weight="bold", color="blue"),
        url_input, cut_options,
        ft.ElevatedButton("ЗАПУСТИТЬ", width=300, on_click=process_video),
        progress_ring, status_text, ft.Divider(), file_list
    ], horizontal_alignment="center"))
    refresh_files()

ft.app(target=main)