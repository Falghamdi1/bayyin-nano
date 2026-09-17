# Source of truth for Bayyin's Gradio interface. scripts/sync_notebook_ui.py
# copies this file's content into the Colab notebook's UI cell.
"""Bayyin's Gradio interface. The model is supplied as a callback, never loaded here."""
from html import escape
from inspect import signature
from pathlib import Path
import tempfile


EXAMPLES = [
    ("موعد وتسجيل", "تعلن الجهة المنظمة عن تمديد فترة التسجيل في الفعالية حتى تاريخ ١٥ نوفمبر، على أن يتم سداد الرسوم البالغة ٢٥٠ ريالاً قبل هذا الموعد."),
    ("رسوم وخدمات", "يتعين على المستفيد سداد رسوم الخدمة البالغة ١٢٠ ريالاً خلال ٧ أيام من تاريخ تقديم الطلب، مع الاحتفاظ بإيصال السداد."),
    ("إرشادات زيارة", "يرجى من جميع الزوار الالتزام بالهدوء داخل المبنى، وعدم التصوير إلا بعد الحصول على موافقة الموظف المختص."),
]

DISCLOSURE_TEXT = "هذه صياغة بمساعدة الذكاء الاصطناعي. راجع المعنى والشروط في الإشعار الرسمي قبل الاعتماد عليها."
_DOWNLOAD_DIR = tempfile.TemporaryDirectory(prefix="bayan_downloads_")

# ── Verified color tokens — same values as app.py; see README for the
# contrast math. Duplicated here (not imported) so this file stays
# self-contained enough to paste directly into the Colab notebook.
INK = "#17150F"
SOFT = "#544F44"
PAPER = "#F2EFE8"
PAPER_RAISED = "#FFFFFF"
RULE = "#E1DACB"
ACCENT = "#4F29B7"
OK = "#215C44"
OK_BG = "#E7F0EB"
FLAG = "#8E2025"
FLAG_BG = "#F7E9E9"


def icon(name, size=22):
    paths = {
        "spark": '<path d="m12 3 2.4 6.6L21 12l-6.6 2.4L12 21l-2.4-6.6L3 12l6.6-2.4Z"/>',
        "check": '<path d="m6 12 4 4 8-8"/>',
        "shield": '<path d="m12 3 8 3v6c0 5-8 9-8 9S4 17 4 12V6Z"/><path d="m8.5 12 2.3 2.3 4.7-4.6"/>',
        "alert": '<path d="m12 3 10 18H2Z"/><path d="M12 9v4M12 17h.01"/>',
        "arrow": '<path d="M20 12H4m6-6-6 6 6 6"/>',
    }
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>'


