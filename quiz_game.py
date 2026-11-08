import json
import os
from quiz import Quiz


class QuizGame:
    def __init__(self):
        self.file_name = "state.json"
        self.backup_path = self.file_name + ".bak"
        self.temp_path = self.file_name + ".tmp"

        self.quizzes = []
        self.quiz_index_by_id = {}
        for quiz in quizzes:
            quiz_index_by_id[quiz.id] = quiz

        self.score = 0
        self.high_score = 0
        self.last_score = 0

        self.load_state()
        self.register_signal_handlers()
    def load_data(self):
        # 1순위: 원본 파일
        try:
            with open(self.file_name, "r", encoding="utf-8") as file:
                self.data = json.load(file)
                return
        except (json.JSONDecodeError, KeyError, ValueError, PermissionError, OSError):
            pass

        # 2순위: 백업 파일
        try:
            with open(self.backup_path, "r", encoding="utf-8") as file:
                self.data = json.load(file)
                print("원본 파일을 읽을 수 없어 백업 파일에서 복구했습니다.")
                return
        except (json.JSONDecodeError, KeyError, ValueError, PermissionError, OSError):
            pass

        # 3순위: 기본값
        self.data = []
        print("데이터 파일을 불러오지 못해 기본값으로 시작합니다.")

    def save_data(self):
        try:
            # 1. 임시 파일에 먼저 저장
            with open(self.temp_path, "w", encoding="utf-8") as file:
                json.dump(self.data, file, ensure_ascii=False, indent=4)

            # 2. 기존 원본이 있으면 백업 생성
            if os.path.exists(self.file_name):
                shutil.copy2(self.file_name, self.backup_path)

            # 3. 임시 파일을 원본으로 교체
            os.replace(self.temp_path, self.file_name)

        except PermissionError:
            print("원본 파일에 쓸 권한이 없습니다. 대체 경로에 저장을 시도합니다.")
            self.save_to_fallback()

        except OSError as e:
            print(f"파일 저장 중 오류가 발생했습니다: {e}")
            self.save_to_fallback()

    def save_to_fallback(self):
        try:
            fallback_path = os.path.join(tempfile.gettempdir(), "state_backup.json")

            with open(fallback_path, "w", encoding="utf-8") as file:
                json.dump(self.data, file, ensure_ascii=False, indent=4)

            print(f"대체 저장 완료: {fallback_path}")

        except OSError as e:
            print(f"대체 저장도 실패했습니다: {e}")

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

        return question, choices, answer

    def add_quiz(self):
        try:
            question, choices, answer = self.input_quiz_data()
            quiz = Quiz(question, choices, answer)
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

        score = 0
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
                score += 1
            else:
                print(f"오답입니다. 정답은 {quiz.answer}번입니다.")

        print("\n=== 결과 ===")
        print(f"총 문제 수: {total}")
        print(f"정답 수: {score}")
        print(f"오답 수: {total - score}")

    def save_state(self):
        data = [quiz.to_dict() for quiz in self.quizzes]

        with open(self.file_name, "w", encoding="utf-8") as file: #state에 저장
            json.dump(data, file, ensure_ascii=False, indent=4)

        print("state.json에 저장되었습니다.")

    def load_state(self):
        if not os.path.exists(self.file_name):
            self.quizzes = []
            return

        try:
            with open(self.file_name, "r", encoding="utf-8") as file: #state 불러오기
                data = json.load(file)
            self.quizzes = [Quiz.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError, ValueError):
            print("state.json 파일을 불러오는 중 오류가 발생했습니다.")
            self.quizzes = []

    def handle_exit_signal(self, signum, frame):
        print("\n종료 신호를 감지했습니다. 데이터를 저장합니다...")
        self.update_high_score()
        self.save_state()
        print("저장 후 안전하게 종료합니다.")
        sys.exit(0)

    def register_signal_handlers(self):
        signal.signal(signal.SIGINT, self.handle_exit_signal)

        # 환경에 따라 SIGTERM이 없을 수 있으므로 확인 후 등록
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

    def load_state(self):
        if not os.path.exists(self.file_name):
            self.high_score = 0
            return

        try:
            with open(self.file_name, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.high_score = data.get("high_score", 0)
        except (json.JSONDecodeError, OSError):
            self.high_score = 0

    def save_state(self):
        data = {
            "high_score": self.high_score
        }

        with open(self.file_name, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_state()
            print("최고점이 갱신되었습니다!")

    def end_game(self):
        print(f"이번 점수: {self.score}")
        print(f"현재 최고점: {self.high_score}")

        self.update_high_score()

        print(f"최종 최고점: {self.high_score}")