import requests
import json
import regex as re
import jaconv

class ShiritoriException(Exception):
    """Illegal shiritori move
    """
    pass

class Game:
    """Shiritori Game
    """
    
    def __init__(self):
        self.last_word = None
        self.word_set = set()
        self.is_alive = True

    def copy(self):
        """Deep copies game
        """
        g = Game()
        g.last_word = self.last_word
        g.word_set = self.word_set.copy()
        g.is_alive = self.is_alive
        return g


    def add_word(self, word):
        """Adds word to chain
        """
        
        if self.is_alive:
            
            word_data = self.get_word_data(word)
            if word_data:
                self.last_word = word_data

                # Add word to set, otherwise default to add reading
                if 'word' in word_data.keys():
                    self.word_set.add(word_data['word'])
                else:
                    self.word_set.add(word_data['reading'])
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
            target = None
            for possible in word_data['japanese']:
                if ('word' in possible.keys() and possible['word'] == word) or ('reading' in possible.keys() and possible['reading'] == word):
                    target = possible
                    break
                
            # Validate and convert reading to hira
            if target and 'reading' in target.keys():
                target['reading'] = jaconv.kata2hira(target['reading'])
            else:
                raise ShiritoriException("Word is invalid")
            
            # Check if word ends in n
            if target['reading'][-1] == "ん":
                raise ShiritoriException("End with n")
                
            # Check if word on chain
            if ('word' in target.keys() and target['word'] in self.word_set) or target['reading'] in self.word_set:
                raise ShiritoriException("Word is already on the chain")
                
            # Check if word fits chain
            if len(self.word_set) != 0 and target['reading'][0] != self.last_word['reading'][-1]:
                raise ShiritoriException("Word does not fit on the chain")
                    
            return target
                    
        raise ShiritoriException("Word is invalid")


if __name__ == "__main__":
    g = Game()
    while True:
        g.add_word(input("Enter word: "))
        print(g.last_word)