CSS = f"""
:root {{ color-scheme: light !important; }}
body, .gradio-container {{ background: {PAPER} !important; }}
.gradio-container {{ width: 100% !important; max-width: 1100px !important; padding: 0 32px 24px !important; margin: auto !important;
  font-family: 'IBM Plex Sans Arabic', Tahoma, sans-serif !important; color: {INK} !important; }}
#bayan {{ direction: rtl; gap: 0 !important; }}
.gradio-container main {{ width: 100% !important; padding: 0 !important; }}
#bayan .html-container {{ padding: 0 !important; }}
#bayan .html-container, #bayan .prose {{ direction: rtl !important; text-align: right !important; }}
#bayan .brand-mark svg, #bayan .brand-mark path {{ color: #fff !important; stroke: #fff !important; }}
#bayan .block {{ box-shadow: none; }}
#bayan button, #bayan textarea {{ font-family: inherit !important; }}
#bayan button {{ transition: filter .12s ease, box-shadow .12s ease, transform .12s ease; }}
#bayan button:active {{ transform: scale(0.98); }}
#bayan button:focus-visible, #bayan a:focus-visible {{ outline: 3px solid {ACCENT}55 !important; outline-offset: 4px; }}
.bayan-nav {{ display: flex; justify-content: space-between; align-items: center; padding: 16px 0; border-bottom: 1px solid {RULE}; }}
.brand {{ display: flex; gap: 13px; align-items: center; text-decoration: none; color: {INK} !important; }}
.brand-mark {{ display: grid; place-items: center; width: 40px; height: 40px; border-radius: 13px 13px 4px 13px;
  background: {ACCENT}; color: #fff; box-shadow: 0 4px 12px {ACCENT}22; }}
.brand-name {{ font-size: 27px; font-weight: 700; line-height: 1; color: {ACCENT}; }}
.brand-subtitle {{ display: block; font-size: 11px; color: {SOFT}; margin-top: 6px; }}
.nav-links {{ display: flex; align-items: center; gap: 28px; font-size: 13px; }}
.nav-links a {{ text-decoration: none; color: {SOFT}; }}
.nav-links a.active {{ color: {ACCENT}; font-weight: 600; }}
.language-tag {{ border: 1px solid {RULE}; border-radius: 30px; padding: 7px 13px; color: {SOFT}; font-size: 11px; }}
.language-tag b {{ color: {ACCENT}; margin-left: 5px; }}
.hero {{ display: flex; align-items: center; justify-content: space-between; gap: 40px; padding: 38px 0 28px; }}
.eyebrow {{ display: flex; align-items: center; gap: 7px; color: {SOFT}; font-size: 11px; font-weight: 500; margin-bottom: 13px; }}
.eyebrow::before {{ content: ''; width: 6px; height: 6px; border-radius: 50%; background: {ACCENT}; }}
.hero h1 {{ margin: 0 !important; color: {INK}; font-size: clamp(28px, 3.2vw, 41px); line-height: 1.5; font-weight: 600; letter-spacing: -.7px; }}
.hero h1 span {{ color: {ACCENT}; }}
.hero p {{ color: {SOFT}; font-size: 15px; line-height: 1.9; margin: 9px 0 0; max-width: 520px; }}
.hero-note {{ position: relative; min-width: 245px; padding: 22px 24px; background: {ACCENT}0d; border-radius: 18px; transform: rotate(-2deg); }}
.hero-note small {{ display: block; font-size: 10px; letter-spacing: .03em; color: {SOFT}; margin-bottom: 10px; }}
.hero-note .before {{ color: {SOFT}; font-size: 12px; }}
.hero-note .after {{ display: flex; align-items: center; gap: 10px; color: {ACCENT}; font-size: 17px; font-weight: 600; padding-top: 9px; }}
.sample-label {{ display: flex; align-items: center; gap: 9px; padding-bottom: 9px; font-size: 12px; color: {SOFT}; }}
.sample-label strong {{ color: {INK}; font-weight: 500; }}
#example-row {{ gap: 9px !important; margin-bottom: 20px; }}
#example-row button {{ min-width: 0 !important; min-height: 38px; border: 1px solid {RULE}; border-radius: 9px;
  background: {PAPER_RAISED}; color: {SOFT}; font-size: 13px; font-weight: 400; box-shadow: none; }}
#example-row button:hover {{ background: {ACCENT}0d; border-color: {ACCENT}55; }}
#workspace {{ gap: 18px !important; align-items: stretch !important; }}
#source-panel, #result-panel {{ padding: 22px !important; border: 1px solid {RULE}; border-radius: 14px; gap: 14px !important;
  background: {PAPER_RAISED}; min-width: min(100%, 310px) !important; }}
.panel-title {{ display: flex; justify-content: space-between; align-items: center; gap: 10px; }}
.panel-title h2 {{ margin: 0; color: {INK}; font-weight: 600; font-size: 17px; }}
.panel-tag {{ background: {PAPER}; border: 1px solid {RULE}; color: {SOFT}; font-size: 10px; padding: 3px 8px; border-radius: 5px; white-space: nowrap; }}
#source-text, #result-text {{ background: transparent !important; border: 0 !important; padding: 0 !important; }}
#source-text textarea, #result-text textarea {{ box-shadow: none !important; border: 0 !important;
  background: {PAPER}66 !important; color: {INK} !important; font-size: 15px !important; line-height: 2.1 !important;
  padding: 16px !important; border-radius: 10px !important; resize: none; height: 224px !important; min-height: 224px; }}
#source-text textarea::placeholder {{ color: {SOFT}99 !important; font-size: 13px; }}
#source-text textarea:focus {{ outline: 1px solid {ACCENT}77 !important; background: {PAPER_RAISED} !important; }}
.char-counter {{ font-size: 10px; color: {SOFT}; display: flex; align-items: center; justify-content: space-between; }}
.char-counter strong {{ direction: ltr; font-family: Arial, sans-serif; font-size: 11px; font-weight: 400; }}
.char-counter.over {{ color: {FLAG}; }}
#source-actions {{ gap: 8px !important; }}
#simplify-button {{ min-height: 45px; background: {ACCENT} !important; color: #fff !important; border: 1px solid {ACCENT} !important;
  border-radius: 10px; font-size: 13px; font-weight: 500; box-shadow: 0 3px 7px {ACCENT}22; }}
#simplify-button:hover:enabled {{ filter: brightness(0.9); box-shadow: 0 4px 14px {ACCENT}33; }}
#simplify-button:disabled {{ background: {SOFT}99 !important; border-color: {SOFT}99 !important; opacity: .72; }}
#clear-button {{ min-height: 45px; border: 1px solid {RULE}; border-radius: 10px; background: {PAPER_RAISED}; color: {SOFT}; font-size: 12px; }}
.result-empty {{ display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 224px; text-align: center; padding: 15px; }}
.empty-symbol {{ display: grid; place-items: center; width: 55px; height: 55px; background: {ACCENT}0d; color: {ACCENT};
  border: 1px solid {ACCENT}22; border-radius: 16px; margin-bottom: 15px; }}
.result-empty h3 {{ margin: 0 0 7px; color: {INK}; font-size: 14px; font-weight: 500; }}
.result-empty p {{ margin: 0; color: {SOFT}; font-size: 12px; line-height: 1.8; max-width: 290px; }}
.result-empty.loading .empty-symbol svg {{ animation: turn 3s ease-in-out infinite; }}
.result-empty.loading .empty-symbol {{ box-shadow: 0 0 0 7px {ACCENT}11; }}
@keyframes turn {{ 0%, 100% {{ transform: rotate(0); }} 50% {{ transform: rotate(100deg); }} }}
.result-meta {{ display: flex; align-items: center; justify-content: space-between; gap: 10px; min-height: 18px; font-size: 10px; color: {SOFT}; }}
.result-meta b {{ color: {INK}; font-weight: 500; }}
#result-actions {{ gap: 8px !important; }}
#download-result, #copy-result {{ min-height: 45px; border: 1px solid {RULE}; background: {PAPER}; color: {SOFT}; border-radius: 10px; font-size: 12px; font-weight: 400; }}
#download-result:disabled, #copy-result:disabled {{ opacity: .55; }}
.review-card {{ display: flex; align-items: flex-start; gap: 14px; background: {PAPER}; border: 1px solid {RULE};
  border-radius: 12px; padding: 18px 20px; margin-top: 18px; }}
.review-icon {{ flex-shrink: 0; display: grid; place-items: center; color: {SOFT}; padding-top: 2px; }}
.review-card h3 {{ margin: 0 0 5px; color: {INK}; font-size: 13px; font-weight: 600; }}
.review-card p {{ margin: 0; font-size: 12px; color: {SOFT}; line-height: 1.9; }}
.review-card.good {{ background: {OK_BG}; border-color: {OK}33; }}
.review-card.good .review-icon, .review-card.good h3 {{ color: {OK}; }}
.review-card.warn {{ background: {FLAG_BG}; border-color: {FLAG}33; }}
.review-card.warn .review-icon, .review-card.warn h3 {{ color: {FLAG}; }}
.review-card.warn p {{ color: {FLAG}; }}
.review-card.error {{ background: {FLAG_BG}; border-color: {FLAG}33; }}
.review-card.error .review-icon, .review-card.error h3 {{ color: {FLAG}; }}
.review-card.error p {{ color: {FLAG}; }}
.guide {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; padding: 26px 9px 24px; }}
.guide-step h3 {{ margin: 0 0 4px; font-size: 12.5px; color: {INK}; font-weight: 600; }}
.guide-step p {{ margin: 0; font-size: 11.5px; color: {SOFT}; line-height: 1.8; }}
.bayan-footer {{ border-top: 1px solid {RULE}; padding: 17px 0 8px; display: flex; align-items: center; justify-content: space-between; gap: 20px; color: {SOFT}; font-size: 10px; line-height: 1.9; }}
.footer-wordmark {{ font-size: 12px; color: {ACCENT}; white-space: nowrap; }}
.preview-banner {{ background: {FLAG_BG}; color: {FLAG}; padding: 10px 15px; border-radius: 9px; font-size: 11px; line-height: 1.9; margin-top: 15px; }}
footer {{ display: none !important; }}
@media (max-width: 760px) {{
  .gradio-container {{ padding: 0 16px 16px !important; }}
  .bayan-nav {{ padding: 14px 0; }}
  .nav-links {{ gap: 15px; }}
  .language-tag {{ display: none; }}
  .hero {{ padding: 22px 0 20px; }}
  .hero h1 {{ font-size: 30px; }}
  .hero-note {{ display: none; }}
  #workspace {{ flex-direction: column !important; }}
  #source-panel, #result-panel {{ min-width: 0 !important; width: 100% !important; padding: 18px !important; }}
  #example-row {{ flex-wrap: wrap; gap: 6px !important; }}
  #example-row button {{ font-size: 10px; padding: 8px; }}
  .guide {{ grid-template-columns: 1fr; gap: 14px; padding-inline: 0; }}
  .bayan-footer {{ align-items: flex-start; }}
}}
@media (max-width: 420px) {{
  .nav-links {{ font-size: 10px; gap: 13px; }}
  .brand-subtitle {{ font-size: 9px; }}
  .hero h1 {{ font-size: 27px; }}
  .hero p {{ font-size: 12px; }}
}}
@media (prefers-reduced-motion: reduce) {{ #bayan *, #bayan *::before {{ animation: none !important; transition: none !important; }} }}
"""


