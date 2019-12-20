import subprocess

import imgaug.augmenters as iaa
import numpy as np

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
    iaa.AddToHueAndSaturation((-20, 20)),
    iaa.OneOf([
        iaa.Multiply((0.5, 1.5), per_channel=0.5),
        iaa.FrequencyNoiseAlpha(
            exponent=(-4, 0),
            first=iaa.Multiply((0.5, 1.5), per_channel=True),
            second=iaa.ContrastNormalization((0.5, 2.0)))
    ]),
],
                           random_order=True)


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
        fontsize = np.random.randint(12, 32)
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
