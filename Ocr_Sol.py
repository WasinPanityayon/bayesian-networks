from collections import defaultdict
import math
import sys

TRAIN_LETTERS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789(),.-!?\"' ")
CHARACTER_WIDTH = 14
CHARACTER_HEIGHT = 25
max_val = 10000000.0  # Maximum value
min_val = sys.float_info.epsilon  # Smallest possible value


class OCRSolver:
    def __init__(self, train_letters, test_letters, train_txt_fname):
        self.train_letters = train_letters
        self.test_letters = test_letters
        self.init_prob = dict()
        self.char_prob = dict()
        for char in TRAIN_LETTERS:
            self.char_prob[char] = min_val
        self.trans_prob = defaultdict(dict)
        for row_char in TRAIN_LETTERS:
            for col_char in TRAIN_LETTERS:
                self.trans_prob[row_char][col_char] = min_val
        self.emit_prob = defaultdict(dict)
        self.train(train_txt_fname)


    @staticmethod
    def normalize_dict(dict_to_normalize):
        total_log = math.log(sum(dict_to_normalize.values()))
        for key, val in dict_to_normalize.items():
            dict_to_normalize[key] = max_val if val < 1 else total_log - math.log(val)

    def compute_emission(self):
        def match_grids(grid1, grid2):
            matches = 0
            for row1, row2 in zip(grid1, grid2):
                for ch1, ch2 in zip(row1, row2):
                    if ch1 == ch2:
                        matches += 1
            return matches
        total_pixels = CHARACTER_WIDTH * CHARACTER_HEIGHT

        for curr_index, test_letter in enumerate(self.test_letters):
            for train_letter, train_letter_grid in self.train_letters.items():
                matched = match_grids(test_letter, train_letter_grid)
                unmmatched = total_pixels - matched
                match_prob = (matched + 0.0) / total_pixels
                prob = (match_prob ** matched) * ((1 - match_prob) ** unmmatched)
                self.emit_prob[curr_index][train_letter] = max_val if prob == 0 else -math.log(prob)

    def train(self, train_txt_fname):
        def clean_string(str_to_clean):
            str_to_clean = list(str_to_clean)
            idx = 0
            while idx < len(str_to_clean) - 1:
                curr_ch = str_to_clean[idx]
                next_ch = str_to_clean[idx + 1]
                if curr_ch not in TRAIN_LETTERS:
                    str_to_clean[idx] = ' '
                if next_ch not in TRAIN_LETTERS:
                    str_to_clean[idx + 1] = ' '
                if next_ch == ' ' and (curr_ch == '.' or curr_ch == ' '):
                    del str_to_clean[idx + 1]
                else:
                    idx += 1
            return str_to_clean

        # train() starts from here
        with open(train_txt_fname, 'r') as train_txt_file:
            train_text = clean_string(train_txt_file.read())
            is_initial_letter = True
            for index in range(0, len(train_text) - 1):
                curr_char = train_text[index]
                next_char = train_text[index + 1]

                if is_initial_letter:
                    if curr_char not in self.init_prob:
                        self.init_prob[curr_char] = 0
                    self.init_prob[curr_char] += 1
                    is_initial_letter = False

                if curr_char == '.':
                    is_initial_letter = True

                self.trans_prob[curr_char][next_char] += 1
                self.char_prob[curr_char] += 1

        self.normalize_dict(self.init_prob)

        self.normalize_dict(self.char_prob)

        for row_dict in self.trans_prob.values():

            self.normalize_dict(row_dict)

        self.compute_emission()

    def simplified(self):
        output_chars = []
        current_chars = ""
        for index, test_letter_grid in enumerate(self.test_letters):
            (best_ch, best_prob) = (None, sys.float_info.max)
            for ch, prob in self.emit_prob[index].items():
                curr_prob = prob + self.char_prob[ch]
                if curr_prob < best_prob:
                    print(current_chars + ch)
                    (best_ch, best_prob) = (ch, curr_prob)
            output_chars.append(best_ch)
            current_chars = "".join(output_chars)
        print ('Simple:', current_chars)
