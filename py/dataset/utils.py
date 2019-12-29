import subprocess

import imgaug.augmenters as iaa
import numpy as np

from enum import Enum
from PIL import Image, ImageDraw, ImageFont
from typing import NamedTuple, Tuple, List

FONTNAMES = subprocess.run(
    "fc-list :lang=en | sed -r -e 's/^(.+): .*$/\\1/g'",
    stdout=subprocess.PIPE,
    shell=True).stdout.decode("utf-8").strip().split("\n")

CUSTOM_FONTS = subprocess.run(
    "fc-list | sed -r -e 's/^(.+): .*$/\\1/g' | grep custom",
    stdout=subprocess.PIPE,
    shell=True).stdout.decode("utf-8").strip().split("\n")

FONTNAMES += CUSTOM_FONTS

with open("/usr/share/dict/words") as f:
    WORDS = f.read().splitlines()

AUGMENTOR = iaa.Sequential([
    iaa.OneOf([iaa.GaussianBlur(
        (0, 1.0)), iaa.AverageBlur(k=(1, 2))]),
    iaa.Sharpen(alpha=(0, 1.0), lightness=(0.75, 1.5)),
    iaa.Emboss(alpha=(0, 1.0), strength=(0, 2.0)),
    iaa.Dropout((0.01, 0.03), per_channel=0.1),
    iaa.Add((-10, 10), per_channel=0.5),
    iaa.OneOf([
        iaa.Multiply((0.5, 1.5), per_channel=0.5),
        iaa.FrequencyNoiseAlpha(
            exponent=(-4, 0),
            first=iaa.Multiply((0.5, 1.5), per_channel=True),
            second=iaa.ContrastNormalization((0.5, 2.0)))
    ]),
],
                           random_order=True)


class LineState(Enum):
    START = 0
    HEADLINE = 1
    NORMAL = 2
    LIST = 3
    COUNTING = 4
    BLANK = 5


class InlineState(Enum):
    START = 0
    NORMAL = 1
    BOLD = 2
    ITALICK = 3
    URL = 4
    BLANK = 5
    END = 6


LINE_TRANSITION = np.array(
    [[0.0, 0.8, 0.2, 0.0, 0.0, 0.0],
     [0.0, 0.05, 0.65, 0.1, 0.1, 0.1],
     [0.0, 0.1, 0.6, 0.1, 0.1, 0.1],
     [0.0, 0.1, 0.1, 0.75, 0.0, 0.05],
     [0.0, 0.1, 0.1, 0.0, 0.75, 0.05],
     [0.0, 0.1, 0.6, 0.1, 0.1, 0.1]]
)

INLINE_TRANSITION = {
    LineState.HEADLINE: np.array([
        [0.0, ]
    ])
}


class TextBox(NamedTuple):
    text: str
    xmin: int
    ymin: int
    xmax: int
    ymax: int


def choose_font() -> str:
    return np.random.choice(FONTNAMES)


def choose_word() -> str:
    return np.random.choice(WORDS)


