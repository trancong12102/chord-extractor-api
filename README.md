# chord-extractor-api

HTTP API trích xuất chord từ file audio. Client upload audio lên S3, gửi presigned URL cho API; API tải về, chạy chord-extractor (Chordino Vamp plugin), trả về `{ duration, chords: [{chord, timestamp}] }`.

## Stack

- Python 3.11 (constraint từ `chord-extractor 0.1.3`, không thể lên 3.12+)
- FastAPI + uvicorn
- [`chord-extractor`](https://github.com/ohollo/chord-extractor) (wrap Chordino + NNLS Chroma Vamp plugin)
- pixi (deps), Docker (deploy)

## API

### `GET /health`
```json
{ "status": "ok" }
```

### `POST /extract`
Body:
```json
{ "url": "https://bucket.s3.amazonaws.com/audio.mp3?X-Amz-..." }
```

Response 200:
```json
{
  "duration": 217.34,
  "chords": [
    { "chord": "N", "timestamp": 0.0 },
    { "chord": "C", "timestamp": 0.74 },
    { "chord": "G", "timestamp": 4.21 }
  ]
}
```

Định dạng audio hỗ trợ: `mp3`, `wav`, `ogg`, `flac`, `m4a`, `webm`. Giới hạn 100MB/file.

Error codes:
- `413` — file > 100MB
- `415` — định dạng không hỗ trợ
- `422` — URL không hợp lệ
- `502` — không tải được URL
- `500` — extraction thất bại

## Local dev

### Khuyến nghị: chạy qua Docker

`chord-extractor` chỉ ship pre-compiled Chordino binary cho **Linux 64-bit**. Trên macOS sẽ thiếu plugin trừ khi cài thủ công, nên cách dễ nhất là dùng container:

```bash
docker build -t chord-extractor-api .
docker run --rm -p 8000:8000 chord-extractor-api
curl http://localhost:8000/health
```

### Chạy native qua pixi (Linux hoặc macOS có cài Vamp plugin)

```bash
pixi install
pixi run dev          # uvicorn --reload, port 8000
```

Trên macOS, để `chord-extractor` tìm thấy Chordino, cần cài plugin pack thủ công vào `~/Library/Audio/Plug-Ins/Vamp/`:

1. Tải Chordino + NNLS Chroma từ https://code.soundsoftware.ac.uk/projects/nnls-chroma/files
2. Copy `.dylib` vào `~/Library/Audio/Plug-Ins/Vamp/`
3. Verify: chạy `pixi run python -c "import vamp; print(vamp.list_plugins())"` — phải thấy `nnls-chroma:chordino`

Nếu lib chưa được cài, request `POST /extract` sẽ trả 500 với log message lỗi Vamp.

## Test

```bash
pixi run -e dev test           # pytest
pixi run -e dev lint           # ruff check
```

## Deploy

Build image và đẩy lên registry/PaaS bất kỳ (Fly.io, Railway, AWS ECS...). Image chạy uvicorn trên port `8000`. Đặt sau API gateway hoặc reverse proxy để xử lý auth + rate limiting.

## Notes

- Extraction là CPU-bound, ~30-60s cho bài 4 phút. Nếu cần xử lý đồng thời nhiều request, scale horizontally hoặc chuyển sang job queue (Celery/Hatchet).
- API không yêu cầu AWS auth; URL phải là presigned hoặc public HTTP.
- Chord notation theo Chordino: `N` = no chord/silence, các chord dạng `C`, `Am`, `G7`, `Dm7`, `F#`, `Bb`...
