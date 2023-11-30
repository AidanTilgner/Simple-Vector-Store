import sys
import shutil
import click

def get_terminal_width() -> int:
    """
    Returns the width of the terminal in characters.
    """
    return shutil.get_terminal_size().columns

def update_progress(progress: float, message: str = "") -> None:
    """
    Displays or updates a console progress bar.

    Accepts a float between 0 and 1. Any int will be converted to a float.
    """
    bar_length = 50  # Fixed length for the progress bar

    status = ""
    if progress < 0:
        progress = 0
        status = "Halt"
    elif progress >= 1:
        progress = 1
        status = "Done"

    block = int(round(bar_length * progress))
    progress_bar = f"Progress: [{'█' * block}{' ' * (bar_length - block)}] {round(progress * 100, 2)}% {status}"

    # Construct the full output with message
    full_output = f"{progress_bar}\n{message}"

    # Clear the line and then print the new output
    click.echo("\r" + " " * (len(full_output) + 10), nl=False)  # Clear with extra spaces
    click.echo("\r" + full_output, nl=False)  # Carriage return to go back to line start

    # If this still doesn't clear properly, increase the number of spaces used to clear the line
