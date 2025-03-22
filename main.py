from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess
import os
import time

app = FastAPI()

# Pasta onde os vídeos serão salvos
VIDEO_FOLDER = "videos"
os.makedirs(VIDEO_FOLDER, exist_ok=True)

# Tornar os vídeos disponíveis para download
app.mount("/videos", StaticFiles(directory=VIDEO_FOLDER), name="videos")

class VideoRequest(BaseModel):
    video_id: str
    use_cookies: bool = True  # Permitir que o usuário escolha se quer usar cookies ou não

def download_video_file(youtube_url: str, output_path: str, use_cookies: bool) -> tuple:
    """
    Faz o download do vídeo usando yt-dlp.
    Retorna uma tupla (success, message).
    """
    # Comando base
    command = ["yt-dlp", "-o", output_path, youtube_url]

    # Adiciona cookies.txt se for necessário
    if use_cookies:
        command.extend(["--cookies", "cookies.txt"])

    # Tenta fazer o download e captura o resultado
    try:
        start_time = time.time()  # Marca o início do download
        result = subprocess.run(command, capture_output=True, text=True)
        end_time = time.time()  # Marca o fim do download

        # Loga o tempo de download
        download_time = round(end_time - start_time, 2)
        print(f"📥 Download finalizado em {download_time} segundos.")

        if result.returncode != 0:
            # Erro durante o download
            return (False, f"❌ Erro ao baixar o vídeo: {result.stderr}")

        # Se o vídeo foi baixado com sucesso
        if os.path.exists(output_path):
            return (True, f"✅ Vídeo baixado com sucesso: {output_path}")

        # Caso o vídeo não tenha sido salvo mesmo após sucesso no yt-dlp
        return (False, "❌ O vídeo não foi salvo corretamente.")
    
    except Exception as e:
        # Captura qualquer erro inesperado
        return (False, f"❌ Erro inesperado: {str(e)}")

@app.post("/download")
async def download_video(data: VideoRequest, request: Request):
    video_id = data.video_id
    use_cookies = data.use_cookies

    # Cria o URL do vídeo
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    output_path = os.path.join(VIDEO_FOLDER, f"{video_id}.mp4")

    # Inicia o download do vídeo
    success, message = download_video_file(youtube_url, output_path, use_cookies)

    if not success:
        # Se houve erro, retorna o problema encontrado
        print(message)
        return {"success": False, "message": "Erro ao baixar o vídeo.", "error": message}
    
    # Se o vídeo foi baixado com sucesso, monta a URL para acesso
    base_url = str(request.base_url)
    video_url = f"{base_url}videos/{video_id}.mp4"

    print(f"✅ URL do vídeo disponível: {video_url}")
    return {"success": True, "message": "Vídeo baixado com sucesso!", "video_url": video_url}