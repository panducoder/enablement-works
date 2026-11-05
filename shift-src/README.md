# The Shift (enablement.works/shift/)

A static sub-site: AI sales workflows on film, each with the prompt, the stack and the before and after.

- `catalog.json` holds the workflows. It is sample content until real team videos replace it.
- `build_shift.py` writes the pages into `static/shift/` using `build.py`'s `page()`, so the header, footer and organisation graph match the main site.
- `shift.css` holds the page styles, scoped to `.shiftsite` and loaded after `/assets/site.css`. `shift.js` adds the scroll film, the before/after divider, board filters and the copy and share buttons. Every page works without it.
- Media lives only in `static/shift/film|media|og`, and the script never touches it.

## Rebuild

```bash
python3 shift-src/build_shift.py && python3 build.py
```

Then commit and push (pull with `--rebase` first).

## Adding a real video

1. Put `<clip>.mp4` and `<clip>-poster.jpg` in `static/shift/media/`.
2. Add or edit the entry in `catalog.json` and point `clip` at the new file name.
3. Make a 1200x630 share card as `static/shift/og/<slug>.png`.
4. Rebuild.

No cookies, analytics or trackers, as the site's privacy page promises.
