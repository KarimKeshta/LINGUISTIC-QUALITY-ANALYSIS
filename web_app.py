from __future__ import annotations

import streamlit as st

from app.analyzer import TextAnalyzer


st.set_page_config(
    page_title="Linguistic Quality Analyzer",
    page_icon="📝",
    layout="wide",
)


@st.cache_resource
def get_analyzer() -> TextAnalyzer:
    return TextAnalyzer()


def main() -> None:
    st.title("Linguistic Quality Analyzer")

    st.markdown(
        """
        Analyze the linguistic characteristics of a text using
        grammar checking, NLP and statistical linguistic measures.
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
    metrics = result["metrics"]
    issues = result["language_issues"]

    st.divider()

    st.header("Analysis")

    # ---------------------------------------------------------
    # Basic statistics
    # ---------------------------------------------------------

    st.subheader("Text Statistics")

    columns = st.columns(4)

    columns[0].metric(
        "Words",
        metrics["words"],
    )

    columns[1].metric(
        "Sentences",
        metrics["sentences"],
    )

    columns[2].metric(
        "Avg. sentence length",
        f"{metrics['avg_sentence_length']:.1f}",
    )

    columns[3].metric(
        "Avg. word length",
        f"{metrics['avg_word_length']:.1f}",
    )

    # ---------------------------------------------------------
    # Lexical characteristics
    # ---------------------------------------------------------

    st.subheader("Lexical Characteristics")

    columns = st.columns(3)

    columns[0].metric(
        "Unique lemmas",
        metrics["unique_lemmas"],
    )

    columns[1].metric(
        "Lemma TTR",
        f"{metrics['lemma_type_token_ratio']:.3f}",
    )

    columns[2].metric(
        "Lexical density",
        f"{metrics['lexical_density']:.3f}",
    )

    # ---------------------------------------------------------
    # Syntax
    # ---------------------------------------------------------

    st.subheader("Syntactic Characteristics")

    columns = st.columns(3)

    columns[0].metric(
        "Dependency depth",
        f"{metrics['avg_dependency_depth']:.2f}",
    )

    columns[1].metric(
        "Shortest sentence",
        metrics["min_sentence_length"],
    )

    columns[2].metric(
        "Longest sentence",
        metrics["max_sentence_length"],
    )

    # ---------------------------------------------------------
    # LanguageTool
    # ---------------------------------------------------------

    st.subheader("Language Issues")

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