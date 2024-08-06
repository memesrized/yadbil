from IPython.display import Markdown, display


# import string
# english_lowercase = set(string.ascii_lowercase)
russian_lowercase = set("".join(chr(i) for i in range(1072, 1104)))


def is_ru(word):
    if set(word).intersection(russian_lowercase):
        return "russian"
    else:
        return "english"


def is_word(word):
    return any(char.isalpha() for char in word)


def print_md(text):
    display(Markdown(text))
