"""
Bayyin · بيّن — application entry point

Run with:  python app.py
Requires a CUDA GPU for reasonable generation speed (CPU works, slowly).

UI design notes (why it's built this way, not just what it does):
- Every color pair below is WCAG AA verified (>= 4.5:1 for text) before use,
  not chosen by eye. See the contrast check in the project README.
- One primary action per screen: "بسّط" is the only filled/primary button.
- The gate's pass/fail state is never conveyed by color alone — each state
  also carries text and an icon-equivalent symbol, for colorblind users and
  for anyone reading a black-and-white printout of a screenshot.
- Loading state is Gradio's native default (a spinner over the output
  region during generation) rather than a custom implementation — fewer
  moving parts, same result, nothing to get wrong under time pressure.
"""

import os

import gradio as gr

from src.pipeline import simplify_and_validate
from src.prompts import MAX_INPUT_CHARS

# ── Verified color tokens — see README for the contrast math ──────────────
INK = "#17150F"
SOFT = "#544F44"
PAPER = "#F2EFE8"
ACCENT = "#4F29B7"      # Tuwaiq Academy's own purple — ties the app to the bootcamp
OK = "#215C44"
OK_BG = "#E7F0EB"
FLAG = "#8E2025"
FLAG_BG = "#F7E9E9"

CUSTOM_CSS = f"""
.gradio-container {{ background: {PAPER} !important; font-family: 'IBM Plex Sans Arabic', 'Noto Naskh Arabic', Tahoma, sans-serif; }}
#title {{ color: {ACCENT}; font-weight: 700; }}
#tagline {{ color: {SOFT}; font-size: 15px; }}
.verdict-ok {{ background: {OK_BG}; color: {OK}; border-inline-start: 4px solid {OK}; border-radius: 0 8px 8px 0; padding: 12px 16px; font-size: 14.5px; }}
.verdict-bad {{ background: {FLAG_BG}; color: {FLAG}; border-inline-start: 4px solid {FLAG}; border-radius: 0 8px 8px 0; padding: 12px 16px; font-size: 14.5px; }}
.disclosure {{ color: {SOFT}; font-size: 12.5px; margin-top: 6px; }}
button.primary {{ background: {ACCENT} !important; border-color: {ACCENT} !important; min-height: 44px; }}
"""

EXAMPLES = [
    "تعلن الهيئة العامة للسياحة عن تمديد فترة التسجيل في مهرجان الرياض الموسمي حتى تاريخ 15 نوفمبر، على أن يتم استيفاء الرسوم البالغة 250 ريالاً قبل هذا الموعد.",
    "وفقاً للائحة المرورية الجديدة، تُفرض غرامة قدرها 500 ريال على عدم ربط حزام الأمان، وتُضاعف الغرامة في حال التكرار خلال 90 يوماً.",
    "يجب على جميع المقيمين تحديث بيانات الإقامة خلال 60 يوماً من تاريخ التجديد، وإلا تُطبق غرامة قدرها 300 ريال عن كل شهر تأخير.",
]


def run(original: str):
    result = simplify_and_validate(original)

    if result.get("error"):
        verdict = f'<div class="verdict-bad">⚠ {result["error"]}</div>'
        return "", verdict, ""

    if result["gate_passed"]:
        verdict = '<div class="verdict-ok">✓ الأرقام والتواريخ محفوظة</div>'
    else:
        missing = "، ".join(result["missing_numbers"])
        verdict = f'<div class="verdict-bad">⚠ أرقام غير مؤكدة: {missing} — راجع النص يدوياً</div>'

    meta = (
        f'<div class="disclosure">{result["disclosure"]}<br>'
        f'{result["input_tokens"]} رمز دخول · {result["output_tokens"]} رمز خرج'
        f'{" · لم يكتمل الرد" if result["truncated"] else ""}</div>'
    )

    return result["simplified"], verdict, meta


def char_count(text: str) -> str:
    n = len(text or "")
    over = n > MAX_INPUT_CHARS
    color = FLAG if over else SOFT
    return f'<span style="color:{color};font-size:12px">{n} / {MAX_INPUT_CHARS} حرف</span>'


with gr.Blocks(css=CUSTOM_CSS, title="بيّن · Bayyin") as demo:
    gr.Markdown("# بيّن · Bayyin", elem_id="title")
    gr.Markdown(
        "يبسّط الإشعارات العربية الرسمية — نفس الحقائق، جمل أقصر.",
        elem_id="tagline",
    )

    with gr.Accordion("كيف يعمل", open=False):
        gr.Markdown(
            "إدخال ← تحقق ← بناء الطلب ← **استدعاء واحد للموديل** ← "
            "فحص بالكود (الأرقام والتواريخ محفوظة؟) ← عرض النتيجة.\n\n"
            "الفحص كود، مو استدعاء ثانٍ للموديل — بحسب متطلبات المشروع."
        )

    original_in = gr.Textbox(
        label="النص الأصلي",
        placeholder="الصق الإشعار الرسمي هنا...",
        lines=6,
        max_lines=10,
        rtl=True,
    )
    count_label = gr.HTML(char_count(""))
    original_in.change(char_count, original_in, count_label)

    gr.Examples(examples=EXAMPLES, inputs=original_in, label="أمثلة")

    submit_btn = gr.Button("بسّط", variant="primary")

    simplified_out = gr.Textbox(
        label="النص المبسّط",
        lines=6,
        max_lines=10,
        rtl=True,
        show_copy_button=True,
        interactive=False,
    )
    verdict_out = gr.HTML()
    meta_out = gr.HTML()

    submit_btn.click(run, inputs=original_in, outputs=[simplified_out, verdict_out, meta_out])
    original_in.submit(run, inputs=original_in, outputs=[simplified_out, verdict_out, meta_out])


if __name__ == "__main__":
    # 0.0.0.0 + $PORT so this also runs correctly on a remote host, not just
    # localhost; Hugging Face Spaces sets its own PORT and ignores these
    # defaults when they don't apply.
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
