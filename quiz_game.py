import json
import os
import sys
import signal
import random
from datetime import datetime

from quiz import Quiz


class QuizGame:
    def __init__(self):
        self.file_name = "state.json"
        self.quizzes = []
        self.score = 0
        self.high_score = 0
        self.history = []

        self.load_state()
        self.register_signal_handlers()

    def input_menu(self):
        print("\n=== 퀴즈 게임 ===")
        print("1. 퀴즈 추가")
        print("2. 퀴즈 목록 보기")
        print("3. 퀴즈 풀기")
        print("4. 퀴즈 삭제")
        print("5. 점수 기록 보기")
        print("6. 저장")
        print("7. 종료")
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

        hint = input("힌트(없으면 엔터): ").strip()
        explanation = input("해설(없으면 엔터): ").strip()

        while True:
            points_input = input("문제 점수(기본 10점): ").strip()
            if points_input == "":
                points = 10
                break
            if points_input.isdigit() and int(points_input) > 0:
                points = int(points_input)
                break
            print("1 이상의 숫자를 입력해주세요.")

        return question, choices, answer, hint, explanation, points

    def add_quiz(self):
        try:
            question, choices, answer, hint, explanation, points = self.input_quiz_data()
            quiz = Quiz(
                question=question,
                choices=choices,
                answer=answer,
                hint=hint,
                explanation=explanation,
                points=points
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
            print(f"힌트: {quiz.hint if quiz.hint else '없음'}")
            print(f"해설: {quiz.explanation if quiz.explanation else '없음'}")
            print(f"점수: {quiz.points}")

    def choose_quiz_count(self):
        while True:
            count_input = input(f"몇 문제를 풀까요? (1~{len(self.quizzes)}): ").strip()
            if count_input.isdigit():
                count = int(count_input)
                if 1 <= count <= len(self.quizzes):
                    return count
            print("올바른 범위의 숫자를 입력해주세요.")

    def play_quiz(self):
        if not self.quizzes:
            print("출제할 퀴즈가 없습니다.")
            return

        count = self.choose_quiz_count()

        # 문제를 랜덤하게 선택
        selected_quizzes = random.sample(self.quizzes, count)

        self.score = 0
        max_score = 0
        hint_used_count = 0

        print("\n=== 퀴즈 시작 ===")

        for idx, quiz in enumerate(selected_quizzes, start=1):
            print(f"\n[{idx}번 문제]")
            quiz.display()

            hint_used = False

            while True:
                user_input = input("정답 번호(1~4) 또는 h(힌트): ").strip().lower()

                if user_input == "h":
                    if quiz.hint:
                        print(f"힌트: {quiz.hint}")
                        hint_used = True
                    else:
                        print("이 문제에는 힌트가 없습니다.")
                    continue

                if user_input.isdigit() and int(user_input) in [1, 2, 3, 4]:
                    user_answer = int(user_input)
                    break

                print("1~4 또는 h를 입력해주세요.")

            earned_points = quiz.points
            if hint_used:
                hint_used_count += 1
                earned_points = max(0, quiz.points - 2)  # 힌트 사용 시 2점 차감

            max_score += quiz.points

            if quiz.check_answer(user_answer):
                print(f"정답입니다! +{earned_points}점")
                self.score += earned_points
            else:
                print(f"오답입니다. 정답은 {quiz.answer}번입니다.")
                if quiz.explanation:
                    print(f"해설: {quiz.explanation}")

        print("\n=== 결과 ===")
        print(f"푼 문제 수: {count}")
        print(f"점수: {self.score} / {max_score}")
        print(f"힌트 사용 횟수: {hint_used_count}")

        if self.score > self.high_score:
            self.high_score = self.score
            print("최고 점수가 갱신되었습니다!")

        self.history.append({
            "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "selected_count": count,
            "score": self.score,
            "max_score": max_score,
            "hint_used_count": hint_used_count
        })

        self.save_state()

    def delete_quiz(self):
        if not self.quizzes:
            print("삭제할 퀴즈가 없습니다.")
            return

        self.show_quizzes()

        while True:
            idx_input = input("삭제할 퀴즈 번호를 입력하세요: ").strip()
            if idx_input.isdigit():
                idx = int(idx_input)
                if 1 <= idx <= len(self.quizzes):
                    removed = self.quizzes.pop(idx - 1)
                    print(f"'{removed.question}' 퀴즈가 삭제되었습니다.")
                    self.save_state()
                    return
            print("올바른 번호를 입력해주세요.")

    def show_history(self):
        if not self.history:
            print("저장된 기록이 없습니다.")
            return

        print("\n=== 점수 기록 ===")
        for i, record in enumerate(self.history, start=1):
            print(f"\n[{i}번 기록]")
            print(f"날짜/시간: {record['played_at']}")
            print(f"푼 문제 수: {record['selected_count']}")
            print(f"점수: {record['score']} / {record['max_score']}")
            print(f"힌트 사용 횟수: {record['hint_used_count']}")

    def load_state(self):
        if not os.path.exists(self.file_name):
            self.quizzes = []
            self.high_score = 0
            self.history = []
            return

        try:
            with open(self.file_name, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, dict):
                self.high_score = int(data.get("high_score", 0))
                self.quizzes = [Quiz.from_dict(q) for q in data.get("quizzes", [])]
                self.history = data.get("history", [])
            elif isinstance(data, list):
                # 예전 형식 호환
                self.quizzes = [Quiz.from_dict(q) for q in data]
                self.high_score = 0
                self.history = []
            else:
                self.quizzes = []
                self.high_score = 0
                self.history = []

        except (json.JSONDecodeError, KeyError, ValueError, OSError):
            print("state.json 파일을 불러오는 중 오류가 발생했습니다.")
            self.quizzes = []
            self.high_score = 0
            self.history = []

    def save_state(self):
        data = {
            "high_score": self.high_score,
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "history": self.history
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
                self.delete_quiz()
            elif menu == "5":
                self.show_history()
            elif menu == "6":
                self.save_state()
            elif menu == "7":
                self.save_state()
                print("프로그램을 종료합니다.")
                break
            else:
                print("올바른 메뉴 번호를 입력하세요.")