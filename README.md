# onua — website source

A static website for ONUA, a non-profit-minded branding studio. Plain HTML, CSS and JavaScript; no build step. Site language: English.

## Structure

```
index.html        Home
about.html        About (the name, the founding question, mission and values, pro bono process, team)
portfolio.html    Portfolio (filters, one detail view per project)
events.html       Events (Upcoming / Ongoing / Past)
notes.html        Notes (editorial archive and articles)
contact.html      Contact (not yet connected to a server)
styles.css        Shared styles; colour, type and spacing tokens at the top in :root
script.js         Shared interactions
assets/
  logo/onua-wordmark.svg       Hand-drawn lowercase wordmark
  fonts/onua-hand.woff         Display font drawn with the wordmark's pen (+ .ttf and its build script)
  projects/<name>.svg          Design-output images for the example projects
  projects/<name>-sketch.svg   Process sketches for the example projects
```

Each page holds its own content. The header and footer are repeated in all six files, so change the menu in all six.

## Portfolio detail views

Each project has an `<article class="detail" id="…">` inside `portfolio.html`. A link ending in `#mulgyeol` shows only that project; no hash shows the list. Without JavaScript, the list and all details are shown in order. To add a real project, add a matching `<li data-tags="…">` in the list and a detail `<article>`. Filter values: `art`, `music`, `fashion`, `food` (Food & Space), `craft`.

## Colour

| Use | Value |
| --- | --- |
| Background | #FAF9F6 |
| Secondary background | #F3F2EE |
| Text | #242422 |
| Secondary text | #72726C |
| Rules | #DEDED7 |

A paper grain sits at about 2.5% opacity. Remove `--grain` for a completely flat background.

## Type

**Body text** (paragraphs, menus, captions, inputs, most headings) uses **Gowun Dodum**: slightly soft terminals without looking cute, calm for long reading, and it carries the few Korean words on the site (온, 情, 이지해, 여백) in the same voice as the English. SIL Open Font License, loaded from Google Fonts. Fallbacks: Pretendard → Apple SD Gothic Neo → Noto Sans KR → Malgun Gothic → system sans. It has a single weight, so hierarchy comes from size, colour and spacing.

**Key lines** use **onua Hand** (`assets/fonts/onua-hand.woff`), a display face drawn for ONUA with the same pen as the wordmark. Its o, n, u and a are the logo's own strokes; the rest of the lowercase alphabet and basic punctuation (. , ’ ? ! - —) were drawn to match. Capitals map to the lowercase forms, as in the logo. It is used only for:

- the main statement at the top of each page (`.hero h1`, `.page-intro h1`)
- the closing invitation (`.send h2`)
- buttons (`.btn`)

Digits and other symbols are not drawn yet and fall back to Gowun Dodum, so keep them out of these lines or add glyphs first. `assets/fonts/build_font.py` rebuilds the font from its stroke definitions (needs Python with numpy, opencv-python and fontTools): add a glyph to `G`, map it in `CMAP`, and run `python3 build_font.py assets/fonts`.

## Where the hand shows

- The irregular strokes of the logo, and the onua Hand lines that share its pen
- Short underlines beneath key words (`.under`)
- Small arrows beside links (`.arrow`, `.arrow--back`)
- The underline on the current menu item and active filter
- Process sketches in each project detail

## Content rules kept

- All six portfolio projects are fictional examples and are labelled on every screen. No results or testimonials. Replace them with real collaborations only with each partner's consent.
- No event is confirmed, so all are marked Upcoming, date and place to be confirmed, registration not open. The Ongoing and Past filters say there is nothing yet.
- Note dates are November 2026, when the site was made. The interview is marked as in preparation.
- No contact details, awards or organisational credentials are included.

## Connecting the contact form

The form validates and prepares a copyable message, and never claims to have sent anything. To connect it:

1. Choose a form service or endpoint and send the data with `fetch` in the submit handler in `script.js`.
2. Show a "sent" confirmation in `#prepared` only after the server confirms success.
3. Update the "This form doesn't send anything yet" notice and the privacy notice, and add the retention period.
4. Add contact details to the footer once they exist.

## Reference image

The ONUA wordmark image mentioned in the brief was not attached, so the logo was drawn from the written description. It can be redrawn to follow the original lettering if you share it.