HEADER = f"""
<header class="bayan-nav">
  <a class="brand" href="#bayan" aria-label="بيّن، الصفحة الرئيسية">
    <span class="brand-mark">{icon('spark', 22)}</span>
    <span><span class="brand-name">بيّن</span><span class="brand-subtitle">مبسّط الإشعارات العربية</span></span>
  </a>
  <nav class="nav-links" aria-label="التنقل"><a href="#workspace" class="active">مساحة التبسيط</a><a href="#guide">كيف يعمل؟</a></nav>
  <span class="language-tag"><b>ع</b> بالعربية، بكل وضوح</span>
</header>
<section class="hero">
  <div><div class="eyebrow">لغة أقرب. قراءة أسهل.</div>
    <h1>إشعار أوضح، <span>بخطوة واحدة.</span></h1>
    <p>حوّل الصياغة الرسمية إلى عربية بسيطة وواضحة.<br>اقرأ بسهولة، وقارن التفاصيل بالنص الأصلي.</p>
  </div>
  <aside class="hero-note" aria-label="مثال توضيحي للصياغة">
    <small>من لغة رسمية إلى معنى قريب</small><div class="before">«يتعيّن على المستفيد سداد الرسوم»</div>
    <div class="after">{icon('arrow', 18)} «يجب عليك دفع الرسوم»</div>
  </aside>
</section>
"""


