from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import subprocess
import os

app = FastAPI()

# Pasta onde os vídeos serão salvos
VIDEO_FOLDER = "videos"
os.makedirs(VIDEO_FOLDER, exist_ok=True)

# Modelo para o JSON recebido
class VideoRequest(BaseModel):
    video_id: str

@app.post("/download")
async def download_video(data: VideoRequest, request: Request):  # Pegando a requisição aqui
    video_id = data.video_id
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    output_path = os.path.join(VIDEO_FOLDER, f"{video_id}.mp4")

    try:
        subprocess.run(["yt-dlp", "-f", "best", "-o", output_path, youtube_url], check=True)
        
        # Pegando o domínio automaticamente
        base_url = str(request.base_url)
        video_url = f"{base_url}videos/{video_id}.mp4"

        return {
            "message": "Vídeo baixado com sucesso!",
            "video_url": video_url
        }

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Erro ao baixar o vídeo.")