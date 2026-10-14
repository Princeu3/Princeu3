# Profile README

`README.md` is rendered on https://github.com/Princeu3.

- Keep career claims grounded in shipped work, public repositories, or confirmed experience.
- Use GitHub-supported Markdown and HTML. GitHub removes custom CSS and scripts.
- Keep display assets in `assets/`; cache generated stats rather than embedding live third-party image endpoints.
- The header uses `<picture>` with light, dark, and mobile SVG variants. Keep their text consistent and retain descriptive alt text.
- SVGs must be self-contained: no external fonts, linked images, scripts, or `foreignObject`. The contribution snake may animate.
- Check relative asset paths, SVG XML, external links, and rendered desktop/mobile layouts before publishing.
- Run `python3 -m unittest discover -s tests -v` before changing the stats refresher. Its daily GitHub Action keeps the last valid images when a provider fails.
