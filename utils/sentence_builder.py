class SentenceBuilder:
    def __init__(self):
        self.words = []

    def add(self, word):
        if len(self.words) == 0 or self.words[-1] != word:
            self.words.append(word)

    def reset(self):
        self.words = []

    def get_sentence(self):
        return " ".join(self.words)
