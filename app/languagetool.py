from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import language_tool_python


@dataclass
class LanguageIssue:
    offset: int
    length: int
    message: str
    category: str
    rule_id: str
    replacements: list[str]


class LanguageToolAnalyzer:
    """
    Local LanguageTool-based grammar, spelling and style analysis.
    """

    def __init__(self, language: str = "de-DE") -> None:
        self.language = language
        self.tool = language_tool_python.LanguageTool(
            language,
            language_tool_download_version="6.8",
        )

    def analyze(self, text: str) -> list[LanguageIssue]:
        matches = self.tool.check(text)

        issues: list[LanguageIssue] = []

        for match in matches:
            issues.append(
                LanguageIssue(
                    offset=match.offset,
                    length=match.error_length,
                    message=match.message,
                    category=getattr(
                        match.category,
                        "id",
                        str(match.category),
                    ),
                    rule_id=match.rule_id,
                    replacements=list(match.replacements),
                )
            )

        return issues

    def close(self) -> None:
        self.tool.close()

    def __enter__(self) -> "LanguageToolAnalyzer":
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        self.close()