import argparse

from python_template_repository.dummy import Dummy


def main() -> None:
    """Dummy script entry point.

    Answers important life questions.
    """
    p = argparse.ArgumentParser(description="Dummy example executable script.")
    p.add_argument(
        "--no-universe-answer",
        dest="no_universe_answer",
        action="store_true",
        default=False,
        help="Set this flag if don't want to know"
        + " the veritable answer of the universe",
    )
    p.add_argument(
        "--no-zen-python",
        dest="no_zen_python",
        action="store_true",
        default=False,
        help="Set this flag if don't want to know"
        + " what is PEP 20 -- The Zen of Python",
    )
    args = p.parse_args()

    dummy = Dummy()

    if not (args.no_universe_answer):
        a = 40
        b = 2
        print("Universe answer from " + dummy.name + ":")
        print("{} + {} = {}".format(a, b, dummy.addition(a, b)))
        print()

    if not (args.no_zen_python):
        print(dummy.zen())


if __name__ == "__main__":
    main()
