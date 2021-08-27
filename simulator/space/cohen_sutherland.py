# modified version
# https://github.com/scivision/lineclipping-python-fortran/blob/main/pylineclip/__init__.py

INSIDE, LEFT, RIGHT, LOWER, UPPER = 0, 1, 2, 4, 8


def _getclip(
    xa: float, ya: float, xmin: float, xmax: float, ymin: float, ymax: float
) -> int:
    p = INSIDE  # default is inside
    # consider x
    if xa < xmin:
        p |= LEFT
    elif xa > xmax:
        p |= RIGHT
    # consider y
    if ya < ymin:
        p |= LOWER  # bitwise OR
    elif ya > ymax:
        p |= UPPER  # bitwise OR
    return p


def cohen_sutherland(
    xmin: float,
    ymax: float,
    xmax: float,
    ymin: float,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> bool:

    # check for trivially outside lines
    k1 = _getclip(x1, y1, xmin, xmax, ymin, ymax)
    k2 = _getclip(x2, y2, xmin, xmax, ymin, ymax)

    # examine non-trivially outside points
    # if both points are inside box (0000) , ACCEPT trivial whole line in box
    while (k1 | k2) != 0:
        # if line trivially outside window, REJECT
        if (k1 & k2) != 0:
            return False
        # if at least one inside:
        if k1 == INSIDE or k2 == INSIDE:
            return True

        # non-trivial case, at least one point outside window
        # this is not a bitwise or, it's the word "or"
        opt = k1 or k2  # take first non-zero point, short circuit logic
        if opt & UPPER:  # these are bitwise ANDS
            x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
            y = ymax
        elif opt & LOWER:
            x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
            y = ymin
        elif opt & RIGHT:
            y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
            x = xmax
        elif opt & LEFT:
            y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
            x = xmin
        else:
            raise RuntimeError("Undefined clipping state")

        if opt == k1:
            x1, y1 = x, y
            k1 = _getclip(x1, y1, xmin, xmax, ymin, ymax)
        elif opt == k2:
            x2, y2 = x, y
            k2 = _getclip(x2, y2, xmin, xmax, ymin, ymax)

    return True
