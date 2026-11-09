import json
import os
import sys
import signal
import random
import shutil
from datetime import datetime

# Quiz 클래스는 별도의 파일(quiz.py)에 정의되어 있다고 가정합니다.
try:
    from quiz import Quiz
except ImportError:
    # 테스트용 더미 클래스 (실제 실행 시 quiz.py가 필요합니다)
    class Quiz:
        def __init__(self, id, question, choices, answer, hint="", explanation="", points=10):
            self.id = id
            self.question = question
            self.choices = choices
            self.answer = answer
            self.hint = hint
            self.explanation = explanation
            self.points = points
        def display(self):
            print(f"\nQ: {self.question}")
            for i, c in enumerate(self.choices, 1):
                print(f"{i}. {c}")
        def check_answer(self, user_answer):
            return self.answer == user_answer
        def to_dict(self):
            return self.__dict__
        @classmethod
        def from_dict(cls, data):
            return cls(**data)

class QuizGame:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_name = os.path.join(self.base_dir, "state.json")

        # 기본 문제는 코드에 내장
        self.default_quizzes = self.default_questions()

        # 실제 실행 중 사용할 퀴즈 목록
        self.quizzes = []
        self.score = 0
        self.high_score = 0
        self.history = []

        self.load_state()
        self.register_signal_handlers()

    @staticmethod
    def default_questions():
        """기본 문제 파일을 로드합니다."""
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "default_questions.json")
        
        if not os.path.exists(file_path):
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            quizzes = []
            for idx, item in enumerate(data, start=1):
                quizzes.append(
                    Quiz(
                        id=f"default-{idx}",
                        question=item["question"],
                        choices=item["choices"],
                        answer=item["answer"],
                        hint=item.get("hint", ""),
                        explanation=item.get("explanation", ""),
                        points=item.get("points", 10)
                    )
                )
            return quizzes
        except (json.JSONDecodeError, OSError, KeyError):
            return []

    def is_default_quiz(self, quiz):
        """기본 문제인지 확인합니다."""
        return isinstance(quiz, Quiz) and isinstance(quiz.id, str) and quiz.id.startswith("default-")

    def normalize_text(self, text):
        """문장 비교용 정규화: 공백 제거 + 소문자 변환"""
        if not isinstance(text, str):
            text = str(text)
        return ''.join(text.split()).lower()

    def is_duplicate_question(self, question):
        """중복 질문 확인"""
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
        choices = [input(f"{i}번 선택지: ").strip() for i in range(1, 5)]

        while True:
            ans = input("정답 번호(1~4): ").strip()
            if ans.isdigit() and 1 <= int(ans) <= 4:
                answer = int(ans)
                break
            print("1~4 사이의 숫자를 입력해주세요.")

        hint = input("힌트(없으면 엔터): ").strip()
        explanation = input("해설(없으면 엔터): ").strip()
        points = input("문제 점수(기본 10점): ").strip()
        points = int(points) if points.isdigit() else 10

        return question, choices, answer, hint, explanation, points

    def add_quiz(self, question, choices, answer, hint="", explanation="", points=10):
        if not question:
            print("문제는 비어 있을 수 없습니다.")
            return False

        if self.is_duplicate_question(question):
            print("기본문제와 같은 질문은 추가할 수 없습니다.")
            return False

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
        self.quizzes.append(new_quiz)
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

    def play_quiz(self):
        if not self.quizzes:
            print("출제할 퀴즈가 없습니다.")
            return

        count_in = input(f"몇 문제를 풀까요? (1~{len(self.quizzes)}): ").strip()
        if not count_in.isdigit() or not (1 <= int(count_in) <= len(self.quizzes)):
            print("올바른 숫자를 입력하세요.")
            return
        
        count = int(count_in)
        selected = random.sample(self.quizzes, count)
        self.score = 0

        for idx, quiz in enumerate(selected, 1):
            print(f"\n[{idx}번 문제]")
            quiz.display()
            ans = input("정답(1-4) 또는 h(힌트): ").strip().lower()
            if ans == 'h' and quiz.hint:
                print(f"힌트: {quiz.hint}")
                ans = input("정답(1-4): ").strip()
            
            if ans.isdigit() and quiz.check_answer(int(ans)):
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
        self.show_quizzes()
        idx_in = input("삭제할 퀴즈 번호: ").strip()
        if idx_in.isdigit() and 1 <= int(idx_in) <= len(self.quizzes):
            idx = int(idx_in) - 1
            if self.is_default_quiz(self.quizzes[idx]):
                print("기본 문제는 삭제할 수 없습니다.")
            else:
                removed = self.quizzes.pop(idx)
                print(f"'{removed.question}' 삭제 완료.")
                self.save_state()

    def show_history(self):
        if not self.history:
            print("기록이 없습니다.")
            return
        print("\n=== 점수 기록 ===")
        for h in self.history:
            print(f"[{h.get('played_at')}] 점수: {h.get('score')}")

    def load_state(self):
        saved_quizzes = []
        if os.path.exists(self.file_name):
            try:
                with open(self.file_name, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.high_score = data.get("high_score", 0)
                self.history = data.get("history", [])
                for q_data in data.get("quizzes", []):
                    saved_quizzes.append(Quiz.from_dict(q_data))
            except:
                pass

        merged = []
        seen = set()
        for q in self.default_quizzes + saved_quizzes:
            key = self.normalize_text(q.question)
            if key not in seen:
                merged.append(q)
                seen.add(key)
        self.quizzes = merged

    def backup_state_file(self):
        """state.json을 별도의 'backups' 폴더에 백업하고 최근 10개만 유지합니다."""
        if not os.path.exists(self.file_name):
            return

        backup_dir = os.path.join(os.path.dirname(self.file_name), "backups")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"state_backup_{timestamp}.json")

        try:
            shutil.copy2(self.file_name, backup_path)
            
            # 10개 유지 로직
            backups = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) 
                       if f.startswith("state_backup_") and f.endswith(".json")]
            backups.sort(key=os.path.getmtime, reverse=True)
            for old in backups[10:]:
                os.remove(old)
        except OSError as e:
            print(f"백업 실패: {e}")

    def save_state(self):
        user_quizzes = [q for q in self.quizzes if not self.is_default_quiz(q)]
        data = {
            "high_score": self.high_score,
            "quizzes": [q.to_dict() for q in user_quizzes],
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
                self.add_quiz(*self.input_quiz_data())
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
