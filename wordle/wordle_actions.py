import re

# regex that holds the user input for wordle
WORDLE_HEADER_RE = re.compile(r"\bWordle\s+(\d+)\s+([1-6Xx])/6\b", re.IGNORECASE)


def parse_wordle_share(text: str):
    # parses the wordle and returns the number puzzle number and the number of attempts
    m = WORDLE_HEADER_RE.search(text.replace(",",""))
    if not m: 
        return None
    puzzle = int(m.group(1))
    a = m.group(2).upper()
    # if the number of attempts isn't 1-6, then assign the value 7 to attempts
    attempts = None if a == "X" else int(a)
    return puzzle, attempts