from __future__ import annotations

import streamlit as st

from app.analyzer import TextAnalyzer


st.set_page_config(
    page_title="Linguistic Quality Analyzer",
    page_icon="📝",
    layout="wide",
)


#@st.cache_resource
def get_analyzer() -> TextAnalyzer:
    return TextAnalyzer()


def main() -> None:
    st.title("Linguistic Quality")

    st.markdown(
        """
        Evaluate the linguistic quality of a text using
        automated linguistic analysis.
        """
    )

    st.divider()

    text = st.text_area(
        "Text to analyze",
        height=300,
        placeholder="Paste your text here...",
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        st.caption(
            f"Characters: {len(text):,}"
        )

    with col2:
        analyze = st.button(
            "Analyze Text",
            type="primary",
            use_container_width=True,
        )

    if not analyze:
        return

    if not text.strip():
        st.warning("Please enter some text first.")
        return

    with st.spinner("Analyzing text..."):
        analyzer = get_analyzer()
        result = analyzer.analyze(text)

    display_results(result)


def display_results(result: dict) -> None:

    score = result["score"]

    linguistic = result["linguistic"]
    custom = linguistic["custom"]

    issues = result["language_issues"]

    dimensions = score["dimensions"]

    # =========================================================
    # Overall Score
    # =========================================================

    st.divider()

    st.subheader("Linguistic Quality")

    overall = score["overall"]

    if overall >= 85:
        interpretation = "Very good"
    elif overall >= 70:
        interpretation = "Good"
    elif overall >= 55:
        interpretation = "Acceptable"
    elif overall >= 40:
        interpretation = "Weak"
    else:
        interpretation = "Poor"

    # Center the score
    left, center, right = st.columns([1, 2, 1])

    with center:
        st.metric(
            "Overall Score",
            f"{overall:.1f} / 100",
            interpretation,
        )

        st.progress(
            overall / 100
        )

    # =========================================================
    # Quality dimensions
    # =========================================================

    st.subheader("Quality Profile")

    columns = st.columns(5)

    dimension_data = [
        ("Grammar", dimensions["grammar"]),
        ("Vocabulary", dimensions["vocabulary"]),
        ("Sentence Quality", dimensions["sentence_quality"]),
        ("Readability", dimensions["readability"]),
        ("Redundancy", dimensions["redundancy"]),
    ]

    for column, (name, value) in zip(
        columns,
        dimension_data,
    ):
        with column:
            st.metric(
                name,
                f"{value:.0f}",
            )

            st.progress(
                value / 100
            )

    # =========================================================
    # Main weaknesses
    # =========================================================

    st.subheader("Assessment")

    weaknesses = []

    if dimensions["grammar"] < 70:
        weaknesses.append("Grammar & spelling")

    if dimensions["vocabulary"] < 70:
        weaknesses.append("Vocabulary")

    if dimensions["sentence_quality"] < 70:
        weaknesses.append("Sentence quality")

    if dimensions["readability"] < 70:
        weaknesses.append("Readability")

    if weaknesses:
        st.warning(
            "**Main weaknesses:** "
            + ", ".join(weaknesses)
        )
    else:
        st.success(
            "No major weaknesses detected."
        )

    # =========================================================
    # Detailed analysis
    # =========================================================

    with st.expander("Detailed analysis"):

        # -----------------------------------------------------
        # Scoring diagnostics
        # -----------------------------------------------------

        st.markdown("### Scoring Diagnostics")

        details = score["details"]

        debug_data = {
            "LanguageTool issues":
                details["language_issues"],

            "Words":
                details["words"],

            "Lexical diversity":
                details["lexical_diversity"],

            "Lexical density":
                details["lexical_density"],

            "Average sentence length":
                details["avg_sentence_length"],

            "Sentence length variation":
                details["sentence_length_std"],

            "Flesch Reading Ease":
                details["flesch_reading_ease"],

            "Text quality passed":
                details["quality_passed"],
        }

        st.json(debug_data)

        st.markdown("#### Dimension calculations")

        dimension_debug = {
            "Grammar":
                details["grammar_score"],

            "Vocabulary":
                details["vocabulary_score"],

            "Sentence quality":
                details["sentence_score"],

            "Readability":
                details["readability_score"],
        }

        st.json(dimension_debug)


        # -----------------------------------------------------
        # Basic statistics
        # -----------------------------------------------------

        st.markdown("### Text Statistics")

        columns = st.columns(4)

        columns[0].metric(
            "Words",
            custom["words"],
        )

        columns[1].metric(
            "Sentences",
            custom["sentences"],
        )

        columns[2].metric(
            "Avg. sentence length",
            f"{custom['avg_sentence_length']:.1f}",
        )

        columns[3].metric(
            "Avg. word length",
            f"{custom['avg_word_length']:.1f}",
        )

        # -----------------------------------------------------
        # Lexical
        # -----------------------------------------------------

        st.markdown("### Lexical Characteristics")

        columns = st.columns(3)

        columns[0].metric(
            "Unique lemmas",
            custom["unique_lemmas"],
        )

        columns[1].metric(
            "Lemma TTR",
            f"{custom['lemma_type_token_ratio']:.3f}",
        )

        columns[2].metric(
            "Lexical density",
            f"{custom['lexical_density']:.3f}",
        )

        # -----------------------------------------------------
        # Sentence structure
        # -----------------------------------------------------

        st.markdown("### Sentence Structure")

        columns = st.columns(4)

        columns[0].metric(
            "Average",
            f"{custom['avg_sentence_length']:.1f}",
        )

        columns[1].metric(
            "Shortest",
            custom["min_sentence_length"],
        )

        columns[2].metric(
            "Longest",
            custom["max_sentence_length"],
        )

        columns[3].metric(
            "Variation",
            f"{custom['sentence_length_std']:.1f}",
        )

        # -----------------------------------------------------
        # Language issues
        # -----------------------------------------------------

        st.markdown("### Language Issues")

        if not issues:

            st.success(
                "LanguageTool did not detect any issues."
            )

        else:

            st.warning(
                f"{len(issues)} potential issue(s) detected."
            )

            for index, issue in enumerate(
                issues,
                start=1,
            ):

                with st.expander(
                    f"{index}. {issue['message']}"
                ):

                    st.write(
                        f"**Category:** "
                        f"{issue['category']}"
                    )

                    st.write(
                        f"**Rule:** "
                        f"`{issue['rule_id']}`"
                    )

                    if issue["replacements"]:

                        st.write(
                            "**Suggestions:** "
                            + ", ".join(
                                issue["replacements"][:5]
                            )
                        )


if __name__ == "__main__":
    main()