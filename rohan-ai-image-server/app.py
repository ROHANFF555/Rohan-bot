import os
import secrets
import threading
from contextlib import asynccontextmanager
from pathlib import Path

import torch
from diffusers import StableDiffusionPipeline
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

MODEL_ID = os.getenv("MODEL_ID", "stable-diffusion-v1-5/stable-diffusion-v1-5")
API_KEY = os.getenv("API_KEY", "")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
pipe = None
generation_lock = threading.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipe
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    print(f"Loading {MODEL_ID} on {device}")
    pipe = StableDiffusionPipeline.from_pretrained(MODEL_ID, torch_dtype=dtype)
    pipe = pipe.to(device)
    if device == "cuda":
        pipe.enable_attention_slicing()
    print("ROHAN AI ready")
    yield
    pipe = None


app = FastAPI(title="ROHAN AI Image Server", version="0.1.0", lifespan=lifespan)


def verify_key(key: str | None):
    if not API_KEY:
        raise HTTPException(status_code=503, detail="Set API_KEY in .env first.")
    if not key or not secrets.compare_digest(key, API_KEY):
        raise HTTPException(status_code=401, detail="Invalid API key")


class ImageRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=1000)
    negative_prompt: str = Field(default="", max_length=1000)
    width: int = Field(default=512, ge=256, le=768)
    height: int = Field(default=512, ge=256, le=768)
    steps: int = Field(default=25, ge=10, le=40)
    seed: int | None = Field(default=None, ge=0, le=4294967295)


@app.get("/health")
def health():
    return {"app": "ROHAN AI", "model_loaded": pipe is not None,
            "gpu_available": torch.cuda.is_available()}


@app.get("/", response_class=HTMLResponse)
def home():
    return """<!doctype html><html lang="bn"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ROHAN AI</title><style>
body{font-family:Arial;max-width:760px;margin:30px auto;padding:18px;background:#101114;color:#f5f5f5}
input,textarea,button,select{box-sizing:border-box;width:100%;padding:12px;margin:7px 0;border-radius:8px}
input,textarea,select{background:#202127;color:white;border:1px solid #555}
button{background:white;color:#111;font-weight:bold}img{max-width:100%;border-radius:12px}
</style><h1>ROHAN AI</h1><p>বর্ণনা লিখে AI ছবি তৈরি করো।</p>
<input id="key" type="password" placeholder="API key">
<textarea id="prompt" rows="4" placeholder="A beautiful house beside a lake at sunrise"></textarea>
<select id="size"><option value="512">512 × 512</option><option value="768">768 × 768</option></select>
<button id="go" onclick="generate()">ছবি তৈরি করো</button><p id="status" role="status"></p>
<img id="result" hidden alt="Generated image"><script>
async function generate(){
const b=document.getElementById('go'),s=document.getElementById('status');
const key=document.getElementById('key').value,prompt=document.getElementById('prompt').value.trim();
const size=Number(document.getElementById('size').value);
if(!key||prompt.length<3){s.textContent='API key ও বর্ণনা দাও।';return}
b.disabled=true;s.textContent='ছবি তৈরি হচ্ছে...';
try{const r=await fetch('/generate',{method:'POST',headers:{'Content-Type':'application/json','X-API-Key':key},
body:JSON.stringify({prompt,width:size,height:size,steps:25})});const d=await r.json();
if(!r.ok)throw Error(d.detail||'Request failed');
const img=document.getElementById('result');img.src=d.image_url+'?key='+encodeURIComponent(key);img.hidden=false;
s.textContent='ছবি তৈরি হয়েছে।';
}catch(e){s.textContent='সমস্যা: '+e.message}finally{b.disabled=false}}
</script></html>"""


@app.post("/generate")
def generate(req: ImageRequest, x_api_key: str | None = Header(default=None)):
    verify_key(x_api_key)
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model is loading")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    generator = torch.Generator(device=device).manual_seed(req.seed) if req.seed is not None else None
    try:
        with generation_lock, torch.inference_mode():
            image = pipe(
                prompt=req.prompt,
                negative_prompt=req.negative_prompt or None,
                width=req.width, height=req.height,
                num_inference_steps=req.steps, generator=generator,
            ).images[0]
            filename = f"image_{secrets.token_hex(8)}.png"
            image.save(OUTPUT_DIR / filename)
        return {"ok": True, "filename": filename, "image_url": f"/images/{filename}", "seed": req.seed}
    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        raise HTTPException(status_code=507, detail="GPU memory insufficient; try 512x512.")


@app.get("/images/{filename}")
def get_image(filename: str, x_api_key: str | None = Header(default=None)):
    verify_key(x_api_key)
    if Path(filename).name != filename or not filename.endswith(".png"):
        raise HTTPException(status_code=400, detail="Invalid filename")
    path = OUTPUT_DIR / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path, media_type="image/png")
