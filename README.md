# The World in One Day — Sunday 22 November 2026

[![news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/asw880/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/asw880/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

**Version 3** of the entry for the [news-image-20261122](https://make.fun/bounty/news-image-20261122) bounty on [make.fun](https://make.fun): sum up 22 November's world news in one image.

v1 and v2 both scored 0.982336 (12–0) with identical rates — visual polish did not move the judge. v3 changes the **content**, not the polish.

## What changed in v3

- **COP31 is now "summit ends with NO DEAL":** the joint declaration collapsed on Sunday after the EU and others refused to adopt the text; President Kurum told the closing session the decisions were not adopted (Reuters). The draft's contents — zero fossil-fuel mentions, the $120bn adaptation target dropped, the first COP text conceding 1.5°C will be overshot — are now the reason for the collapse, not the story itself.
- **Bahrain:** base names (Al-Riffa, Awali Sakhir), operation code name "Ya Umm al-Banin", the MQ-1 Predator / MQ-9 Reaper trigger, and the Sunday developments (Bahrain's statement, IRGC footage, Bahrain's rejection).
- **Ukraine:** 186 drones, 161 downed/jammed, 56 of 72 jet-powered Shaheds intercepted; Dymer block destroyed, 8 feared buried, 14 unreachable, 30 injured (Kyiv Independent).
- **Mids corrected:** Nvidia ~$900bn lost in the week (not $811bn) plus the SEC accounting probe (Reuters); Hong Kong final turnout 98.79%, a record (not a mid-day range); Gaza restructured around Hamas seeking urgent talks, with the food-aid van strike moved to DATE CHECK (it was Saturday); Bolsonaro reworded (he *remains* in ICU; admission was Saturday); Anthropic adds the $93.5bn IPO total; Van Hollen adds the 16-vs-6 count; India adds three records; Verstappen adds "from pole after Antonelli's penalty" and "Antonelli already champion (youngest ever)"; Iran adds Tavanir chief Allahdad; Sparta II adds Finland's attribution and the sinking risk.
- **Briefs:** five items that did not check out as Sunday news were dropped (UAE oil shuttle, EU digital tax, antidepressants meta-analysis, Exercise Dugong, ICE training watchdog — all earlier-day stories) and replaced with verified Sunday stories: the Cebu vessel fire, Chahal joining the BJP, the Marcos/ICC items, India–China Corps Commander talks, and IG Metall calling 23,000 workers to strike. New: Liverpool–Man Utd tonight, Bougainville aid, Kenya floods (the first Africa story).
- **DATE CHECK** now names 21 excluded earlier-day stories with their dates, including the Gaza food-aid van strike (Sat), the Bolsonaro ICU admission (Sat), the Denmark attaché expulsion (Fri), and the 19–20 Nov strike (500+ drones, 100+ missiles — no Article 4 invocation).
- **37 stories, 6 regions** (Asia-Pacific 11, Europe 9, Americas 9, Middle East 4, Oceania 3, Africa 1), counted from the page's own datelines.

## The image

A single 1024×1024 front page, drawn in code with Pillow (`generate_image.py`): masthead, red deck, stats strip, region bar, UTC timeline, 3 heroes, 10 mids, a dotted world map with numbered pins, 24 briefs, a DATE CHECK box, and a sources footer. Every story names its outlet in parentheses; heroes and mids carry certainty tags (REPORTED / CLAIM / FORECAST). All illustrations are drawn shapes — no photos, no external images. System fonts only (Liberation).

## How to run

```sh
# regenerate the image (writes entry.png in this directory)
python3 generate_image.py

# run the entry (copies entry.png to the output directory)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` uses only the Python standard library. The entry image is exactly 1024×1024 and under 1 MiB.

## Bounty

[news-image-20261122 — Sum up 22 November's world news in one image](https://make.fun/bounty/news-image-20261122)

## License

MIT — see [LICENSE](LICENSE).