def empty_html(loading=False):
    title = "جارٍ تبسيط الإشعار…" if loading else "هنا، تصبح الكلمات أوضح."
    subtitle = "لحظات، نجهّز الصياغة لتراجعها مع النص الأصلي." if loading else "أضف نصاً أو اختر أحد الأمثلة، ثم اضغط «بسّط الإشعار»."
    return f'<div class="result-empty {"loading" if loading else ""}" role="status"><div class="empty-symbol">{icon("spark", 26)}</div><h3>{title}</h3><p>{subtitle}</p></div>'


def review_html(kind="idle", detail=None):
    titles = {"idle": "المراجعة جزء من الوضوح.", "loading": "نجهّز الصياغة المبسّطة", "good": "اكتمل الفحص الأولي",
              "neutral": "المعنى يحتاج إلى مراجعتك", "warn": "انتبه لبعض التفاصيل", "error": "تعذّر تبسيط الإشعار"}
    detail = detail or "بعد التبسيط، نفحص الأرقام والتواريخ التي نتعرّف عليها. تبقى مراجعة المعنى والشروط مسؤولية القارئ."
    glyph = "alert" if kind in ("error", "warn") else "shield"
    return f'<section class="review-card {kind}" role="status" aria-live="polite"><div class="review-icon">{icon(glyph)}</div><div><h3>{titles[kind]}</h3><p>{escape(detail)}</p></div></section>'


