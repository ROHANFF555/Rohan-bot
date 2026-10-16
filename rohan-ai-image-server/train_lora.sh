#!/usr/bin/env bash
set -euo pipefail

# Run from this directory on a Linux machine with an NVIDIA GPU.
# The script downloads the Diffusers training example and its dependencies.
MODEL_ID="${MODEL_ID:-stable-diffusion-v1-5/stable-diffusion-v1-5}"
DATA_DIR="${DATA_DIR:-dataset}"
OUTPUT_DIR="${TRAIN_OUTPUT_DIR:-lora-output}"
STEPS="${TRAIN_STEPS:-500}"

if [[ ! -f "$DATA_DIR/metadata.jsonl" ]]; then
  echo "Missing $DATA_DIR/metadata.jsonl. See README_BN.md for format."
  exit 1
fi

python prepare_data.py
python -m pip install --upgrade diffusers transformers accelerate datasets torchvision peft

if [[ ! -d diffusers-src ]]; then
  git clone --depth 1 https://github.com/huggingface/diffusers.git diffusers-src
fi

accelerate launch diffusers-src/examples/text_to_image/train_text_to_image_lora.py \
  --pretrained_model_name_or_path "$MODEL_ID" \
  --train_data_dir "$DATA_DIR" \
  --image_column image \
  --caption_column text \
  --resolution 512 \
  --center_crop \
  --random_flip \
  --train_batch_size 1 \
  --gradient_accumulation_steps 4 \
  --gradient_checkpointing \
  --learning_rate 1e-4 \
  --lr_scheduler constant \
  --lr_warmup_steps 0 \
  --max_train_steps "$STEPS" \
  --checkpointing_steps 100 \
  --output_dir "$OUTPUT_DIR" \
  --report_to none

echo "Training finished. Check $OUTPUT_DIR and the training logs."
