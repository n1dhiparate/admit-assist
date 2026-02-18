import os

def load_brochure():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", "admission_brochure.txt")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def retrieve_context(query):
    text = load_brochure()
    lines = text.split("\n")

    query = query.lower()

    for line in lines:
        if any(word in line.lower() for word in query.split()):
            return line

    return ""
