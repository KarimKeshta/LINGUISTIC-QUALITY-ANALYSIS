from __future__ import annotations

from typing import Any


def print_report(result: dict[str, Any]) -> None:

    metrics = result["metrics"]
    issues = result["language_issues"]

    print()
    print("=" * 60)
    print("LINGUISTIC QUALITY ANALYSIS")
    print("=" * 60)

    print()
    print("TEXT STATISTICS")
    print("-" * 60)

    print(f"Characters:              {metrics['characters']}")
    print(f"Words:                   {metrics['words']}")
    print(f"Sentences:               {metrics['sentences']}")

    print(
        f"Average sentence length: "
        f"{metrics['avg_sentence_length']:.2f} words"
    )

    print(
        f"Shortest sentence:       "
        f"{metrics['min_sentence_length']} words"
    )

    print(
        f"Longest sentence:        "
        f"{metrics['max_sentence_length']} words"
    )

    print(
        f"Average word length:     "
        f"{metrics['avg_word_length']:.2f} characters"
    )

    print()
    print("LEXICAL CHARACTERISTICS")
    print("-" * 60)

    print(
        f"Unique lemmas:            "
        f"{metrics['unique_lemmas']}"
    )

    print(
        f"Lemma type-token ratio:   "
        f"{metrics['lemma_type_token_ratio']:.3f}"
    )

    print(
        f"Lexical density:          "
        f"{metrics['lexical_density']:.3f}"
    )

    print()
    print("SYNTACTIC CHARACTERISTICS")
    print("-" * 60)

    print(
        f"Average dependency depth: "
        f"{metrics['avg_dependency_depth']:.2f}"
    )

    print()
    print("LANGUAGE ISSUES")
    print("-" * 60)

    print(f"Total detected issues: {len(issues)}")

    if not issues:
        print("No issues detected.")

    else:
        for index, issue in enumerate(issues, start=1):
            print()
            print(f"{index}. {issue['message']}")
            print(f"   Category: {issue['category']}")
            print(f"   Rule:     {issue['rule_id']}")

            if issue["replacements"]:
                replacements = ", ".join(
                    issue["replacements"][:5]
                )

                print(
                    f"   Suggestions: {replacements}"
                )

    print()
    print("=" * 60)