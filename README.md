---
title: Bayyin
emoji: 📝
colorFrom: purple
colorTo: gray
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
short_description: يبسّط الإشعارات العربية الرسمية بنموذج ذكاء اصطناعي، مع فحص آلي للأرقام والتواريخ
---

# Bayyin · بيّن
### Arabic Notice Simplifier — "بيّن" means made clear

A GenAI application that rewrites formal Arabic notices in plain Arabic — one model call, verified by a deterministic code gate before anything is shown.

Built for the Tuwaiq Academy Generative AI Application Engineering Bootcamp, Day 9–10.

> بيّن — "he made it clear." The name is the function.

## Problem

Official Arabic notices (government, tourism, municipal) are written formally and are hard for many readers to act on correctly.

## User

A tourist or new resident trying to understand a Saudi government or tourism-authority notice.

## Solution

| Step | What happens |
|---|---|
| Input | one formal Arabic paragraph |
| Model call | the LLM rewrites it in plain Arabic — one call, no chain |
| Gate | deterministic code check: every number/date in the original must appear in the output |
| Output | the simplified text, or a rejection with a stated reason |

No second model call is used for verification. The gate is code, not a judge — matching the brief's "can one model call do it?" constraint.

## Models

| Model | Role | Status |
|---|---|---|
| `Qwen/Qwen2.5-3B-Instruct` | primary — used in both evaluation runs | confirmed working, FP16 |
| `humain-ai/ALLaM-7B-Instruct-preview` | Arabic-specialized comparison candidate | integrated with revision pinning + tokenizer SHA256 verification, 4-bit NF4 — **load not yet confirmed live** |

**Honest note on the comparison:** the two evaluation runs in this repo (`s1`, `s2`) both generated with Qwen2.5-3B-Instruct — an earlier attempt to load ALLaM used an incorrect repository ID and silently fell back to Qwen. What `s1` vs `s2` actually compares is **two different system prompts on the same model**, not two model sizes. The corrected ALLaM integration lives in `arabic_simplifier.ipynb` and has not yet been run end to end.

## Results (human-judged, `s2`, n=10)

| Metric | Result |
|---|---|
| Meaning preserved | 10/10 |
| Judged simpler | 10/10 |
| Code gate passed (numbers/dates kept) | 6/10 |

**The gap between 10/10 human judgment and 6/10 gate pass is the most interesting finding in this project**, not a bug to hide. It means the deterministic gate is stricter than human judgment on this test set — worth investigating whether that's the gate catching real risk or over-flagging on formatting.

## Limitations

- Evaluation set is 10 invented notices — not representative of all formal Arabic
- The gate's number-preservation check is regex-based; a number spelled as a word could pass undetected — mitigated in the latest prompt version by an explicit "never spell numbers as words" rule, not eliminated
- `s1`'s human evaluation was not completed
- ALLaM comparison is code-complete but unexecuted as of this commit

## Color accessibility (app.py)

Every text/background pair in the interface is WCAG AA verified before use:

| Pair | Contrast ratio |
|---|---|
| Tuwaiq purple (#4F29B7) on white | 9.0:1 |
| Body ink on paper background | 15.9:1 |
| Secondary text on paper background | 7.1:1 |
| Success green on white | 7.8:1 |
| Error red on white | 8.8:1 |

All comfortably clear the 4.5:1 minimum for body text.

## Responsible AI

- All test data is invented — no real personal data
- Every output carries a disclosure that it was AI-generated and should be checked against the original
- This tool is informational only; it does not act on anyone's behalf

## Running it

**As a script (Qwen, recommended for a live demo):**

```bash
git clone <this-repo>
cd bayyin
pip install -r requirements.txt
python app.py
```

Opens a local Gradio interface. A CUDA GPU is strongly recommended; it will run on CPU but slowly. No Hugging Face login needed — Qwen2.5-3B-Instruct is not gated.

**As a notebook (ALLaM comparison, Colab):**

Open `notebooks/arabic_simplifier.ipynb` in Google Colab with a GPU runtime. Run cells top to bottom.

## Repository structure

```
bayyin/
├── app.py                — run this: python app.py
├── src/
│   ├── model.py           — Qwen/Qwen2.5-3B-Instruct, lazy-loaded once
│   ├── prompts.py         — the one system prompt, injection-resistant
│   ├── gate.py            — the deterministic code gate, with self-tests
│   └── pipeline.py        — wires the three into one function
├── notebooks/
│   ├── arabic_simplifier_s1.ipynb   — Qwen, plain-assistant prompt
│   ├── arabic_simplifier_s2.ipynb   — Qwen, evaluated (10/10 · 10/10 · 6/10)
│   └── arabic_simplifier.ipynb      — Colab version: model-agnostic, ALLaM + Qwen, integrity-checked
├── data/
│   └── test_notices.json  — the 10 evaluation notices
├── deploy/
│   └── index.html         — static results showcase (Vercel-ready, no live inference)
├── requirements.txt
└── .gitignore
```

**Why two versions exist.** `app.py` is the clean, GitHub-runnable version — locked to Qwen2.5-3B-Instruct, the model both evaluations actually used, with a redesigned interface. `notebooks/arabic_simplifier.ipynb` is the Colab version with the ALLaM comparison — kept separate because that model's live load is not yet confirmed. Don't let anyone present `app.py` as including the ALLaM comparison; it doesn't.

## Team

| Member | Role |
|---|---|
| Faisal Alghamdi | — |
| _fill in_ | — |
| _fill in_ | — |
| _fill in_ | — |

## Deployment

**Primary — Hugging Face Space.** `app.py` (this repo's Gradio app) is deployed as a Hugging Face Space using **ZeroGPU** hardware — free, real on-demand GPU inference, no separate backend or frontend to build or maintain. The Space URL is the one durable public link; the QR code points there. See [DEPLOYMENT.md](DEPLOYMENT.md) for the exact steps and [DEMO_RUNBOOK.md](DEMO_RUNBOOK.md) for the presentation checklist.

**Fallback — Colab + Gradio share link.** `arabic_simplifier.ipynb` can still launch its own temporary public `gradio.live` link (~72h) as a live backup if the Space is asleep or unreachable:

```python
LAUNCH_UI = True
SHARE_UI  = True
```

**Last resort — `deploy/index.html`.** A static results page with recorded numbers, for if no live path is reachable at all. It performs no inference. Deploy with `npx vercel --prod` from `deploy/` if wanted. Never presented as live inference.
