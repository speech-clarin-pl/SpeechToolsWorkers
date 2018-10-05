id = 0


def next():
    global id
    id += 1
    return id


def reset():
    global id
    id = 0