class MarkDownText:
    initial_headline_level = 1

    def __init__(self):
        self.headline_level = self.initial_headline_level
        self.current_line = 0
        self.last_state = LineState.START
        self.counting = 1

    def generate(self):
        self.current_line += 1
        state = LineState(np.random.choice(
            np.arange(6),
            p=LINE_TRANSITION[self.last_state.value]))
        if self.last_state == LineState.COUNTING and \
                state != LineState.COUNTING:
            self.counting = 1
        self.last_state = state

        if state == LineState.BLANK:
            return []
        elif state == LineState.HEADLINE:
            n_words = np.random.choice([1, 2, 3, 4, 5, 6])
            texts = []
            for _ in range(n_words):
                word = choose_word()
                fontsize = np.random.randint(25, 48)
                fontname = choose_font()
                font = ImageFont.truetype(fontname, fontsize)
                texts.append((word, font))
            return texts
        elif state == LineState.NORMAL:
            n_words = np.random.choice([5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
            texts = []
            for _ in range(n_words):
                word = choose_word()
                fontsize = np.random.randint(15, 25)
                fontname = choose_font()
                font = ImageFont.truetype(fontname, fontsize)
                texts.append((word, font))
            return texts
        elif state == LineState.LIST:
            n_words = np.random.choice(np.arange(3, 12))
            fontsize = np.random.randint(15, 25)
            fontname = choose_font()
            font = ImageFont.truetype(fontname, fontsize)
            texts = [("*", font)]
            for _ in range(n_words):
                word = choose_word()
                fontsize = np.random.randint(15, 25)
                fontname = choose_font()
                font = ImageFont.truetype(fontname, fontsize)
                texts.append((word, font))
            return texts
        elif state == LineState.COUNTING:
            n_words = np.random.choice(np.arange(3, 12))
            fontsize = np.random.randint(15, 25)
            fontname = choose_font()
            font = ImageFont.truetype(fontname, fontsize)
            texts = [(f"{self.counting}.", font)]
            self.counting += 1
            for _ in range(n_words):
                word = choose_word()
                fontsize = np.random.randint(15, 25)
                fontname = choose_font()
                font = ImageFont.truetype(fontname, fontsize)
                texts.append((word, font))
            return texts


def generate(width: int, height: int,
             noise: bool = True) -> Tuple[Image.Image, List[TextBox]]:
    image = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    used_pixel_map = np.zeros((height, width), dtype=np.bool)
    retry_count = 0
    boxes: List[TextBox] = []

    while retry_count < 10:
        retry_count += 1
        fontname = choose_font()
        fontsize = np.random.randint(15, 32)
        font = ImageFont.truetype(fontname, fontsize)
        text = choose_word()
        textsize_x, textsize_y = draw.textsize(text, font=font)
        if width <= textsize_x or height <= textsize_y:
            continue

        x = np.random.randint(0, width - textsize_x)
        y = np.random.randint(0, height - textsize_y)
        used_pixel_count = np.sum(
            used_pixel_map[y:y + textsize_y, x:x + textsize_x])
        if used_pixel_count > 0:
            continue

        retry_count = 0
        used_pixel_map[y:y + textsize_y, x:x + textsize_x] = True
        draw.text((x, y), text, fill=(0, 0, 0), font=font)
        boxes.append(
            TextBox(
                text=text,
                xmin=x,
                ymin=y,
                xmax=x + textsize_x,
                ymax=y + textsize_y))

        if np.sum(used_pixel_map) > np.random.random() * width * height * 0.5:
            break

    if noise:
        img = AUGMENTOR.augment_image(np.asarray(image))
        image = Image.fromarray(img)
    return image, boxes


def generate_markdown_like_image(width: int,
                                 height: int,
                                 n_lines: int = 35,
                                 noise: bool = True
                                 ) -> Tuple[Image.Image, List[TextBox]]:
    image = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    used_pixel_map = np.zeros((height, width), dtype=np.bool)
    boxes: List[TextBox] = []

    line_height = height // n_lines
    markdown = MarkDownText()

    for i in range(n_lines):
        texts = markdown.generate()
        head_x = np.random.randint(0, 10)
        for text, font in texts:
            head_y = i * line_height + np.random.randint(0, 10)
            textsize_x, textsize_y = draw.textsize(text, font)
            if (head_x + textsize_x > width) or (head_y + textsize_y > height):
                break
            used_pixel_map[
                head_x: head_x + textsize_x,
                head_y: head_y + textsize_y
            ] = True
            draw.text((head_x, head_y), text, fill=(0, 0, 0), font=font)
            boxes.append(
                TextBox(
                    text=text,
                    xmin=head_x,
                    ymin=head_y,
                    xmax=head_x + textsize_x,
                    ymax=head_y + textsize_y
                )
            )
            head_x += textsize_x + np.random.randint(5, 15)

    if noise:
        img = AUGMENTOR.augment_image(np.asarray(image))
        image = Image.fromarray(img)
    return image, boxes
