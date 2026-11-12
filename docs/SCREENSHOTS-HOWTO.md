# How the screenshots were produced

## Problem
Local Odoo 20 (`:10031`, DB `magyc_dev`) rendered a blank page in the Hermes harness browser
(headless Chrome 145 via CDP). Login worked, `web.assets_web.min.js` returned HTTP 200, but the
bundle body arrived empty (`fetch` length 0, `odoo.loader` undefined). Every earlier capture was a
blank white PNG. Restarts, asset-attachment purge, cache and service-worker clearing did not help.
The Odoo server was fine: `curl` and Playwright both received all 8,476,976 bytes.

## Fix
Drive a separate Chrome with Playwright instead of the harness browser:

    cd docs
    uv run --with playwright python capture.py

`channel="chrome"` uses the installed Chrome; no browser download. Run it from the terminal, not
from `execute_code` (its venv breaks `greenlet`).

## Pipeline
1. `capture.py` logs in, opens each screen by action id or URL, waits for `.o_main_navbar`
   plus a fixed settle time, and scrolls the first target into view.
2. Red boxes: for each target it reads `bounding_box()`, injects `position:fixed` overlay divs
   (4px red border, numbered badge) into the page, screenshots, then removes the overlays.
   Annotation is therefore part of the capture; no image editing, no coordinates to maintain.
3. A missing target prints `WARN` and is left out of the legend. Nothing is faked.
4. Output: `screenshots/de/de-*.png` and `screenshots/shots.json` (title, intro, legend per image).
5. `build_docs.py` reads `shots.json` and adds the chapter "Bildanleitung" to
   `MAGYC-Handbuch-De.pdf`: heading, intro, image, numbered legend.

## Re-run
    cd docs
    uv run --with playwright python capture.py
    uv run --with reportlab python build_docs.py

Needs Odoo running on `:10031` with DB `magyc_dev` and the admin password in env `ODOO_PW`.

## Coverage (19 images)
Start menu; company DATEV numbers; company tabs Pfand, Kommission, Kiosk-Prozess; kiosk contact
tab MAGYC; Pfand product; Kiosk-Postfach list and form; Abverkauf list and form; Pfand-Rücknahme;
Tour; Belegtexte; Nachschub wizard; Speditionstransfer wizard; sales order; invoice; DATEV export.

## Known limits
- Screens render in English where the module has no `de_DE` translation (company tabs, invoice).
- Two wizards (Nachschub, Speditionstransfer) show empty fields; filling them first would be better.
- Local dev admin password was reset to a dev-only value to log in. Not a client credential.
