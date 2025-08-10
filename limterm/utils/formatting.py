import time


def format_elapsed_since(start_time: float) -> str:
    """Return HH:MM:SS.sss timestamp string for elapsed time since start_time."""
    elapsed = time.time() - start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = elapsed % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f} "
