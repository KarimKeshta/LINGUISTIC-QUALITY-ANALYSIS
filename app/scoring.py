from __future__ import annotations

import spacy
nlp = spacy.load("de_core_news_lg")

from typing import Any

def readability_score(
    readability: dict[str, Any],
) -> float:

    flesch = readability.get(
        "flesch_reading_ease"
    )

    if flesch is None:
        return 50.0

    # For German prose, we don't want to reward
    # extremely simple texts.
    #
    # Target range: approximately 0–30 for our
    # current German TextDescriptives output.

    if 0 <= flesch <= 30:
        return 100.0

    if flesch > 30:
        return max(
            60.0,
            100.0 - (flesch - 30) * 1.0
        )

    return max(
        50.0,
        100.0 + flesch * 1.0
    )

def calculate_score(result: dict[str, Any]) -> dict[str, Any]:

    linguistic = result["linguistic"]
    custom = linguistic["custom"]
    textdesc = linguistic["textdescriptives"]
    issues = result["language_issues"]

    grammar = grammar_score(
        issues,
        custom["words"],
    )

    vocabulary = vocabulary_score(
        custom,
    )

    sentence = sentence_score(
        custom,
    )

    readability = readability_score(
        textdesc["readability"],
    )

    redundancy = redundancy_score(
        result["text"]
    )

    overall = (
        grammar * 0.35
        + vocabulary * 0.20
        + sentence * 0.20
        + readability * 0.15
        + redundancy * 0.10
    )

    return {
        "overall": round(clamp(overall), 1),

        "dimensions": {
            "grammar": round(grammar, 1),
            "vocabulary": round(vocabulary, 1),
            "sentence_quality": round(sentence, 1),
            "readability": round(readability, 1),
            "redundancy": round(redundancy, 1),
        },

        "details": {
            "language_issues": len(issues),
            "words": custom["words"],
            "lexical_diversity": custom["lemma_type_token_ratio"],
            "lexical_density": custom["lexical_density"],
            "avg_sentence_length": custom["avg_sentence_length"],
            "sentence_length_std": custom["sentence_length_std"],
            "flesch_reading_ease": textdesc["readability"].get(
                "flesch_reading_ease"
            ),

            "quality_passed": getattr(
                textdesc["quality"],
                "passed",
                False,
            ),

            "grammar_score": grammar,
            "vocabulary_score": vocabulary,
            "sentence_score": sentence,
            "readability_score": readability,
        },
    }


def grammar_score(
    issues: list[dict[str, Any]],
    words: int,
) -> float:

    if words == 0:
        return 0.0

    penalty = 0.0

    for issue in issues:

        category = issue.get(
            "category",
            ""
        ).upper()

        rule = issue.get(
            "rule_id",
            ""
        ).upper()

        # Confirmed grammar problems
        if category in {
            "GRAMMAR",
            "CONFUSED_WORDS",
        }:
            penalty += 1.0

        # Real spelling errors
        elif (
            category == "TYPOS"
            and rule != "GERMAN_SPELLER_RULE"
        ):
            penalty += 0.8

        # Punctuation / typography
        elif category in {
            "PUNCTUATION",
            "TYPOGRAPHY",
        }:
            penalty += 0.4

        # Style suggestions
        elif category == "STYLE":
            penalty += 0.2

        # German spellchecker false positives:
        # don't count them as errors.
        elif (
            category == "TYPOS"
            and rule == "GERMAN_SPELLER_RULE"
        ):
            continue

    errors_per_100_words = (
        penalty / words * 100
    )

    # Gradual penalty instead of immediately
    # destroying the score.
    score = 100 - (
        errors_per_100_words * 5
    )

    return clamp(score)

def vocabulary_score(
    custom: dict[str, Any],
) -> float:

    diversity = custom["lemma_type_token_ratio"]
    density = custom["lexical_density"]

    # We currently don't assume that maximum diversity
    # means maximum quality.

    diversity_score = clamp(
        diversity * 100
    )

    density_score = range_score(
        density,
        0.30,
        0.60,
        0.30,
    )

    return (
        diversity_score * 0.5
        + density_score * 0.5
    )


def sentence_score(
    custom: dict[str, Any],
) -> float:

    length = custom["avg_sentence_length"]
    variation = custom["sentence_length_std"]

    length_score = range_score(
        length,
        8,
        25,
        10,
    )

    variation_score = range_score(
        variation,
        3,
        12,
        8,
    )

    return (
        length_score * 0.7
        + variation_score * 0.3
    )


def text_quality_score(
    quality: Any,
) -> float:

    checks: list[bool] = []

    def collect_checks(value: Any) -> None:

        if hasattr(value, "passed"):
            checks.append(bool(value.passed))
            return

        if isinstance(value, dict):
            for item in value.values():
                collect_checks(item)

        elif isinstance(value, (list, tuple)):
            for item in value:
                collect_checks(item)

        elif hasattr(value, "__dict__"):
            for item in vars(value).values():
                collect_checks(item)

    collect_checks(quality)

    if not checks:
        return 70.0

    return (
        sum(checks)
        / len(checks)
        * 100
    )


def range_score(
    value: float,
    minimum: float,
    maximum: float,
    tolerance: float,
) -> float:

    if minimum <= value <= maximum:
        return 100.0

    distance = (
        minimum - value
        if value < minimum
        else value - maximum
    )

    return clamp(
        100 - (distance / tolerance * 100)
    )


def clamp(value: float) -> float:

    return max(
        0.0,
        min(
            100.0,
            value,
        ),
    )

def redundancy_score(text: str) -> float:

    doc = nlp(text)

    word_counts: dict[str, int] = {}

    for token in doc:
        if token.is_alpha and not token.is_stop:
            lemma = token.lemma_.lower()
            word_counts[lemma] = (
                word_counts.get(lemma, 0) + 1
            )

    total_words = sum(word_counts.values())

    if total_words == 0:
        return 100.0

    repeated_words = sum(
        count - 1
        for count in word_counts.values()
        if count > 1
    )

    repetition_ratio = (
        repeated_words / total_words
    )

    # Gradual scoring:
    # 0% repetition  -> 100
    # 10%            -> 80
    # 20%            -> 60
    # 30%            -> 40
    # 40%+           -> 20

    score = 100 - (
        repetition_ratio * 200
    )

    return clamp(score)