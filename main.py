from quiz_game import QuizGame


def main():
    game = QuizGame()
    try:
        game.run()
    except KeyboardInterrupt:
        game.handle_exit_signal(None, None)


if __name__ == "__main__":
    main()