def words_line(text: str, pos: tuple[int, int] = (0, 0)):
    y = pos[1]
    for i, letter in enumerate(text):
        x = pos[0] + i
        yield (x, y), letter


def words_bound(text: str, size: tuple[int, int]):
    pos = (0, 0)
    while len(text) > 0 and pos[1] < size[1]:
        cut = size[0] - pos[0]
        word = text[:cut]
        text = text[cut:]
        yield from words_line(word, pos)
        if pos[0] + len(word) >= size[0]:
            pos = (0, pos[1] + 1)
        else:
            pos = (pos[0] + len(word), pos[1])


def scroll(text: str, window: int, start: int = 0):
    """yields views starting from empty view, shifts to left
    returns number of views yield

    Parameters:
    text: str
    window: int
        length of the view
    start: int = 0
        pass value < window to start from partially filled view
    """
    text = " " * window + text
    length = 0
    for pos in range(start, len(text) - window + 1):
        yield text[pos : pos + window]
        length += 1
    return length


def reveal(text: str, start: int = 0):
    d = len(text)
    for pos in range(start, d + 1):
        # yield text[0: pos] + ' ' * (d - pos)
        yield text[0:pos]
    return d
