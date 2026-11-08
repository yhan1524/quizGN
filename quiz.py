class Quiz:
    def __init__(self, question, choices, answer):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제는 비어 있지 않은 문자열이어야 합니다.")

        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("선택지는 4개의 항목을 가진 리스트여야 합니다.")

        for choice in choices:
            if not isinstance(choice, str) or not choice.strip():
                raise ValueError("각 선택지는 비어 있지 않은 문자열이어야 합니다.")

        if not isinstance(answer, int) or answer not in [1, 2, 3, 4]:
            raise ValueError("정답은 1~4 사이의 정수여야 합니다.")

        self.question = question.strip()
        self.choices = [choice.strip() for choice in choices]
        self.answer = answer

    def display(self):
        print(f"\n문제: {self.question}")
        for i, choice in enumerate(self.choices, start=1):
            print(f"{i}. {choice}")

    def check_answer(self, user_answer):
        return user_answer == self.answer

    def to_dict(self):
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["question"], data["choices"], data["answer"])
    
from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class Quiz:
    id: str
    question: str
    choices: List[str]
    answer: int
    explanation: str = ""
    points: int = 10

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Quiz":
        required_keys = ["id", "question", "choices", "answer"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"퀴즈 데이터에 '{key}' 항목이 없습니다.")

        return cls(
            id=str(data["id"]).strip(),
            question=str(data["question"]).strip(),
            choices=[str(choice).strip() for choice in data["choices"]],
            answer=int(data["answer"]),
            explanation=str(data.get("explanation", "")).strip(),
            points=int(data.get("points", 10)),
        )