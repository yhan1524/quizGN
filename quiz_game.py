import json
import os
import sys
import signal
import random
import shutil

from datetime import datetime

from quiz import Quiz


class QuizGame:
    def __init__(self):
        self.file_name = os.path.join(os.path.dirname(__file__), "state.json")

        # 기본 문제는 코드에 내장
        self.default_quizzes = self.get_default_quizzes()

        # 실제 실행 중 사용할 퀴즈 목록
        self.quizzes = []

        self.score = 0
        self.high_score = 0
        self.history = []

        self.load_state()
        self.register_signal_handlers()

    def get_default_quizzes(self):
        """기본 문제 목록을 반환합니다."""
        return [
            Quiz(
                id="default-1",
                question="파이썬에서 출력에 사용하는 함수는?",
                choices=["print()", "input()", "len()", "type()"],
                answer=1,
                hint="화면에 무엇인가를 보여줄 때 씁니다.",
                explanation="파이썬의 출력 함수는 print()입니다.",
                points=10
            ),
            Quiz(
                id="default-2",
                question="리스트의 길이를 구하는 함수는?",
                choices=["size()", "count()", "len()", "sum()"],
                answer=3,
                hint="문자열 길이도 구할 수 있는 함수입니다.",
                explanation="리스트나 문자열의 길이는 len()으로 구합니다.",
                points=10
            ),
            Quiz(
                id="default-3",
                question="조건문에 사용하는 키워드는?",
                choices=["for", "if", "def", "class"],
                answer=2,
                hint="조건에 따라 실행을 나눌 때 사용합니다.",
                explanation="조건문은 if를 사용합니다.",
                points=10
            ),
            Quiz(
                id="default-4",
                question="사용자로부터 값을 입력받을 때 사용하는 함수는 무엇인가요?",
                choices=["print()", "type()", "input()", "range()"],
                answer=3,
                points=10
            ),
            Quiz(
                id="default-5",
                question="input() 함수로 입력받은 값의 기본 자료형은 무엇인가요?",
                choices=["int", "float", "str", "bool"],
                answer=3,
                points=10
            ),
            Quiz(
                id="default-6",
                question="같은 코드를 여러 번 반복할 때 주로 사용하는 문장은 무엇인가요?",
                choices=["if", "return", "for", "class"],
                answer=3,
                points=10
            ),
            Quiz(
                id="default-7",
                question="range(3)을 사용한 for문은 몇 번 반복되나요?",
                choices=["2번", "3번", "4번", "무한 반복"],
                answer=2,
                points=10
            ),
            Quiz(
                id="default-8",
                question="파이썬에서 함수를 정의할 때 사용하는 키워드는 무엇인가요?",
                choices=["func", "define", "return", "def"],
                answer=4,
                points=10
            ),
            Quiz(
                id="default-9",
                question="함수에서 값을 호출한 곳으로 돌려보낼 때 사용하는 키워드는 무엇인가요?",
                choices=["break", "print", "return", "input"],
                answer=3,
                points=10
            ),
            Quiz(
                id="default-10",
                question="클래스(class)는 무엇을 만들기 위한 설계도라고 볼 수 있나요?",
                choices=["객체", "반복문", "조건문", "파일"],
                answer=1,
                points=10
            ),
            Quiz(
                id="default-11",
                question="파일에 내용을 새로 저장할 때 open() 함수에서 주로 사용하는 모드는 무엇인가요?",
                choices=["r", "w", "a", "x"],
                answer=2,
                points=10
            )
        ]

    def is_default_quiz(self, quiz):
        """기본 문제인지 확인합니다."""
        return isinstance(quiz, Quiz) and isinstance(quiz.id, str) and quiz.id.startswith("default-")

    def normalize_text(self, text):
        """문장 비교용 정규화: 공백 제거 + 소문자 변환"""
        if not isinstance(text, str):
            text = str(text)
        return ''.join(text.split()).lower()

    def is_duplicate_question(self, question):
        """기본문제와 현재 저장된 문제에 같은 질문이 있는지 확인"""
        target = self.normalize_text(question)

        all_quizzes = self.default_quizzes + self.quizzes
        for quiz in all_quizzes:
            if self.normalize_text(quiz.question) == target:
                return True
        return False

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

    def add_quiz(self, question, choices, answer, hint="", explanation="", points=10):
        """새 문제를 추가합니다."""
        question = question.strip()

        if not question:
            print("문제는 비어 있을 수 없습니다.")
            return False

        if self.is_duplicate_question(question):
            print("기본문제와 같은 질문은 추가할 수 없습니다.")
            return False

        try:
            user_count = len([q for q in self.quizzes if not self.is_default_quiz(q)])
            new_quiz = Quiz(
                id=f"user-{user_count + 1}",
                question=question,
                choices=choices,
                answer=answer,
                hint=hint,
                explanation=explanation,
                points=points
            )
        except ValueError as e:
            print(f"문제 추가 실패: {e}")
            return False

        self.quizzes.append(new_quiz)
        self.save_state()
        print("문제가 추가되었습니다.")
        return True

    def show_quizzes(self):
        if not self.quizzes:
            print("저장된 퀴즈가 없습니다.")
            return

        for idx, quiz in enumerate(self.quizzes, start=1):
            tag = "[기본 문제]" if self.is_default_quiz(quiz) else "[추가 문제]"
            print(f"\n{tag} {idx}번 퀴즈")
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
                earned_points = max(0, quiz.points - 2)

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

        self.update_high_score()

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
                    if self.is_default_quiz(self.quizzes[idx - 1]):
                        print("기본 문제는 삭제할 수 없습니다.")
                        return

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
            if not isinstance(record, dict):
                continue

            print(f"\n[{i}번 기록]")
            print(f"날짜/시간: {record.get('played_at', '알 수 없음')}")
            print(f"푼 문제 수: {record.get('selected_count', 0)}")
            print(f"점수: {record.get('score', 0)} / {record.get('max_score', 0)}")
            print(f"힌트 사용 횟수: {record.get('hint_used_count', 0)}")

    def load_state(self):
        """기본 문제 + 저장된 사용자 문제를 합쳐서 불러옵니다."""
        saved_quizzes = []
        self.high_score = 0
        self.history = []

        if os.path.exists(self.file_name):
            try:
                with open(self.file_name, "r", encoding="utf-8") as file:
                    data = json.load(file)

                if isinstance(data, dict):
                    self.high_score = self._safe_int(data.get("high_score", 0), default=0)

                    quizzes_data = data.get("quizzes", [])
                    if isinstance(quizzes_data, list):
                        for idx, item in enumerate(quizzes_data, start=1):
                            try:
                                saved_quizzes.append(Quiz.from_dict(item))
                            except Exception:
                                print(f"저장된 퀴즈 {idx}번을 불러오지 못했습니다. 건너뜁니다.")

                    history_data = data.get("history", [])
                    self.history = history_data if isinstance(history_data, list) else []

                elif isinstance(data, list):
                    # 예전 형식 호환
                    for idx, item in enumerate(data, start=1):
                        try:
                            saved_quizzes.append(Quiz.from_dict(item))
                        except Exception:
                            print(f"저장된 퀴즈 {idx}번을 불러오지 못했습니다. 건너뜁니다.")

            except (json.JSONDecodeError, KeyError, ValueError, OSError):
                print("state.json 파일을 불러오는 중 오류가 발생했습니다.")
                saved_quizzes = []

        # 기본 문제 + 사용자 저장 문제 합치기, 같은 질문은 하나만 남김
        merged = []
        seen_questions = set()

        for quiz in self.default_quizzes + saved_quizzes:
            key = self.normalize_text(quiz.question)
            if key not in seen_questions:
                merged.append(quiz)
                seen_questions.add(key)

        self.quizzes = merged
    def backup_state_file(self):
        """state.json 백업을 만들고 최근 10개만 유지합니다."""
        if not os.path.exists(self.file_name):
            return

        backup_dir = os.path.dirname(self.file_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"state_backup_{timestamp}.json"
        backup_path = os.path.join(backup_dir, backup_name)

        try:
            shutil.copy2(self.file_name, backup_path)
        except OSError as e:
            print(f"백업 생성 중 오류가 발생했습니다: {e}")
            return

        # 최근 10개만 유지
        try:
            backups = [
                os.path.join(backup_dir, f)
                for f in os.listdir(backup_dir)
                if f.startswith("state_backup_") and f.endswith(".json")
            ]
            backups.sort(key=os.path.getmtime, reverse=True)

            for old_backup in backups[10:]:
                try:
                    os.remove(old_backup)
                except OSError:
                    pass
        except OSError:
            pass
    def save_state(self):
        """
        사용자 추가 문제만 저장합니다.
        기본 문제는 코드에 내장되어 있으므로 state.json에 저장하지 않습니다.
        """
        user_quizzes = [quiz for quiz in self.quizzes if not self.is_default_quiz(quiz)]

        data = {
            "high_score": self.high_score,
            "quizzes": [quiz.to_dict() for quiz in user_quizzes],
            "history": self.history
        }

        try:
            # 저장 전에 기존 파일 백업
            self.backup_state_file()

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

    def _safe_int(self, value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def run(self):
        while True:
            menu = self.input_menu()

            if menu == "1":
                question, choices, answer, hint, explanation, points = self.input_quiz_data()
                self.add_quiz(question, choices, answer, hint, explanation, points)

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
                print("프로그램을 종료합니다.")
                self.save_state()
                break

            else:
                print("올바른 메뉴 번호를 입력해주세요.")