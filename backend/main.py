import sys

from orchestrator import Orchestrator


def main():

    # ========================================================
    # TARGET FILE
    # ========================================================

    if len(sys.argv) > 1:

        target_file = sys.argv[1]

    else:

        target_file = "example.json"


    print(
        f"[MAIN] Target configuration: {target_file}"
    )


    # ========================================================
    # CREATE ORCHESTRATOR
    # ========================================================

    orchestrator = Orchestrator()


    # ========================================================
    # START WORKFLOW
    # ========================================================

    orchestrator.run(
        target_file
    )


if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print(
            "\n[MAIN] Execution stopped by user."
        )

    except Exception as error:

        print()
        print(
            "=============================================="
        )
        print(
            "ORCHESTRATOR ERROR"
        )
        print(
            "=============================================="
        )

        print(
            f"{type(error).__name__}: {error}"
        )