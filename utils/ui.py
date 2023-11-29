import shutil
import sys


def get_terminal_width():
    """Get the current width of the terminal."""
    return shutil.get_terminal_size().columns


def update_progress(progress: float, message: str = "") -> None:
    """
    Displays or updates a console progress bar.

    Accepts a float between 0 and 1. Any int will be converted to a float.
    """
    term_width = get_terminal_width()
    bar_length = max(20, term_width - 30)  # Adjust bar length based on terminal width

    status = ""
    if progress < 0:
        progress = 0
        status = "Halt"
    elif progress >= 1:
        progress = 1
        status = "Done"

    block = int(round(bar_length * progress))

    sys.stdout.write("\r" + " " * term_width)  # Clear line
    sys.stdout.flush()

    progress_bar = f"Progress: [{'█' * block}{' ' * (bar_length - block)}] {round(progress * 100, 2)}% {status}"

    sys.stdout.write("\r" + progress_bar)
    sys.stdout.flush()

    sys.stdout.write("\n" + " " * term_width)  # Clear message line
    sys.stdout.write("\r" + message)  # Write new message
    sys.stdout.flush()

    # Move the cursor back up to the start of the progress bar line
    sys.stdout.write("\033[A\r")  # Move cursor up and to the beginning
    sys.stdout.flush()

