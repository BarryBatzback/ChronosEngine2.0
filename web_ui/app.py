"""
Веб-интерфейс для Chronos Engine
FastAPI + Three.js
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os
import uuid

app = FastAPI(title="Chronos Engine API", description="AI 3D Model Generator")

# Создаём папки для статики
os.makedirs("static", exist_ok=True)
os.makedirs("output", exist_ok=True)

# Монтируем статику
app.mount("/static", StaticFiles(directory="static"), name="static")


class TextTo3DRequest(BaseModel):
    prompt: str
    style: Optional[str] = "realistic"
    polycount: Optional[int] = 10000


class ImageTo3DRequest(BaseModel):
    image_url: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def index():
    """Главная страница"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chronos Engine - AI 3D Model Generator</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 {
                text-align: center;
                font-size: 3em;
                margin-bottom: 0.5em;
            }
            .subtitle {
                text-align: center;
                color: #888;
                margin-bottom: 2em;
            }
            .input-section {
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
            }
            textarea {
                width: 100%;
                padding: 15px;
                font-size: 16px;
                border-radius: 10px;
                border: none;
                background: rgba(255,255,255,0.2);
                color: white;
                resize: vertical;
            }
            button {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 12px 30px;
                font-size: 16px;
                border-radius: 25px;
                cursor: pointer;
                margin-top: 15px;
                transition: transform 0.2s;
            }
            button:hover {
                transform: scale(1.05);
            }
            #status {
                margin-top: 20px;
                padding: 10px;
                border-radius: 10px;
                display: none;
            }
            #viewer {
                width: 100%;
                height: 500px;
                background: #111;
                border-radius: 10px;
                display: none;
            }
            .examples {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-top: 20px;
            }
            .example-btn {
                background: #333;
                padding: 8px 16px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
            }
            .example-btn:hover {
                background: #555;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 Chronos Engine</h1>
            <div class="subtitle">AI-Powered 3D Model Generator</div>

            <div class="input-section">
                <textarea id="prompt" rows="3" placeholder="Describe your 3D model...&#10;&#10;Example: 'a wooden table with realistic texture'"></textarea>

                <div class="examples">
                    <div class="example-btn" onclick="setPrompt('a wooden table with realistic texture')">Wooden Table</div>
                    <div class="example-btn" onclick="setPrompt('a fantasy sword with ornate handle')">Fantasy Sword</div>
                    <div class="example-btn" onclick="setPrompt('a low-poly tree with green leaves')">Low-poly Tree</div>
                    <div class="example-btn" onclick="setPrompt('a sci-fi spaceship')">Sci-fi Spaceship</div>
                </div>

                <button onclick="generateModel()">🚀 Generate 3D Model</button>

                <div id="status"></div>
            </div>

            <div id="viewer"></div>
        </div>

        <script>
            async function setPrompt(text) {
                document.getElementById('prompt').value = text;
            }

            async function generateModel() {
                const prompt = document.getElementById('prompt').value;
                if (!prompt) {
                    alert('Please enter a description');
                    return;
                }

                const statusDiv = document.getElementById('status');
                const viewerDiv = document.getElementById('viewer');

                statusDiv.style.display = 'block';
                statusDiv.innerHTML = '⏳ Generating 3D model... This may take a minute.';
                statusDiv.style.background = '#ff9800';

                try {
                    const response = await fetch('/api/text-to-3d', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ prompt: prompt })
                    });

                    const data = await response.json();

                    if (data.success) {
                        statusDiv.innerHTML = '✅ Model generated successfully!';
                        statusDiv.style.background = '#4CAF50';

                        // Показываем модель в Three.js
                        showModel(data.model_url);
                    } else {
                        statusDiv.innerHTML = '❌ Error: ' + data.message;
                        statusDiv.style.background = '#f44336';
                    }
                } catch (error) {
                    statusDiv.innerHTML = '❌ Error: ' + error.message;
                    statusDiv.style.background = '#f44336';
                }
            }

            async function showModel(modelUrl) {
                const viewerDiv = document.getElementById('viewer');
                viewerDiv.style.display = 'block';

                // Импортируем Three.js
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
                document.head.appendChild(script);

                script.onload = () => {
                    // Загружаем GLTFLoader
                    const loaderScript = document.createElement('script');
                    loaderScript.src = 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js';
                    document.head.appendChild(loaderScript);

                    loaderScript.onload = () => {
                        const scene = new THREE.Scene();
                        scene.background = new THREE.Color(0x111111);

                        const camera = new THREE.PerspectiveCamera(45, viewerDiv.clientWidth / viewerDiv.clientHeight, 0.1, 1000);
                        camera.position.set(3, 2, 5);
                        camera.lookAt(0, 0, 0);

                        const renderer = new THREE.WebGLRenderer({ antialias: true });
                        renderer.setSize(viewerDiv.clientWidth, viewerDiv.clientHeight);
                        viewerDiv.innerHTML = '';
                        viewerDiv.appendChild(renderer.domElement);

                        // Lights
                        const ambientLight = new THREE.AmbientLight(0x404040);
                        scene.add(ambientLight);
                        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
                        directionalLight.position.set(1, 2, 1);
                        scene.add(directionalLight);

                        const loader = new THREE.GLTFLoader();
                        loader.load(modelUrl, (gltf) => {
                            scene.add(gltf.scene);
                            animate();
                        });

                        function animate() {
                            requestAnimationFrame(animate);
                            renderer.render(scene, camera);
                        }
                    };
                };
            }
        </script>
    </body>
    </html>
    """


@app.post("/api/text-to-3d")
async def text_to_3d(request: TextTo3DRequest):
    """API эндпоинт для генерации 3D модели из текста"""
    import subprocess
    import json

    model_id = str(uuid.uuid4())
    output_path = f"output/{model_id}.glb"

    # Вызываем оркестратор
    result = subprocess.run([
        "python", "main.py",
        "--prompt", request.prompt,
        "--output", output_path,
        "--api-mode"
    ], capture_output=True, text=True)

    if result.returncode == 0:
        return {
            "success": True,
            "model_url": f"/static/{model_id}.glb",
            "model_id": model_id
        }
    else:
        return {
            "success": False,
            "message": result.stderr
        }


@app.post("/api/image-to-3d")
async def image_to_3d(file: UploadFile = File(...)):
    """API эндпоинт для генерации 3D модели из изображения"""
    # Сохраняем изображение
    image_path = f"static/{uuid.uuid4()}.png"
    with open(image_path, "wb") as f:
        f.write(await file.read())

    # Генерируем модель
    import subprocess
    model_id = str(uuid.uuid4())
    output_path = f"output/{model_id}.glb"

    result = subprocess.run([
        "python", "main.py",
        "--image", image_path,
        "--output", output_path,
        "--api-mode"
    ], capture_output=True, text=True)

    if result.returncode == 0:
        return {
            "success": True,
            "model_url": f"/static/{model_id}.glb",
            "model_id": model_id
        }
    else:
        return {
            "success": False,
            "message": result.stderr
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)