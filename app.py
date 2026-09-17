"""
Bayyin · بيّن — application entry point

Run with:  python app.py
Requires a CUDA GPU for reasonable generation speed (CPU works, slowly).

The interface itself lives in ui.py (shared with the Colab notebook, which
embeds the same file inline so it works without cloning this repo). This
file only wires ui.py to the real model pipeline and launches it.
"""

import os

from src.pipeline import simplify_and_validate
from src.prompts import MAX_INPUT_CHARS
from ui import build_demo, launch_demo


def status_text(result: dict) -> str:
    if not result["gate_passed"]:
        missing = "، ".join(result["missing_numbers"])
        return f"أرقام غير مؤكدة: {missing} — راجع النص يدوياً."
    if not result["facts_detected"]:
        return "لا توجد أرقام أو تواريخ يتعرف عليها الفحص. راجع المعنى والشروط يدوياً."
    note = "الأرقام والتواريخ محفوظة."
    if result["truncated"]:
        note += " قد يكون الرد غير مكتمل."
    return note


demo = build_demo(simplify_and_validate, status_text, MAX_INPUT_CHARS)

if __name__ == "__main__":
    # 0.0.0.0 + $PORT so this also runs correctly on a remote host, not just
    # localhost; Hugging Face Spaces sets its own PORT and ignores these
    # defaults when they don't apply.
    launch_demo(demo, server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
