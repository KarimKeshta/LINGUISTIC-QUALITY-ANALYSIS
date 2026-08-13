from __future__ import annotations

from typing import Any


def calculate_score(result: dict[str, Any]) -> dict[str, Any]:
    """
    Calculate an initial 0-100 linguistic quality score.

    This is an MVP heuristic model.
    It is intentionally transparent and will be refined later.
    """

    linguistic = result["linguistic"]

    custom = linguistic["custom"]

    textdesc = linguistic["textdescriptives"]

    issues = result["language_issues"]

    # ---------------------------------------------------------
    # 1. Grammar & spelling
    # ---------------------------------------------------------

    words = max(custom["words"], 1)

    error_rate = len(issues) / words

    # 0 errors -> 100
    # 1 error / 100 words -> ~90
    # 5 errors / 100 words -> ~50
    grammar_score = max(
        0.0,
        100.0 * (1.0 - error_rate * 10.0),
    )

    # ---------------------------------------------------------
    # 2. Readability
    # ---------------------------------------------------------

    readability = textdesc["readability"]

    flesch = readability["flesch_reading_ease"]

    # We don't want extreme values to dominate.
    readability_score = _clamp(
        flesch,
        0.0,
        100.0,
    )

    # ---------------------------------------------------------
    # 3. Lexical quality
    # ---------------------------------------------------------

    lexical_density = custom["lexical_density"]

    lexical_diversity = custom[
        "lemma_type_token_ratio"
    ]

    # Moderate lexical density is generally preferable
    # to extremely low density.
    density_score = _range_score(
        lexical_density,
        ideal_min=0.35,
        ideal_max=0.65,
    )

    diversity_score = _clamp(
        lexical_diversity * 100.0,
        0.0,
        100.0,
    )

    lexical_score = (
        density_score * 0.4
        + diversity_score * 0.6
    )

    # ---------------------------------------------------------
    # 4. Sentence structure
    # ---------------------------------------------------------

    avg_sentence_length = custom[
        "avg_sentence_length"
    ]

    sentence_variation = custom[
        "sentence_length_std"
    ]

    # Approximate useful range for general prose.
    sentence_length_score = _range_score(
        avg_sentence_length,
        ideal_min=10.0,
        ideal_max=25.0,
    )

    # Some variation is preferable to completely
    # monotonous sentence lengths.
    variation_score = _range_score(
        sentence_variation,
        ideal_min=3.0,
        ideal_max=12.0,
    )

    syntax_score = (
        sentence_length_score * 0.7
        + variation_score * 0.3
    )

    # ---------------------------------------------------------
    # 5. Text cleanliness
    # ---------------------------------------------------------

    quality = textdesc["quality"]

    # TextDescriptives provides an overall quality check.
    #
    # We don't use it as "linguistic quality".
    # We only use it as one signal.

    quality_score = 100.0 if quality.passed else 70.0

    # ---------------------------------------------------------
    # Final score
    # ---------------------------------------------------------

    overall = (
        grammar_score * 0.30
        + readability_score * 0.20
        + lexical_score * 0.20
        + syntax_score * 0.15
        + quality_score * 0.15
    )

    return {
        "overall": round(
            _clamp(overall, 0.0, 100.0),
            1,
        ),

        "dimensions": {
            "grammar": round(
                grammar_score,
                1,
            ),

            "readability": round(
                readability_score,
                1,
            ),

            "lexical": round(
                lexical_score,
                1,
            ),

            "syntax": round(
                syntax_score,
                1,
            ),

            "cleanliness": round(
                quality_score,
                1,
            ),
        },

        "details": {
            "grammar_error_rate": error_rate,
            "language_issues": len(issues),
            "words": words,
            "flesch": flesch,
            "lexical_density": lexical_density,
            "lexical_diversity": lexical_diversity,
            "avg_sentence_length": avg_sentence_length,
            "sentence_length_variation": sentence_variation,
        },
    }


def _clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:

    return max(
        minimum,
        min(value, maximum),
    )


def _range_score(
    value: float,
    ideal_min: float,
    ideal_max: float,
) -> float:

    if ideal_min <= value <= ideal_max:
        return 100.0

    if value < ideal_min:
        distance = ideal_min - value
        return max(
            0.0,
            100.0 - distance * 5.0,
        )

    distance = value - ideal_max

    return max(
        0.0,
        100.0 - distance * 5.0,
    )