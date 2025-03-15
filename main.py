from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess
import os

app = FastAPI()

# Pasta onde os vídeos serão salvos
VIDEO_FOLDER = "videos"
os.makedirs(VIDEO_FOLDER, exist_ok=True)  # Garante que a pasta exista

# ✅ Modelo do JSON esperado
class VideoRequest(BaseModel):
    video_id: str

# ✅ Endpoint que recebe o JSON corretamente
@app.post("/download")
async def download_video(data: VideoRequest):  # Agora FastAPI entende o corpo JSON
    video_id = data.video_id

    if not video_id:
        raise HTTPException(status_code=400, detail="video_id é obrigatório")

    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    output_path = os.path.join(VIDEO_FOLDER, f"{video_id}.mp4")

    try:
        subprocess.run(["yt-dlp", "-f", "best", "-o", output_path, youtube_url], check=True)
        video_url = f"http://127.0.0.1:8000/videos/{video_id}.mp4"
        return {"video_url": video_url, "video_id": video_id}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao baixar o vídeo: {e}")

# ✅ Servir os vídeos via HTTP
app.mount("/videos", StaticFiles(directory=VIDEO_FOLDER), name="videos")