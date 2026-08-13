from __future__ import annotations

from collections import Counter
from typing import Any

import spacy
import textdescriptives


class LinguisticAnalyzer:

    def __init__(
        self,
        model: str = "de_core_news_lg",
    ) -> None:

        self.nlp = spacy.load(model)

        self.nlp.add_pipe(
            "textdescriptives/all",
        )

    def analyze(
        self,
        text: str,
    ) -> dict[str, Any]:

        doc = self.nlp(text)

        return {
            "textdescriptives": {
                "descriptive_stats": doc._.descriptive_stats,
                "readability": doc._.readability,
                "dependency_distance": doc._.dependency_distance,
                "pos_proportions": doc._.pos_proportions,
                "quality": doc._.quality,
            },

            "custom": self._custom_metrics(doc),
        }

    def _custom_metrics(
        self,
        doc,
    ) -> dict[str, Any]:

        tokens = [
            token
            for token in doc
            if not token.is_space
            and not token.is_punct
        ]

        words = [
            token
            for token in tokens
            if token.is_alpha
        ]

        sentences = list(doc.sents)

        sentence_lengths = [
            sum(
                1
                for token in sentence
                if not token.is_space
                and not token.is_punct
            )
            for sentence in sentences
        ]

        word_lengths = [
            len(token.text)
            for token in words
        ]

        lemmas = [
            token.lemma_.lower()
            for token in words
            if token.lemma_
        ]

        unique_lemmas = set(lemmas)

        pos_counts = Counter(
            token.pos_
            for token in tokens
        )

        dependency_depths = [
            self._dependency_depth(token)
            for token in tokens
        ]

        return {
            "characters": len(doc.text),
            "tokens": len(tokens),
            "words": len(words),
            "sentences": len(sentences),

            "avg_sentence_length": (
                sum(sentence_lengths)
                / len(sentence_lengths)
                if sentence_lengths
                else 0.0
            ),

            "min_sentence_length": (
                min(sentence_lengths)
                if sentence_lengths
                else 0
            ),

            "max_sentence_length": (
                max(sentence_lengths)
                if sentence_lengths
                else 0
            ),

            "sentence_length_std": (
                self._standard_deviation(sentence_lengths)
                if sentence_lengths
                else 0.0
            ),

            "avg_word_length": (
                sum(word_lengths)
                / len(word_lengths)
                if word_lengths
                else 0.0
            ),

            "unique_lemmas": len(unique_lemmas),

            "lemma_type_token_ratio": (
                len(unique_lemmas)
                / len(lemmas)
                if lemmas
                else 0.0
            ),

            "lexical_density": (
                self._lexical_density(tokens)
            ),

            "avg_dependency_depth": (
                sum(dependency_depths)
                / len(dependency_depths)
                if dependency_depths
                else 0.0
            ),

            "pos_distribution": dict(pos_counts),
        }

    @staticmethod
    def _lexical_density(tokens) -> float:

        if not tokens:
            return 0.0

        content_words = [
            token
            for token in tokens
            if token.pos_ in {
                "NOUN",
                "VERB",
                "ADJ",
                "ADV",
                "PROPN",
            }
        ]

        return len(content_words) / len(tokens)

    @staticmethod
    def _dependency_depth(token) -> int:

        depth = 0
        current = token

        while current.head != current:
            depth += 1
            current = current.head

        return depth

    @staticmethod
    def _standard_deviation(
        values: list[float],
    ) -> float:

        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)

        variance = sum(
            (value - mean) ** 2
            for value in values
        ) / len(values)

        return variance ** 0.5