from PIL import Image, ImageDraw, ImageFont
import sys
from Ocr_Sol import OCRSolver
import os

CHARACTER_WIDTH = 14
CHARACTER_HEIGHT = 25


def load_letters(fname):
    im = Image.open(fname)
    px = im.load()
    (x_size, y_size) = im.size
    result = []
    for x_beg in range(0, int(x_size / CHARACTER_WIDTH) * CHARACTER_WIDTH, CHARACTER_WIDTH):
        result += [["".join(['*' if px[x, y] < 1 else ' ' for x in range(x_beg, x_beg + CHARACTER_WIDTH)]) for y in
                    range(0, CHARACTER_HEIGHT)], ]
    return result


def load_training_letters(fname):
    TRAIN_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789(),.-!?\"' "
    letter_images = load_letters(fname) 
    save_character_images(letter_images, "output_characters")
    return {TRAIN_LETTERS[i]: letter_images[i] for i in range(0, len(TRAIN_LETTERS))}


def save_character_images(test_letters, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for i, char in enumerate(test_letters):
        char_img = Image.new('RGB', (CHARACTER_WIDTH, CHARACTER_HEIGHT), color='white')
        draw = ImageDraw.Draw(char_img)
        for y, row in enumerate(char):
            for x, pixel in enumerate(row):
                if pixel == '*':
                    draw.point((x, y), fill='black')

        char_img.save(os.path.join(output_dir, f'char_{i}.png'))
test_img_fname = sys.argv[1]
train_img_fname = "Img-Train.png"
train_txt_fname = "Text-Train.txt"
train_letters = load_training_letters(train_img_fname)
test_letters = load_letters(test_img_fname)
save_character_images(test_letters, "output_Data")

solver = OCRSolver(train_letters, test_letters, train_txt_fname)
solver.simplified()
