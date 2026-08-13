from __future__ import annotations

from typing import Any

from .languagetool import LanguageIssue, LanguageToolAnalyzer
from .linguistic_metrics import LinguisticAnalyzer
from .scoring import calculate_score


class TextAnalyzer:

    def __init__(self) -> None:
        self.linguistic = LinguisticAnalyzer()
        self.language_tool = LanguageToolAnalyzer()

    def analyze(
        self,
        text: str,
    ) -> dict[str, Any]:

        linguistic_result = self.linguistic.analyze(text)

        issues = self.language_tool.analyze(text)

        result = {
            "text": text,
            "linguistic": linguistic_result,
            "language_issues": [
                self._issue_to_dict(issue)
                for issue in issues
            ],
        }

        result["score"] = calculate_score(result)

        return result

    @staticmethod
    def _issue_to_dict(
        issue: LanguageIssue,
    ) -> dict[str, Any]:

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