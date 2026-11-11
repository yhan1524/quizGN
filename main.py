from quiz_game import QuizGame          # quiz_game.py 파일 안에 있는 QuizGame 클래스를 가져옴


def main():
    game = QuizGame()
    try:
        game.run()
    except KeyboardInterrupt:
        game.handle_exit_signal(None, None)         # KeyboardInterrupt 예외 처리


if __name__ == "__main__":
    main()
