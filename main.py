from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess
import os

app = FastAPI()

# Pasta para armazenar os vídeos baixados
VIDEO_FOLDER = "videos"
os.makedirs(VIDEO_FOLDER, exist_ok=True)

# Tornar os vídeos acessíveis via /videos/
app.mount("/videos", StaticFiles(directory=VIDEO_FOLDER), name="videos")

# Modelo para o JSON de entrada
class VideoRequest(BaseModel):
    video_id: str

@app.post("/download")
async def download_video(data: VideoRequest, request: Request):
    video_id = data.video_id
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    output_path = os.path.join(VIDEO_FOLDER, f"{video_id}.mp4")

    try:
        # Comando para baixar o vídeo
        result = subprocess.run(
            ["yt-dlp", "-f", "best", "-o", output_path, youtube_url],
            capture_output=True,
            text=True
        )
        
        # Se yt-dlp falhar
        if result.returncode != 0:
            error_message = result.stderr
            print(f"Erro ao baixar o vídeo: {error_message}")
            return {
                "success": False,
                "message": "Não foi possível baixar o vídeo.",
                "error": error_message
            }

        # Se o download for bem-sucedido
        base_url = str(request.base_url)
        video_url = f"{base_url}videos/{video_id}.mp4"
        return {
            "success": True,
            "message": "Vídeo baixado com sucesso!",
            "video_url": video_url
        }

    except Exception as e:
        # Qualquer outro erro inesperado
        print(f"Erro inesperado: {e}")
        return {
            "success": False,
            "message": "Erro inesperado ao processar o vídeo.",
            "error": str(e)
        }