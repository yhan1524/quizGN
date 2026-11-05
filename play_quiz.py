class Quiz:
    def __init__(self, question, choices, answer):
        self.question = question
        self.choices = choices
        self.answer = answer  # 정답 번호(1부터 시작)


class QuizGame:
    def __init__(self):
        self.quizzes = []

    def play_quiz(self):
        # 1. 퀴즈가 없는 경우 처리
        if not self.quizzes:
            print("\n출제할 퀴즈가 없습니다.")
            return

        score = 0
        total = len(self.quizzes)

        print("\n=== 퀴즈 시작 ===")

        # 2. 저장된 퀴즈를 순서대로 출제
        for i, quiz in enumerate(self.quizzes, start=1):
            print(f"\n[{i}번 문제] {quiz.question}")

            for idx, choice in enumerate(quiz.choices, start=1):
                print(f"{idx}. {choice}")

            # 3. 사용자 정답 입력
            while True:
                user_input = input("정답 번호를 입력하세요: ").strip()

                if not user_input.isdigit():
                    print("숫자로 입력해주세요.")
                    continue

                user_answer = int(user_input)

                if user_answer < 1 or user_answer > len(quiz.choices):
                    print("보기 범위 안에서 입력해주세요.")
                    continue

                break

            # 4. 정답/오답 판별
            if user_answer == quiz.answer:
                print("정답입니다!")
                score += 1
            else:
                print(f"오답입니다. 정답은 {quiz.answer}번입니다.")

        # 5. 모든 문제 풀이 후 결과 출력
        print("\n=== 퀴즈 결과 ===")
        print(f"총 문제 수: {total}")
        print(f"맞힌 개수: {score}")
        print(f"틀린 개수: {total - score}")