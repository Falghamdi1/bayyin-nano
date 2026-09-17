"""
Bayyin · بيّن — the gate

Verification today is code, not a second model call — one generation per
notice, per the brief. The gate checks the one thing a human can trust
immediately: every number and date in the original still appears in the
simplified version.

This module was rewritten once already. The first version used Python's
`\\d` regex class directly, which is Unicode-aware and silently matched
Eastern Arabic-Indic digits (٠-٩) as well as Western ones — the *same*
number then existed as two different strings in the comparison set, which
produced a false "missing number" flag on text that was actually correct.
The fix: normalize the whole string to Western digits first, then extract
once. The self-tests below exist so that bug cannot come back unnoticed.
"""

import re

EASTERN_TO_WESTERN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def extract_numbers(text: str) -> set:
    normalized = text.translate(EASTERN_TO_WESTERN)
    return set(re.findall(r"[0-9]+", normalized))


def validate_preserved_facts(original: str, simplified: str) -> dict:
    original_numbers = extract_numbers(original)
    simplified_numbers = extract_numbers(simplified)
    missing = original_numbers - simplified_numbers

    return {
        "original_numbers": sorted(original_numbers),
        "simplified_numbers": sorted(simplified_numbers),
        "missing_numbers": sorted(missing),
        "passed": len(missing) == 0,
    }


def _self_test() -> None:
    assert validate_preserved_facts(
        "الرسوم 250 ريال خلال 15 يوماً", "الرسوم 250 ريال خلال 15 يوماً بس أوضح"
    )["passed"], "self-test failed — the checker itself is broken"

    assert not validate_preserved_facts(
        "الرسوم 250 ريال", "الرسوم غير محددة"
    )["passed"], "self-test failed — should have caught a dropped number"

    assert validate_preserved_facts(
        "الرسوم ٢٥٠ ريال", "الرسوم 250 ريال بس أوضح"
    )["passed"], "self-test failed — Eastern Arabic-Indic digits should match their Western form"

    assert not validate_preserved_facts(
        "الرسوم ٢٥٠ ريال", "الرسوم غير محددة"
    )["passed"], "self-test failed — should catch a dropped Eastern-digit number too"


_self_test()
