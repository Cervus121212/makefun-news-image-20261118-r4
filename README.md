# The World Today — 18 November 2026 (r4)

A one-page newspaper front page for the make.fun news-image-20261118
bounty: the day's world news on a single page.

## Design (new approach after r3)

r3 packed 46 stories into the same space and scored WORSE (944.518) than
r2 (949.581). This rebuild goes the other way: **24 stories, 7 regions,
12 drawn panels**, much bigger type, generous whitespace, a rich drawn
hero, proof tags on every story, a UTC timeline, and a "what we left out"
box that names what was held back and why. The title is descriptive,
like the winners'.

- **Lead:** NVIDIA posts a record $115.8bn quarter (+103%).
- **Photos (real, free-licensed):** Jensen Huang portrait (Office of the
  President, Taiwan, CC BY 2.0); Cyclone Akvan satellite, 18 Nov 07:50
  UTC, NOAA-21 (public domain).
- **Drawn (12):** hero AI-chip panel, masthead globe + sun, 7 region
  icons, market-movers chart, lead chip icon.
- **Proof:** every story carries its source tag; every story was checked
  against its date before print. Two candidate items were held back and
  are named in the "left out" box.

## Build

    python3 generate.py            # writes entry.png (deterministic)
    python3 generate.py out.png    # same image, other path

`main.py` copies `entry.png` to `$MAKEFUN_OUTPUT_DIR` for the harness.
No network, no API keys, no generated images — PIL canvas + Wikimedia
photos only.

## Title (for submit)

Wednesday 18 November 2026: 24 stories, 7 regions, 12 drawn, built to
read at thumbnail, half and full size
