import json
from pathlib import Path
from PIL import Image

DATASET = Path("dataset")
METADATA = DATASET / "metadata.jsonl"
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def main():
    if not METADATA.is_file():
        raise SystemExit("Missing dataset/metadata.jsonl")
    valid, errors = 0, []
    for line_no, line in enumerate(METADATA.read_text(encoding="utf-8").splitlines(), 1):
        try:
            row = json.loads(line)
            filename, caption = row["file_name"], row["text"]
            if Path(filename).name != filename:
                raise ValueError("file_name must be a filename only")
            path = DATASET / filename
            if path.suffix.lower() not in EXTENSIONS or not path.is_file():
                raise ValueError(f"Missing/unsupported image: {filename}")
            if not isinstance(caption, str) or len(caption.strip()) < 3:
                raise ValueError("Caption too short")
            with Image.open(path) as image:
                image.verify()
            valid += 1
        except Exception as exc:
            errors.append(f"Line {line_no}: {exc}")
    print(f"Valid images: {valid}; errors: {len(errors)}")
    for error in errors:
        print(error)
    if errors:
        raise SystemExit("Fix dataset errors before training.")
    if valid < 10:
        print("Warning: very small dataset; fine-tuning results may be poor.")


if __name__ == "__main__":
    main()
