import json
import os
import sys
import signal
from quiz import Quiz


class QuizGame:
    def __init__(self):
        self.file_name = "state.json"
        self.quizzes = []
        self.score = 0
        self.high_score = 0

        self.load_state()
        self.register_signal_handlers()

    def input_menu(self):
        print("\n=== 퀴즈 게임 ===")
        print("1. 퀴즈 추가")
        print("2. 퀴즈 목록 보기")
        print("3. 퀴즈 풀기")
        print("4. 저장")
        print("5. 종료")
        return input("메뉴를 선택하세요: ").strip()

    def input_quiz_data(self):
        question = input("문제를 입력하세요: ").strip()

        choices = []
        for i in range(1, 5):
            choice = input(f"{i}번 선택지: ").strip()
            choices.append(choice)

        while True:
            answer_input = input("정답 번호(1~4): ").strip()
            if answer_input.isdigit() and int(answer_input) in [1, 2, 3, 4]:
                answer = int(answer_input)
                break
            print("1~4 사이의 숫자를 입력해주세요.")

        explanation = input("해설(없으면 엔터): ").strip()

        return question, choices, answer, explanation

    def add_quiz(self):
        try:
            question, choices, answer, explanation = self.input_quiz_data()
            quiz = Quiz(
                question=question,
                choices=choices,
                answer=answer,
                explanation=explanation
            )
            self.quizzes.append(quiz)
            print("퀴즈가 추가되었습니다.")
        except ValueError as e:
            print(f"오류: {e}")

    def show_quizzes(self):
        if not self.quizzes:
            print("저장된 퀴즈가 없습니다.")
            return

        for idx, quiz in enumerate(self.quizzes, start=1):
            print(f"\n[{idx}번 퀴즈]")
            quiz.display()

    def play_quiz(self):
        if not self.quizzes:
            print("출제할 퀴즈가 없습니다.")
            return

        self.score = 0
        total = len(self.quizzes)

        print("\n=== 퀴즈 시작 ===")

        for idx, quiz in enumerate(self.quizzes, start=1):
            print(f"\n[{idx}번 문제]")
            quiz.display()

            while True:
                user_input = input("정답 번호를 입력하세요: ").strip()
                if user_input.isdigit() and int(user_input) in [1, 2, 3, 4]:
                    user_answer = int(user_input)
                    break
                print("1~4 사이의 숫자를 입력해주세요.")

            if quiz.check_answer(user_answer):
                print("정답입니다!")
                self.score += 1
            else:
                print(f"오답입니다. 정답은 {quiz.answer}번입니다.")
                if quiz.explanation:
                    print(f"해설: {quiz.explanation}")

        print("\n=== 결과 ===")
        print(f"총 문제 수: {total}")
        print(f"정답 수: {self.score}")
        print(f"오답 수: {total - self.score}")

        self.update_high_score()
        print(f"현재 최고점: {self.high_score}")

    def load_state(self):
        if not os.path.exists(self.file_name):
            self.quizzes = []
            self.high_score = 0
            return

        try:
            with open(self.file_name, "r", encoding="utf-8") as file:
                data = json.load(file)

            # 새로운 형식: {"high_score": ..., "quizzes": [...]}
            if isinstance(data, dict):
                self.high_score = int(data.get("high_score", 0))
                quiz_list = data.get("quizzes", [])
                self.quizzes = [Quiz.from_dict(item) for item in quiz_list]

            # 예전 형식: 퀴즈 리스트만 저장된 경우
            elif isinstance(data, list):
                self.quizzes = [Quiz.from_dict(item) for item in data]
                self.high_score = 0
            else:
                self.quizzes = []
                self.high_score = 0

        except (json.JSONDecodeError, KeyError, ValueError, OSError):
            print("state.json 파일을 불러오는 중 오류가 발생했습니다.")
            self.quizzes = []
            self.high_score = 0

    def save_state(self):
        data = {
            "high_score": self.high_score,
            "quizzes": [quiz.to_dict() for quiz in self.quizzes]
        }

        try:
            with open(self.file_name, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print("state.json에 저장되었습니다.")
        except OSError as e:
            print(f"저장 중 오류가 발생했습니다: {e}")

    def update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            print("최고점이 갱신되었습니다!")

    def end_game(self):
        print(f"이번 점수: {self.score}")
        print(f"현재 최고점: {self.high_score}")
        self.update_high_score()
        self.save_state()
        print(f"최종 최고점: {self.high_score}")

    def handle_exit_signal(self, signum, frame):
        print("\n종료 신호를 감지했습니다. 데이터를 저장합니다...")
        self.save_state()
        print("저장 후 안전하게 종료합니다.")
        sys.exit(0)

    def register_signal_handlers(self):
        signal.signal(signal.SIGINT, self.handle_exit_signal)

        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, self.handle_exit_signal)

    def run(self):
        while True:
            menu = self.input_menu()

            if menu == "1":
                self.add_quiz()
            elif menu == "2":
                self.show_quizzes()
            elif menu == "3":
                self.play_quiz()
            elif menu == "4":
                self.save_state()
            elif menu == "5":
                self.save_state()
                print("프로그램을 종료합니다.")
                break
            else:
                print("올바른 메뉴 번호를 입력하세요.")