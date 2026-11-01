# chiparse.py
class ChiParseError(Exception):
    pass


def parse_error(key, symbol, value, metadata, index):
    if not symbol:
        raise ChiParseError(f'"=" is missing on line {index}')
    elif key.strip() in metadata:
        raise ChiParseError(f"Duplicate key on line {index}")
    elif key.strip() == "":
        raise ChiParseError(f"Empty key on line {index}")
    else:
        metadata[key.strip()] = value.strip()
        return metadata


def parse(file: str) -> dict:
    in_metadata = False
    metadata = {}
    body = ""
    lines = file.splitlines(keepends=True)
    for index, line in enumerate(lines, start=1):
        if line.strip() == "[metadata]":
            in_metadata = True
        elif line.strip().startswith("["):
            in_metadata = False
            body = "".join(lines[index - 1 :])
            break
        elif in_metadata and line.strip():
            key, symbol, value = line.partition("=")
            parse_error(key, symbol, value, metadata, index)
    return {"metadata": metadata, "body": body}


if __name__ == "__main__":
    test = "[metadata]\ntitle = Test\nartist = Someone\n[lyrics]\nhello\n"
    result = parse(test)
    print(result)
