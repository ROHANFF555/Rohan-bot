# ROHAN AI Image Server (Starter)

বাংলা নির্দেশনা: এটি একটি প্রাথমিক text-to-image API, যা আগে থেকে প্রশিক্ষিত Diffusers-compatible মডেল ব্যবহার করে। এটি নিজে থেকে নতুন মডেল শূন্য থেকে ট্রেন করে না।

## প্রয়োজন
- Docker + Docker Compose
- NVIDIA GPU server recommended; compatible NVIDIA driver ও NVIDIA Container Toolkit
- প্রথমবার মডেল ডাউনলোডের জন্য internet এবং পর্যাপ্ত disk space
- মডেলটির লাইসেন্স ও ব্যবহার-শর্ত যাচাই

## চালানো
1. এই ফোল্ডারে `.env.example` কপি করে `.env` বানাও।
2. `.env`-এ দীর্ঘ random API key বসাও।
3. Linux GPU server-এ চালাও:

```bash
docker compose up --build -d
docker compose logs -f
```

4. সার্ভারের ভেতর থেকে `http://localhost:8000` খোলো।
5. API docs: `http://localhost:8000/docs`

প্রথমবার model weights ডাউনলোড হবে। CPU-তে চললে খুব ধীর হতে পারে।

## API
`POST /generate` — Header: `X-API-Key: <your key>`

```json
{
  "prompt": "A cinematic photo of a small modern library at sunrise",
  "negative_prompt": "blurry, low quality",
  "width": 512,
  "height": 512,
  "steps": 25,
  "seed": 1234
}
```

`GET /images/<filename>`-এ একই `X-API-Key` header লাগবে।

## ঐচ্ছিক LoRA fine-tuning
- `dataset/metadata.jsonl` এবং ছবিগুলো এই ফোল্ডারের `dataset/`-এ রাখো।
- প্রতিটি JSONL লাইনে `{"file_name":"image1.jpg","text":"ছবির ইংরেজি বর্ণনা"}` ফরম্যাট ব্যবহার করো; ছবির ফাইলটি `dataset/` ফোল্ডারে থাকতে হবে।
- Linux + NVIDIA GPU-তে training dependencies ইনস্টল করে চালাও: `bash train_lora.sh`
- Training scriptটি starter; এটি এখানে চালিয়ে যাচাই করা হয়নি। Diffusers-এর নতুন সংস্করণে argument বদলাতে পারে।

## নিরাপত্তা ও সীমাবদ্ধতা
- এই starter-টি production-ready নয়। Public internet-এ প্রকাশের আগে HTTPS, authentication, rate limiting, logging, queueing এবং safety controls যোগ করতে হবে।
- API key না সেট করলে generation বন্ধ থাকবে।
- মডেল weights ZIP বা Git repository-তে রাখা নেই; runtime-এ download হবে।
- Training data বা pretrained model-এর অধিকার/লাইসেন্স আলাদাভাবে যাচাই করতে হবে।
- এই repository-তে training script আছে বলে পূর্ণ training সম্পন্ন হয়েছে এমন নয়।
