from __future__ import annotations

from collections import Counter
from typing import Any

import spacy


class LinguisticAnalyzer:
    """
    Extracts basic linguistic statistics from German text.
    """

    def __init__(self, model: str = "de_core_news_lg") -> None:
        self.nlp = spacy.load(model)

    def analyze(self, text: str) -> dict[str, Any]:
        doc = self.nlp(text)

        sentences = list(doc.sents)

        words = [
            token
            for token in doc
            if not token.is_space and not token.is_punct
        ]

        alphabetic_words = [
            token
            for token in words
            if token.is_alpha
        ]

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
            for token in alphabetic_words
        ]

        lemmas = [
            token.lemma_.lower()
            for token in alphabetic_words
            if token.lemma_
        ]

        unique_lemmas = set(lemmas)

        pos_counts = Counter(
            token.pos_
            for token in words
        )

        dependency_depths = [
            self._dependency_depth(token)
            for token in words
        ]

        return {
            "characters": len(text),
            "tokens": len(words),
            "words": len(alphabetic_words),
            "sentences": len(sentences),

            "avg_sentence_length": (
                sum(sentence_lengths) / len(sentence_lengths)
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

            "avg_word_length": (
                sum(word_lengths) / len(word_lengths)
                if word_lengths
                else 0.0
            ),

            "unique_lemmas": len(unique_lemmas),

            "lemma_type_token_ratio": (
                len(unique_lemmas) / len(lemmas)
                if lemmas
                else 0.0
            ),

            "lexical_density": (
                self._lexical_density(doc)
            ),

            "avg_dependency_depth": (
                sum(dependency_depths) / len(dependency_depths)
                if dependency_depths
                else 0.0
            ),

            "pos_distribution": dict(pos_counts),
        }

    @staticmethod
    def _lexical_density(doc) -> float:
        """
        Approximation of lexical density.

        Content words:
        NOUN, VERB, ADJ, ADV, PROPN
        """

        tokens = [
            token
            for token in doc
            if not token.is_space
            and not token.is_punct
        ]

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