def counter_html(text, limit):
    count = len(text or "")
    note = "تجاوزت الحد؛ اختصر النص للمتابعة." if count > limit else "فقرة واحدة تكفي للبداية"
    return f'<div class="char-counter {"over" if count > limit else ""}"><span>{note}</span><strong>{count} / {limit}</strong></div>'


def result_meta(original="", simplified=""):
    if not simplified:
        return '<div class="result-meta"><span>صياغة أسهل، مع مراجعتك للتفاصيل</span><span>جاهز للبداية</span></div>'
    return f'<div class="result-meta"><span>كلمات الأصل <b>{len(original.split())}</b> · كلمات الصياغة <b>{len(simplified.split())}</b></span><span>جاهز للمراجعة</span></div>'


def write_download(result, status):
    """Prepare a UTF-8 copy with the original, review notes and disclosure attached."""
    text = (f"بيّن — تبسيط إشعار\n\nالنص الأصلي\n{result['original']}\n\n"
            f"الصياغة المبسّطة\n{result['simplified']}\n\nالفحص الأولي\n{status}\n\n{DISCLOSURE_TEXT}\n")
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8-sig", suffix=".txt", prefix="bayan_",
                                     dir=_DOWNLOAD_DIR.name, delete=False) as handle:
        handle.write(text)
        return handle.name


def launch_demo(demo, **kwargs):
    """Apply Bayyin's styling at the correct API boundary in Gradio 5 or 6."""
    options = {**getattr(demo, "_bayan_launch_options", {}), **kwargs}
    return demo.launch(**options)


