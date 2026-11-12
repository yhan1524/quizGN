import json                                     # json 파일을 읽고 쓰는 기능
import os                                       # 파일 경로, 폴더존재여부, 폴더 생성 등
import sys                                      # 파이썬 시스템 기능
import signal                                   # 종료신호처리
import random                                   # 랜덤
import shutil                                   # 파일 복사
from datetime import datetime                   # 현재 날짜와 시간을가져옴, 백업 파일명 생성
from quiz import Quiz                           # Quiz 클래스를 가져옴


class QuizGame:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))          # 코드가 들어있는 폴더 위치 저장
        self.file_name = os.path.join(self.base_dir, "state.json")          # state.json 파일 경로 저장

        self.default_quizzes = self.default_questions()                     # 기본 문제를 불러와 저장
        self.reset_state()                                                  # 실제로 사용하는 퀴즈 목록

        self.load_state()                                                   # 저장된 데이터가 있으면 불러옴
        self.register_signal_handlers()                                     # 갑작스런 종료시 저장 후 종료

    @staticmethod
    def default_questions():                                                # 객체를 사용하지 않아 일반 함수처럼 동작
        """기본 문제 파일을 불러옵니다."""
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "default_questions.json"
        )

        if not os.path.exists(file_path):
            return []                                                       # 기본문제 파일이 없으면 종료

        try:
            with open(file_path, "r", encoding="utf-8") as f:               # json 형식 데이터를 파이썬 데이터로 변환
                data = json.load(f)

            return [
                Quiz(
                    id=f"default-{idx}",
                    question=item.get("question", ""),
                    choices=item.get("choices", []),
                    answer=item.get("answer", 1),
                    hint=item.get("hint", ""),
                    explanation=item.get("explanation", ""),
                    points=item.get("points", 10),
                )
                for idx, item in enumerate(data, start=1)
            ]
        except (json.JSONDecodeError, OSError, TypeError, ValueError):     # 에러 발생시 빈리스트 반환
            return []

    def reset_state(self):
        self.quizzes = list(self.default_quizzes)
        self.high_score = 0
        self.history = []
        self.score = 0

    def _user_quizzes(self):
        return [q for q in self.quizzes if not self.is_default_quiz(q)]     # 사용자 문제만 골라냄, 파일저장시 사용

    def _next_user_quiz_id(self):
        return f"user-{len(self._user_quizzes()) + 1}"                      # 새 퀴즈의 id 부여

    def is_default_quiz(self, quiz):                                        # 기본문제 판단(삭제방지, 저장제외)
        return isinstance(quiz, Quiz) and isinstance(quiz.id, str) and quiz.id.startswith("default-")

    def normalize_text(self, text):                                         # 비교용 정규화, 문장정리
        if not isinstance(text, str):
            text = str(text)
        return "".join(text.split()).lower()

    def is_duplicate_question(self, question):                              # 중복질문 확인
        target = self.normalize_text(question)                      
        return any(self.normalize_text(q.question) == target for q in self.quizzes)

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
        question = input("문제를 입력하세요(0: 돌아가기): ").strip()
        if question == "0":
            print("퀴즈 추가를 취소하고 돌아갑니다.")
            return None

        choices = []
        for i in range(1, 5):
            choice = input(f"{i}번 선택지를 입력하세요(0: 돌아가기): ").strip()
            if choice == "0":
                print("퀴즈 추가를 취소하고 돌아갑니다.")
                return None
            choices.append(choice)

        answer_input = input("정답 번호(1~4)를 입력하세요(0: 돌아가기): ").strip()
        if answer_input == "0":
            print("퀴즈 추가를 취소하고 돌아갑니다.")
            return None
        if not answer_input.isdigit() or not (1 <= int(answer_input) <= 4):
            print("정답은 1~4 사이의 숫자여야 합니다.")
            return None
        answer = int(answer_input)

        hint = input("힌트를 입력하세요(선택): ").strip()
        explanation = input("해설을 입력하세요(선택): ").strip()

        points_input = input("점수를 입력하세요(기본값 10): ").strip()
        if points_input:
            if not points_input.isdigit():
                print("점수는 숫자만 입력하세요.")
                return None
            points = int(points_input)
        else:
            points = 10

        return question, choices, answer, hint, explanation, points

    def input_answer(self, quiz):
        while True:
            ans = input("정답(1-4) 또는 h(힌트): ").strip().lower()

            if ans == "h":
                print(f"힌트: {quiz.hint}" if quiz.hint else "힌트가 없습니다.")
                continue

            if ans.isdigit() and 1 <= int(ans) <= 4:
                return int(ans)

            print("1~4 사이의 숫자만 입력해주세요.")

    def add_quiz(self, question, choices, answer, hint="", explanation="", points=10):      # 입력받은 문제를 저장
        if self.is_duplicate_question(question):
            print("같은 질문은 추가할 수 없습니다.")
            return False

        try:
            quiz = Quiz(
                id=self._next_user_quiz_id(),
                question=question,
                choices=choices,
                answer=answer,
                hint=hint,
                explanation=explanation,
                points=points,
            )
        except (TypeError, ValueError) as e:
            print(f"퀴즈 추가 실패: {e}")
            return False

        self.quizzes.append(quiz)               # 기존문제에 뒤로 이어서 추가
        self.save_state()
        print("문제가 추가되었습니다.")
        return True

    def show_quizzes(self):
        if not self.quizzes:
            print("저장된 퀴즈가 없습니다.")
            return

        for idx, quiz in enumerate(self.quizzes, start=1):
            tag = "[기본]" if self.is_default_quiz(quiz) else "[추가]"
            print(f"\n{tag} {idx}번 퀴즈")
            quiz.display()

    def show_history(self):
        if not self.history:
            print("기록이 없습니다.")
            return

        print("\n=== 점수 기록 ===")
        print(f"최고점: {self.high_score}")

        for item in self.history:
            if isinstance(item, dict):
                print(f"[{item.get('played_at', '기록 없음')}] 점수: {item.get('score', 0)}")

    def play_quiz(self):
        if not self.quizzes:
            print("출제할 퀴즈가 없습니다.")
            return

        count_in = input(f"몇 문제를 풀까요? (1~{len(self.quizzes)}): ").strip()
        if not count_in.isdigit() or not (1 <= int(count_in) <= len(self.quizzes)):
            print("올바른 숫자를 입력하세요.")
            return

        self.score = 0
        selected = random.sample(self.quizzes, int(count_in))

        for idx, quiz in enumerate(selected, 1):
            print(f"\n[{idx}번 문제]")
            quiz.display()

            user_answer = self.input_answer(quiz)
            if quiz.check_answer(user_answer):
                print("정답입니다!")
                self.score += quiz.points
            else:
                print(f"오답입니다. 정답은 {quiz.answer}번입니다.")

        print(f"\n최종 점수: {self.score}")
        self.update_high_score()
        self.history.append({
            "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "score": self.score
        })
        self.save_state()

    def delete_quiz(self):
        if not self.quizzes:
            print("삭제할 퀴즈가 없습니다.")
            return

        while True:
            self.show_quizzes()
            idx_in = input("삭제할 퀴즈 번호를 입력하세요 (0: 돌아가기): ").strip()

            if idx_in == "0":
                print("삭제를 취소하고 돌아갑니다.")
                return

            if not idx_in.isdigit():
                print("숫자를 입력해주세요.")
                continue

            idx = int(idx_in) - 1
            if not (0 <= idx < len(self.quizzes)):
                print("올바른 번호를 입력해주세요.")
                continue

            if self.is_default_quiz(self.quizzes[idx]):
                print("기본 문제는 삭제할 수 없습니다.")
                continue

            removed = self.quizzes.pop(idx)
            print(f"'{removed.question}' 삭제 완료.")
            self.save_state()
            return

    def load_state(self):
        self.reset_state()

        if not os.path.exists(self.file_name):
            return

        try:
            with open(self.file_name, "r", encoding="utf-8") as f:
                data = json.load(f)

            for q in data.get("quizzes", []):
                try:
                    self.quizzes.append(Quiz.from_dict(q))
                except (TypeError, ValueError, KeyError):
                    continue

            self.high_score = data.get("high_score", 0)

            self.history = data.get("history", [])
            if not isinstance(self.history, list):
                self.history = []

        except (json.JSONDecodeError, OSError, TypeError, ValueError) as e:
            print(f"저장된 데이터를 불러오는 중 문제가 발생했습니다: {e}")
            self.reset_state()

    def backup_state_file(self):
        if not os.path.exists(self.file_name):
            return

        backup_dir = os.path.join(os.path.dirname(self.file_name), "backups")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_path = os.path.join(backup_dir, f"state_backup_{timestamp}.json")

        try:
            shutil.copy2(self.file_name, backup_path)

            backups = [
                os.path.join(backup_dir, f)
                for f in os.listdir(backup_dir)
                if f.startswith("state_backup_") and f.endswith(".json")
            ]
            backups.sort(key=os.path.getmtime, reverse=True)

            for old in backups[10:]:
                os.remove(old)
        except OSError as e:
            print(f"백업 실패: {e}")

    def save_state(self):
        data = {
            "high_score": self.high_score,
            "quizzes": [q.to_dict() for q in self._user_quizzes()],
            "history": self.history
        }

        try:
            self.backup_state_file()
            with open(self.file_name, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print("데이터가 저장되었습니다.")
        except OSError as e:
            print(f"저장 오류: {e}")

    def update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            print("최고점 갱신!")

    def handle_exit_signal(self, signum, frame):
        self.save_state()
        sys.exit(0)

    def register_signal_handlers(self):
        signal.signal(signal.SIGINT, self.handle_exit_signal)

    def run(self):
        while True:
            menu = self.input_menu()

            if menu == "1":
                quiz_data = self.input_quiz_data()
                if quiz_data is not None:
                    self.add_quiz(*quiz_data)
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
                print("종료합니다.")
                break
            else:
                print("잘못된 선택입니다.")


if __name__ == "__main__":
    game = QuizGame()
    game.run()