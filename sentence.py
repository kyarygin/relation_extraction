class Sentence(str):
    """docstring for Sentence"""
    def __init__(self, sentence):
        self.text = sentence

    def __repr__(self):
        return self.text


    # def is_good(self):
    #     if sum(map(bool, [self.bacteria, self.nutrients, self.diseases])) >= 2:
    #         return True
    #     else:
    #         return False