def build_demo(simplify_fn, status_fn, max_input_chars=800, *, preview=False):
    """Build the same UI for the notebook, a local model or a labelled fixture preview."""
    import gradio as gr

    theme = gr.themes.Base(
        primary_hue="violet", neutral_hue="stone", radius_size="lg",
        font=[gr.themes.GoogleFont("IBM Plex Sans Arabic"), "Tahoma", "sans-serif"],
    ).set(body_background_fill=PAPER, body_background_fill_dark=PAPER, body_text_color=INK,
          body_text_color_dark=INK, block_background_fill=PAPER_RAISED, block_background_fill_dark=PAPER_RAISED,
          block_border_width="0px", block_shadow="none", button_primary_background_fill=ACCENT,
          button_primary_text_color="#ffffff", input_background_fill=PAPER, input_background_fill_dark=PAPER)

    # Gradio 6 moved theme/css to launch() and removed launch(show_api=...).
    # Inspect the installed API so this also works in an existing Colab runtime.
    if "theme" in signature(gr.Blocks.launch).parameters:
        block_style = {}
        launch_style = {"theme": theme, "css": CSS, "footer_links": []}
    else:
        block_style = {"theme": theme, "css": CSS}
        launch_style = {}

    with gr.Blocks(title="بيّن · إشعار أوضح", **block_style, analytics_enabled=False,
                   fill_width=True, delete_cache=(86400, 86400)) as demo:
        with gr.Column(elem_id="bayan"):
            if preview:
                gr.HTML('<div class="preview-banner">معاينة الواجهة فقط · النتائج أمثلة مكتوبة مسبقاً، ولا يتم تشغيل الموديل. اختر أحد الأمثلة لتجربة الواجهة.</div>')
            gr.HTML(HEADER)
            gr.HTML('<div class="sample-label"><strong>ابدأ بمثال</strong><span>أمثلة توضيحية، وليست إشعارات رسمية</span></div>')
            with gr.Row(elem_id="example-row"):
                example_buttons = [gr.Button(label + "  ↗", min_width=95) for label, _ in EXAMPLES]
            with gr.Row(elem_id="workspace"):
                with gr.Column(scale=1, elem_id="source-panel"):
                    gr.HTML('<div class="panel-title"><h2>النص الأصلي</h2><span class="panel-tag">ابدأ من هنا</span></div>')
                    source = gr.Textbox(label="النص الأصلي", show_label=False, container=False, lines=6, max_lines=12,
                                        rtl=True, text_align="right", elem_id="source-text",
                                        placeholder="ألصق الإشعار الرسمي هنا…\n\nمثلاً: يتعين على المستفيد سداد الرسوم قبل الموعد المحدد.")
                    counter = gr.HTML(counter_html("", max_input_chars), elem_id="char-count")
                    with gr.Row(elem_id="source-actions"):
                        submit = gr.Button("بسّط الإشعار  ←", variant="primary", interactive=False, scale=4, elem_id="simplify-button")
                        clear = gr.Button("مسح النص", scale=1, min_width=85, elem_id="clear-button")
                with gr.Column(scale=1, elem_id="result-panel"):
                    gr.HTML('<div class="panel-title"><h2>الصياغة المبسّطة</h2><span class="panel-tag">لغة أقرب لك</span></div>')
                    blank = gr.HTML(empty_html(), elem_id="empty-result")
                    output = gr.Textbox(label="الصياغة المبسّطة", show_label=False, container=False, lines=6, max_lines=12,
                                        rtl=True, text_align="right", interactive=False,
                                        visible=False, elem_id="result-text")
                    meta = gr.HTML(result_meta(), elem_id="result-meta")
                    with gr.Row(elem_id="result-actions"):
                        copy = gr.Button("نسخ النص", interactive=False, scale=1, min_width=85, elem_id="copy-result")
                        download = gr.DownloadButton("تنزيل النص والمراجعة ↓", interactive=False, scale=2, min_width=120, elem_id="download-result")
            review = gr.HTML(review_html(), elem_id="review-status")
            gr.HTML(f'''<section id="guide" class="guide" aria-label="كيف يعمل بيّن؟">
              <div class="guide-step"><h3>أضف الإشعار</h3><p>فقرة عربية واحدة، بحد أقصى {max_input_chars} حرف.</p></div>
              <div class="guide-step"><h3>بسّط الصياغة</h3><p>كلمات أقرب وجمل أسهل للقراءة.</p></div>
              <div class="guide-step"><h3>راجع التفاصيل</h3><p>قارن الأرقام والمواعيد والشروط بالأصل.</p></div>
            </section><div class="bayan-footer"><span>{DISCLOSURE_TEXT}</span><span class="footer-wordmark">بيّن · لغة أقرب للناس</span></div>''')

        view_outputs = [counter, output, blank, review, download, copy, meta, submit]

        def edit(text):
            valid_length = bool(text and text.strip()) and len(text) <= max_input_chars
            return (counter_html(text, max_input_chars), gr.update(value="", visible=False),
                    gr.update(value=empty_html(), visible=True), review_html(),
                    gr.update(value=None, interactive=False), gr.update(value="نسخ النص", interactive=False),
                    result_meta(), gr.update(interactive=valid_length))

        def fill(text):
            return (text, *edit(text))

        source.input(edit, source, view_outputs, queue=False, show_progress="hidden", trigger_mode="always_last")
        clear.click(lambda: fill(""), outputs=[source, *view_outputs], queue=False, show_progress="hidden")
        for button, (_, example) in zip(example_buttons, EXAMPLES):
            button.click(lambda value=example: fill(value), outputs=[source, *view_outputs], queue=False, show_progress="hidden")
        copy.click(fn=None, inputs=output, outputs=copy, queue=False, js="""async (text) => {
            try { await navigator.clipboard.writeText(text); return 'تم النسخ ✓'; }
            catch { return 'حدد النص للنسخ'; }
        }""")

        controls = [source, clear, *example_buttons]
        submitted_text = gr.State("")

        def begin(text):
            # Lock and snapshot BEFORE the request waits for the shared GPU queue.
            locked = [gr.update(interactive=False) for _ in controls]
            locked[0] = gr.update(value=text, interactive=False)
            return (*locked, gr.update(value="جارٍ التبسيط…", interactive=False),
                   gr.update(value="", visible=False), gr.update(value=empty_html(True), visible=True),
                   review_html("loading", "ستظهر الصياغة هنا عند اكتمالها. بعدها قارن التفاصيل بالنص الأصلي."),
                   gr.update(value=None, interactive=False), gr.update(value="نسخ النص", interactive=False), result_meta(), text)

        def respond(text):
            try:
                result = simplify_fn(text)  # Exactly one pipeline invocation; no second model.
                if result.get("error"):
                    final = (gr.update(value="", visible=False), gr.update(value=empty_html(), visible=True),
                             review_html("error", result["error"]), gr.update(value=None, interactive=False),
                             gr.update(value="نسخ النص", interactive=False), result_meta())
                else:
                    status = status_fn(result)
                    kind = "warn" if not result["gate_passed"] else "good" if result.get("facts_detected") else "neutral"
                    path = write_download(result, status) if result["simplified"].strip() else None
                    final = (gr.update(value=result["simplified"], visible=True), gr.update(visible=False),
                             review_html(kind, status), gr.update(value=path, interactive=bool(path)),
                             gr.update(value="نسخ النص", interactive=bool(result["simplified"].strip())),
                             result_meta(result["original"], result["simplified"]))
            except Exception:
                # Hide implementation errors from the interface; preserve the source for retry.
                final = (gr.update(value="", visible=False), gr.update(value=empty_html(), visible=True),
                         review_html("error", "حدث خطأ أثناء التبسيط. تأكد من تحميل النموذج، ثم أعد المحاولة."),
                         gr.update(value=None, interactive=False), gr.update(value="نسخ النص", interactive=False), result_meta())
            unlocked = [gr.update(interactive=True) for _ in controls]
            unlocked[0] = gr.update(value=text, interactive=True)
            return (*unlocked, gr.update(value="بسّط الإشعار  ←", interactive=bool(text and text.strip()) and len(text) <= max_input_chars), *final)

        response_outputs = [*controls, submit, output, blank, review, download, copy, meta]
        submit.click(begin, source, [*response_outputs, submitted_text], queue=False,
                     trigger_mode="once", show_progress="hidden").then(
            respond, submitted_text, response_outputs, concurrency_limit=1,
            concurrency_id="simplify", show_progress="hidden",
        )
    demo._bayan_launch_options = launch_style
    return demo.queue(default_concurrency_limit=1, max_size=8)
