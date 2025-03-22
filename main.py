from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess
import os

app = FastAPI()

# ✅ Verifica se a variável de ambiente COOKIES_DATA existe e cria o arquivo cookies.txt
if "COOKIES_DATA" in os.environ:
    with open("cookies.txt", "w") as file:
        file.write(os.environ["COOKIES_DATA"])
    print("✅ Arquivo 'cookies.txt' foi criado a partir da variável do Railway.")

    # ✅ Verifica se o arquivo foi realmente criado e contém dados válidos
    if os.path.exists("cookies.txt"):
        with open("cookies.txt", "r") as file:
            cookies_content = file.read()
            if len(cookies_content.strip()) > 0:
                print("✅ O arquivo 'cookies.txt' foi criado e contém dados válidos.")
            else:
                print("❌ O arquivo 'cookies.txt' foi criado, mas está VAZIO.")
    else:
        print("❌ O arquivo 'cookies.txt' não foi criado corretamente.")
else:
    print("❌ Variável 'COOKIES_DATA' não encontrada no Railway.")

# Pasta para armazenar os vídeos baixados
VIDEO_FOLDER = "videos"
os.makedirs(VIDEO_FOLDER, exist_ok=True)

# Tornar os vídeos acessíveis via /videos/
app.mount("/videos", StaticFiles(directory=VIDEO_FOLDER), name="videos")

class VideoRequest(BaseModel):
    video_id: str
    is_short: bool = False  # Indica se é um YouTube Short
    use_cookies: bool = True

@app.post("/download")
async def download_video(data: VideoRequest, request: Request):
    video_id = data.video_id
    is_short = data.is_short
    use_cookies = data.use_cookies

    # Determina o URL correto para Shorts ou vídeos normais
    if is_short:
        youtube_url = f"https://www.youtube.com/shorts/{video_id}"
    else:
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    
    output_path = os.path.join(VIDEO_FOLDER, f"{video_id}.mp4")
    
    try:
        # Monta o comando yt-dlp
        command = ["yt-dlp", "-o", output_path, youtube_url]
        
        # ✅ Adiciona o arquivo de cookies se solicitado
        if use_cookies and os.path.exists("cookies.txt"):
            command.extend(["--cookies", "cookies.txt"])
            print("✅ Comando configurado para usar 'cookies.txt'.")

        # Executa o comando yt-dlp
        result = subprocess.run(command, capture_output=True, text=True)
        
        # Se ocorrer um erro no download
        if result.returncode != 0:
            print(f"❌ Erro ao baixar o vídeo: {result.stderr}")
            return {"success": False, "message": "Erro ao baixar o vídeo.", "error": result.stderr}

        # Verifica se o vídeo foi realmente salvo
        if not os.path.exists(output_path):
            return {"success": False, "message": "O vídeo não foi salvo corretamente."}

        # Envia o vídeo como resposta para download automático
        with open(output_path, "rb") as file:
            video_content = file.read()
            headers = {
                "Content-Disposition": f"attachment; filename={video_id}.mp4"
            }
            return Response(content=video_content, media_type="video/mp4", headers=headers)
        
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return {"success": False, "message": "Erro inesperado ao processar o vídeo.", "error": str(e)}