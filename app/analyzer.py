from __future__ import annotations

from typing import Any

from .languagetool import LanguageIssue, LanguageToolAnalyzer
from .linguistic_metrics import LinguisticAnalyzer


class TextAnalyzer:

    def __init__(self) -> None:
        self.linguistic = LinguisticAnalyzer()
        self.language_tool = LanguageToolAnalyzer()

    def analyze(self, text: str) -> dict[str, Any]:

        metrics = self.linguistic.analyze(text)
        issues = self.language_tool.analyze(text)

        return {
            "metrics": metrics,
            "language_issues": [
                self._issue_to_dict(issue)
                for issue in issues
            ],
        }

    @staticmethod
    def _issue_to_dict(issue: LanguageIssue) -> dict[str, Any]:
        return {
            "offset": issue.offset,
            "length": issue.length,
            "message": issue.message,
            "category": issue.category,
            "rule_id": issue.rule_id,
            "replacements": issue.replacements,
        }

    def close(self) -> None:
        self.language_tool.close()