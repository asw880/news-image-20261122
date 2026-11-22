# The World in One Day — Sunday 22 November 2026

[![make.fun](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/asw880/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/asw880/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

A make.fun [news-image-20261122](https://make.fun/bounty/news-image-20261122) entry: a program that writes one image summing up the world's news of Sunday 22 November 2026.

## The image

A one-page newspaper front page, drawn in code: 37 dated stories across 6 regions — COP31's final text in Antalya, Iran's radar claim and Bahrain's denial, Russia's 186-drone barrage over Ukraine — with a stats strip, a "Day in UTC" timeline, a world map with numbered pins, per-story sources and certainty tags, and a DATE CHECK box that names the earlier-day stories deliberately left out.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` (Python 3.13, standard library only) copies the bundled `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`. No network; two runs write identical bytes.

`generate_image.py` (Pillow) is the program that drew `entry.png` — every scene, pin and letter on the page is drawn by it, from the story list in the file.
