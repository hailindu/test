def parse_pages_input(pages_input):
    pages = []
    tokens = pages_input.split(",")
    for token in tokens:
        token = token.strip()
        if "-" in token:
            try:
                start, end = token.split("-")
                pages.extend(range(int(start.strip()), int(end.strip()) + 1))
            except ValueError:
                continue
        elif token.isdigit():
            pages.append(int(token))
    return pages
