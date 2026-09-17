"""
Bayyin · بيّن — the pipeline

input -> validate -> build the prompt -> ONE model call -> parse and
validate (the gate) -> return. This is the whole application, in the
order the brief asks for it. Nothing here is a second model call.
"""

from . import gate, model, prompts


def simplify_and_validate(original: str) -> dict:
    if not original or not original.strip():
        return {"error": "الرجاء إدخال نص."}
    if len(original) > prompts.MAX_INPUT_CHARS:
        return {"error": f"النص أطول من {prompts.MAX_INPUT_CHARS} حرف."}

    messages = prompts.build_messages(original)
    result = model.ask(messages, max_new_tokens=prompts.MAX_NEW_TOKENS)
    simplified = result["reply"]

    check = gate.validate_preserved_facts(original, simplified)

    return {
        "original": original,
        "simplified": simplified,
        "gate_passed": check["passed"],
        "missing_numbers": check["missing_numbers"],
        "facts_detected": check["facts_detected"],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "truncated": result["truncated"],
        "disclosure": prompts.DISCLOSURE,
        "error": None,
    }
