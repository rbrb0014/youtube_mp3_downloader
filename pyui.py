import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from yt_dlp import YoutubeDL


class YouTubeMP3Downloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube MP3 다운로더")

        # 기본 다운로드 폴더 설정 (Windows 기준)
        self.default_download_path = os.path.join(os.path.expanduser("~"), "Downloads")

        # Tkinter 변수들
        self.path_var = tk.StringVar(value=self.default_download_path)
        self.link_var = tk.StringVar()
        self.title_var = tk.StringVar()

        # UI 구성
        self.create_widgets()

    def create_widgets(self):
        """UI 요소를 생성합니다."""
        # 저장 경로 라벨, 엔트리, 찾아보기 버튼
        tk.Label(self.root, text="저장 경로:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        tk.Entry(self.root, textvariable=self.path_var, width=50).grid(
            row=0, column=1, padx=5, pady=5
        )
        tk.Button(self.root, text="찾아보기", command=self.browse_folder).grid(
            row=0, column=2, padx=5, pady=5
        )

        # 유튜브 링크 라벨, 엔트리
        tk.Label(self.root, text="유튜브 링크:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        tk.Entry(self.root, textvariable=self.link_var, width=50).grid(
            row=1, column=1, padx=5, pady=5, columnspan=2
        )

        # 파일 제목 라벨, 엔트리
        tk.Label(self.root, text="저장할 제목(선택):").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        tk.Entry(self.root, textvariable=self.title_var, width=50).grid(
            row=2, column=1, padx=5, pady=5, columnspan=2
        )

        # 진행 상황 라벨
        self.progress_label = tk.Label(self.root, text="진행 상황: 대기 중", fg="blue")
        self.progress_label.grid(row=3, column=0, columnspan=3, pady=5)

        # 다운로드 버튼
        tk.Button(
            self.root,
            text="다운로드",
            command=self.download_mp3,
            width=15,
            bg="#4CAF50",
            fg="white",
        ).grid(row=4, column=0, columnspan=3, pady=10)

    def get_ffmpeg_path(self):
        """ffmpeg.exe의 경로를 반환합니다."""
        if getattr(sys, "frozen", False):  # PyInstaller로 빌드된 경우
            return os.path.join(sys._MEIPASS, "ffmpeg.exe")
        return "ffmpeg.exe"  # 개발 환경에서는 현재 디렉토리의 ffmpeg.exe 사용

    def browse_folder(self):
        """사용자가 폴더를 선택해 path_var 변수에 저장합니다."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.path_var.set(folder_selected)

    def progress_hook(self, d):
        """다운로드 진행 상황을 업데이트합니다."""
        if d["status"] == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes", 0) or d.get("total_bytes_estimate", 0)
            if total > 0:
                percent = downloaded / total * 100
                self.progress_label.config(text=f"진행 중: {percent:.2f}%")
            else:
                self.progress_label.config(text="진행 중: 계산 중...")

            self.root.update()  # UI 강제 업데이트
        elif d["status"] == "finished":
            self.progress_label.config(text="다운로드 완료!")

    def download_mp3(self):
        """유튜브 링크로부터 .mp3 파일을 다운로드합니다."""
        link = self.link_var.get().strip()
        save_path = self.path_var.get().strip()
        custom_title = self.title_var.get().strip()

        if not link:
            messagebox.showerror("오류", "유튜브 영상 링크를 입력해주세요.")
            return

        if not save_path:
            messagebox.showerror("오류", "저장할 경로를 지정해주세요.")
            return

        # yt-dlp 옵션 설정
        ydl_opts = {
            "format": "bestaudio/best",  # 최상의 오디오 품질로 다운로드
            "outtmpl": os.path.join(
                save_path, "%(title)s.%(ext)s"
            ),  # 저장 경로 및 파일명 템플릿
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",  # 오디오 추출
                    "preferredcodec": "mp3",  # MP3로 변환
                    "preferredquality": "192",  # MP3 품질 (192kbps)
                }
            ],
            "ffmpeg_location": self.get_ffmpeg_path(),  # ffmpeg 경로 설정
            "progress_hooks": [self.progress_hook],  # 진행 상황 업데이트를 위한 훅
        }

        try:
            # yt-dlp를 사용하여 다운로드
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(
                    link, download=True
                )  # 정보 추출 및 다운로드
                original_title = info_dict.get(
                    "title", "Unknown Title"
                )  # 원본 제목 가져오기

            # 사용자 지정 제목이 있으면 파일명 변경
            if custom_title:
                original_file = os.path.join(save_path, f"{original_title}.mp3")
                new_file = os.path.join(save_path, f"{custom_title}.mp3")
                os.rename(original_file, new_file)

            messagebox.showinfo("완료", f"다운로드 및 변환 성공:\n{save_path}")
        except Exception as e:
            messagebox.showerror("오류", f"오류가 발생했습니다: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeMP3Downloader(root)
    root.mainloop()
