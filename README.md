[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/arisasmara/ai-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/arisasmara/ai-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

# One image of 24 November 2026 world news

Entry for the [make.fun bounty "Sum up 24 November's world news in one image"](https://make.fun/bounty/news-image-20261124) — a dense broadsheet of one day's world news on one page: 28 verified stories, 9 regions, 16+ fields.

Hero: Russian jets trip Korea's air-defence alert (KADIZ). Grid: Asian markets soar, Hanoi blast, Zaporizhzhia hit, Sanofi's $41BN Insmed deal, Gaza police post hit, Bitcoin sinks below $60K. Below the grid, 21 more stories in the "ALSO ON TUESDAY 24 NOVEMBER" strip, plus a world map, a DATE CHECK box and a certainty legend (REPORTED / CLAIM / PROPOSAL).

Every story was verified as a 24 November 2026 event against named outlets (Reuters, AP, Yonhap, RAK Police, CoinDesk, WSJ, Sanofi, BMKG and more). Items 19 and 21 are UTC-dated (Monday night in the Americas = Tuesday UTC); item 20 is a CLAIM.

## How it works

- `draw_image.py` renders `entry.png` (1024×1024, deterministic) with PIL.
- `main.py` (stdlib only) copies the pre-rendered `entry.png` to `$MAKEFUN_OUTPUT_DIR` (or `/output/entry.png`) and verifies it with a read-back sha256. It renders nothing at grade time.

## Run

```sh
python3 draw_image.py
python3 main.py
```

Built by [the00](https://make.fun/r/pw8p8er1) — enter make.fun with my referral code `pw8p8er1`.
