from dataclasses import dataclass, field
from typing import Any, Dict, List
import uuid


@dataclass
class Quiz:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    question: str = ""
    choices: List[str] = field(default_factory=list)
    answer: int = 1
    hint: str = ""
    explanation: str = ""
    points: int = 10

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id.strip():
            self.id = str(uuid.uuid4())

        if not isinstance(self.question, str) or not self.question.strip():
            raise ValueError("문제는 비어 있지 않은 문자열이어야 합니다.")

        if not isinstance(self.choices, list) or len(self.choices) != 4:
            raise ValueError("선택지는 4개여야 합니다.")

        cleaned_choices = []
        for choice in self.choices:
            if not isinstance(choice, str) or not choice.strip():
                raise ValueError("각 선택지는 비어 있지 않은 문자열이어야 합니다.")
            cleaned_choices.append(choice.strip())
        self.choices = cleaned_choices

        if not isinstance(self.answer, int) or self.answer not in [1, 2, 3, 4]:
            raise ValueError("정답은 1~4 사이의 정수여야 합니다.")

        if not isinstance(self.points, int) or self.points <= 0:
            raise ValueError("점수는 1 이상의 정수여야 합니다.")

        self.question = self.question.strip()
        self.hint = self.hint.strip() if isinstance(self.hint, str) else ""
        self.explanation = self.explanation.strip() if isinstance(self.explanation, str) else ""

    def display(self):
        print(f"\n문제: {self.question}")
        for i, choice in enumerate(self.choices, start=1):
            print(f"{i}. {choice}")

    def check_answer(self, user_answer: int) -> bool:
        return user_answer == self.answer

    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
            "explanation": self.explanation,
            "points": self.points,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        if not isinstance(data, dict):
            raise ValueError("퀴즈 데이터 형식이 올바르지 않습니다.")

        choices = data.get("choices", [])
        if not isinstance(choices, list):
            raise ValueError("선택지 형식이 올바르지 않습니다.")

        try:
            answer = int(data.get("answer", 1))
        except (TypeError, ValueError):
            raise ValueError("정답 형식이 올바르지 않습니다.")

        try:
            points = int(data.get("points", 10))
        except (TypeError, ValueError):
            raise ValueError("점수 형식이 올바르지 않습니다.")

        return cls(
            id=str(data.get("id", str(uuid.uuid4()))),
            question=str(data.get("question", "")),
            choices=[str(x) for x in choices],
            answer=answer,
            hint=str(data.get("hint", "")),
            explanation=str(data.get("explanation", "")),
            points=points,
        )