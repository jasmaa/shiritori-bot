import requests
import json

class Game:
    """Shiritori Game
    """
    
    def __init__(self):
        self.last_word = None
        self.word_set = set()
        self.is_alive = True

    def add_word(self, word):
        """Adds word to chain
        """
        if self.is_alive:
            reading_data = self.get_word_data(word)
            if reading_data:
                self.last_word = reading_data
                self.word_set.add(reading_data['word'])
            else:
                self.is_alive = False

    def get_word_data(self, word):
        """Gets and validates word
        """
        r = requests.get(f"https://jisho.org/api/v1/search/words?keyword={word}")
        data = json.loads(r.text)

        # Check if word is in Jisho
        if len(data['data']) > 0:
            word_data = data['data'][0]

            # Get reading of word
            target = ""
            for possible in word_data['japanese']:
                if ('word' in possible.keys() and possible['word'] == word) or possible['reading'] == word:
                    target = possible
                    break

            if len(target) > 0:
                # Check if word ends in n
                if target['reading'][-1] == "ん": # make it work with katakana
                    raise Exception("End with n")
                # Check if word on chain
                if target['word'] in self.word_set:
                    raise Exception("Word already on chain")
                # Check if word fits chain
                if len(self.word_set) != 0 and target['reading'][0] != self.last_word['reading'][-1]:
                    raise Exception("Word does not fit on chain")
                    
                return target
                    
        raise Exception("Word is invalid")

g = Game()
while True:
    g.add_word(input("Enter word: "))
    print(g.last_word, g.is_alive)
