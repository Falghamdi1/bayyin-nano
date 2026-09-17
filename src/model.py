"""
Bayyin · بيّن — model loading

Locked to Qwen/Qwen2.5-3B-Instruct. This is the model both evaluation runs
(s1, s2) actually generated with, and the only one of the two candidates
confirmed working end to end — an earlier attempt to load ALLaM used an
incorrect repository ID and silently fell back to this model anyway.
ALLaM integration exists separately (see notebooks/arabic_simplifier.ipynb)
and is not part of this script until its own load is confirmed live.

The model loads once, lazily, on first request — not at import time — so
that importing this module for tests or tooling doesn't require a GPU.
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    # Only present on Hugging Face Spaces (ZeroGPU hardware). Attaches a real
    # GPU to this process for the duration of the decorated call, then
    # releases it — this is what makes free ZeroGPU hardware work at all.
    import spaces
    gpu_decorator = spaces.GPU(duration=60)
except ImportError:
    def gpu_decorator(func):
        return func

MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"

_tokenizer = None
_model = None


def load_model():
    global _tokenizer, _model
    if _model is not None:
        return _tokenizer, _model

    has_gpu = torch.cuda.is_available()
    _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    _model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16 if has_gpu else torch.float32,
        device_map="auto" if has_gpu else None,
    )
    _model.eval()

    n_params = sum(p.numel() for p in _model.parameters())
    device = "GPU" if has_gpu else "CPU"
    print(f"Loaded {MODEL_NAME} — {n_params:,} parameters on {device}.")
    if not has_gpu:
        print("No GPU detected — generation will be slow. That is expected, not a bug.")

    return _tokenizer, _model


@gpu_decorator
def ask(messages: list, max_new_tokens: int = 250) -> dict:
    tokenizer, model = load_model()

    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.3,
            top_p=0.9,
            do_sample=True,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.eos_token_id,
        )

    n_in = inputs["input_ids"].shape[1]
    n_out = output.shape[1] - n_in
    reply = tokenizer.decode(output[0][n_in:], skip_special_tokens=True).strip()

    return {
        "reply": reply,
        "input_tokens": n_in,
        "output_tokens": n_out,
        "truncated": n_out >= max_new_tokens,
    }
