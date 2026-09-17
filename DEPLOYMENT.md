# Deployment — بيّن · Bayyin

This app is a single self-contained Gradio app (`app.py`). There is no separate
frontend/backend split, no REST API, and no FastAPI server anywhere in this
repo — the UI and the model call live in one process. That shapes everything
below: "deploying the backend" and "deploying the frontend" are the same step.

## Prerequisites

- Python 3.10+
- A Hugging Face account (free) — for the public Space
- A GitHub account — for the source repository
- Git

## 1. Local development

Two terminals are not needed — it's one process.

```bash
pip install -r requirements.txt
python app.py
```

Opens a local Gradio UI at `http://0.0.0.0:7860` (equivalently
`http://localhost:7860`). A CUDA GPU is strongly recommended; Qwen2.5-3B-Instruct
will run on CPU but slowly (expect tens of seconds to minutes per request).

There is no `/health` or `/ready` HTTP endpoint to check separately — Gradio's
own UI loading successfully at that URL *is* the health check for this
architecture. The model itself loads lazily on the **first** submission, not
at startup, so the first request will be slower than the rest — this is
expected, not a bug (see `src/model.py`).

## 2. Public deployment — Hugging Face Space (primary, free, real GPU)

This is the durable public link the QR code should point to.

### Why this instead of Vercel + a remote backend

The handoff for this project assumed a FastAPI backend + a hand-built
frontend calling it over HTTP, deployed separately (backend on a GPU host,
frontend on Vercel). That architecture does not exist in this repo — building
it from scratch would mean writing a new server and a new frontend, not
"deploying" the existing one. Hugging Face Spaces natively hosts a Gradio
app like this one as a single public URL, with no new code required, which
is both truer to "don't rebuild what's already built" and simpler to operate.

### Steps

1. On huggingface.co, create a **new Space**:
   - SDK: **Gradio**
   - Hardware: **ZeroGPU** (free tier — allocates a real GPU on demand per
     request, released afterward; this is what makes free hosting of a 3B
     model actually usable instead of painfully slow on free CPU hardware)
   - Visibility: Public
2. Note the Space's git remote, shown on the Space page, of the form:
   `https://huggingface.co/spaces/<your-username>/<space-name>`
3. From this repo:

   ```bash
   git remote add space https://huggingface.co/spaces/<your-username>/<space-name>
   git push space main
   ```

   (You'll be prompted for your Hugging Face username and an access token —
   generate one at huggingface.co/settings/tokens with **write** scope. Use
   the token as the password, not your account password.)
4. Wait for the Space to finish "Building" (visible on the Space page — this
   **is** the "backend running" status; there is no separate health endpoint
   to poll). First build can take several minutes (dependency install +
   model download on first request).
5. Open the Space URL and submit one of the example notices to confirm real
   inference. **The first submission will be slow** (model load + ZeroGPU
   cold allocation) — this is expected. Subsequent submissions are faster.

### What "free" actually means here

- ZeroGPU quota is shared and rate-limited per account/day. For a classroom
  demo with a handful of people testing over a short window, this is
  comfortably enough; it is not a guarantee of unlimited concurrent use.
- Free Spaces can go to a **sleeping** state after a period with no traffic.
  The next visitor triggers a cold start (tens of seconds to a couple of
  minutes) before the UI responds. Warm it up yourself a few minutes before
  presenting (see `DEMO_RUNBOOK.md`).
- This is genuinely free — no billing setup, no card required, no paid
  hardware tier selected.

## 3. Fallback — Colab + Gradio share link

If the Space is asleep, unreachable, or over its ZeroGPU quota during the
actual presentation:

1. Open `notebooks/arabic_simplifier.ipynb` in Google Colab with a GPU
   runtime (Runtime → Change runtime type → GPU).
2. Run all cells. In the launch cell, set:
   ```python
   LAUNCH_UI = True
   SHARE_UI  = True
   ```
3. This prints a temporary public `https://xxxxx.gradio.live` URL, valid for
   about 72 hours. Update whatever you're showing (slide, printed QR) if you
   have to fall back to this — **do not** reuse the original QR code, since
   it points at the Space, not this temporary URL.

This is explicitly ephemeral: the link dies the moment the Colab runtime
disconnects. Never describe it as the permanent deployment.

## 4. Last resort — static backup page

`deploy/index.html` shows real, previously recorded input/output pairs and
evaluation numbers. It performs **no live inference** — it is a fallback for
if no live path (Space or Colab) is reachable at all.

```bash
cd deploy
npx vercel --prod
```

Never present this as a live demo; it says so on the page itself.

## Environment variables

None are required. There are no API keys, tokens, or secrets in this
project's runtime path — Qwen2.5-3B-Instruct is not a gated model, so no
Hugging Face token is needed to download or run it.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Space stuck "Building" | Dependency install failure | Check the Space's **Logs** tab for the actual pip error |
| First request times out / very slow | Model download + lazy load + ZeroGPU cold start | Expected on first request only; wait, don't resubmit repeatedly |
| `ImportError: No module named 'spaces'` locally | `spaces` only matters on actual Spaces hardware | Harmless locally — `src/model.py` falls back to a no-op decorator when the package is absent |
| Space shows "sleeping" | No recent traffic, free-tier auto-sleep | Visit the URL yourself a few minutes before the demo to wake it |
| Gate flags a correct output as "missing numbers" | Model spelled a number as a word instead of digits, or added/reformatted a number | Documented, known limitation — see README "Limitations" |
| `gradio.live` link stopped working | Colab runtime disconnected or 72h expired | Re-run the notebook cells to get a new link |

## Verifying before presenting

1. Open the Space URL fresh (not from cache).
2. Submit one of the three examples in the UI.
3. Confirm Arabic output appears, and the gate verdict banner shows either
   the green "محفوظة" state or the red "أرقام غير مؤكدة" state — both are
   correct behavior, not a bug.
4. Scan the QR code with a phone on a **different network** than the one
   used to deploy, to rule out local-network-only reachability issues.

## Stopping the backend

- **Space:** nothing to manually stop — it sleeps on its own after
  inactivity, or you can pause it from Space settings.
- **Colab:** disconnect the runtime (Runtime → Disconnect and delete
  runtime), or just close the tab — the `gradio.live` link dies with it.
- **Local:** `Ctrl+C` in the terminal running `python app.py`.
