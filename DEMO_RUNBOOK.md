# Demo Runbook — بيّن · Bayyin

## Before the demo (do this ~15–20 minutes ahead)

- [ ] Open the Hugging Face Space URL yourself, from your own phone or
      laptop, to wake it if it's sleeping (free-tier Spaces sleep after
      inactivity — first visit after sleeping is a slow cold start).
- [ ] Submit one of the three built-in examples and confirm you get real
      Arabic output back, not an error.
- [ ] Note whether the gate verdict was green (numbers preserved) or red
      (flagged) — either is fine to show; know which one you got so you're
      not surprised live.
- [ ] Have the QR code ready (printed or on a slide) — it should point at
      the Space URL, not a Colab or Vercel link.
- [ ] Have a backup screenshot of a successful run, in case you need to show
      *something* while troubleshooting live.
- [ ] Know the fallback path cold: Colab notebook open in a tab, ready to
      run, in case the Space is unreachable (see `DEPLOYMENT.md` §3).

## During the demo

1. State the problem in one sentence: formal Arabic notices are hard for
   many readers — tourists, new residents — to act on correctly.
2. Submit one clear example live (use one of the three built-in examples if
   you want a guaranteed-good result, or a fresh notice if you're
   confident).
3. Show the simplified output next to the original.
4. Point out the verdict banner and explain what it means: a deterministic
   code check, not a second model call, confirms every number and date from
   the original still appears in the simplified text.
5. Name the architecture in one line: one model call (Qwen2.5-3B-Instruct),
   then a regex-based code gate — no second LLM call for verification.
6. Mention limitations honestly if asked or if time allows:
   - The gate is regex-based; a number spelled as a word instead of digits
     would slip past it (mitigated by an explicit prompt rule, not
     eliminated).
   - Evaluation results (10/10 meaning preserved, 10/10 judged simpler,
     6/10 gate pass, n=10) come from an invented 10-notice test set, not
     real-world traffic.
   - The 10/10 vs 6/10 gap is a genuine finding — the gate is stricter than
     human judgment — not a bug being hidden.
7. Invite peers to scan the QR code and try their own notice on their own
   phones.

## If the backend fails live

Work down this list — don't spend more than a minute on any one step before
moving to the next:

1. **Retry once.** A slow/cold Space can look like a failure on the first
   request after sleeping.
2. **Switch to the Colab fallback.** If you kept the notebook open and
   already ran it earlier, this is just running the launch cell again for a
   fresh `gradio.live` link.
3. **Show the backup screenshot** of a previously successful run while you
   explain what would normally happen — say plainly that this is a
   recorded result, not a live call right now.
4. **Fall back to `deploy/index.html`** (already deployed to Vercel, or open
   the file locally) — it shows real recorded input/output pairs and the
   evaluation numbers. State clearly that it is a static backup, not a live
   model call.

Never present a static screenshot or the backup page as if it were live
inference — say explicitly which mode you're in.

## After the demo

- [ ] If peers tested it with real notices, no action needed — the app does
      not log or store submitted text anywhere; each request is stateless.
- [ ] If you deployed a Colab fallback link, disconnect the runtime once
      done (it counts against your Colab GPU quota while connected).
