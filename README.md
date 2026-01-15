# Academic Pages - Alberto Carraro

This is an academic personal website built with GitHub Pages, hosted at [https://lambdalambdalambda.github.io/albertocarraro/](https://lambdalambdalambda.github.io/albertocarraro/).

## Project Structure

```
/docs/                          # GitHub Pages root (published to github.io)
├── /publication/               # Individual publication pages
├── /publications/              # Publications index page
├── /assets/                    # CSS, JS, images
└── index.html                  # Home page

/my_publications.bib            # BibTeX bibliography file
/generate_publications.py       # Script to generate publication pages
```

## Managing Publications

### Adding or Updating Publications

1. **Edit your bibliography**: Update `/my_publications.bib` with your BibTeX entries
   - Add new entries using standard BibTeX format
   - Update existing entries as needed

2. **Regenerate publication pages**: Run the generation script
   ```bash
   python3 generate_publications.py
   ```

3. **The script will automatically**:
   - Parse all BibTeX entries from `/my_publications.bib`
   - Generate individual HTML pages for each publication in `/docs/publication/`
   - Regenerate the publications index at `/docs/publications/index.html`
   - Organize publications by type (Journal Articles, Book Chapters, Conferences, etc.)
   - Clean up old LaTeX formatting in titles
   - Sort publications by year (most recent first)

4. **Commit and push changes**:
   ```bash
   git add -A
   git commit -m "Update publications"
   git push origin master
   ```

### BibTeX Format

The script supports standard BibTeX entry types:
- `@article` - Journal articles
- `@inproceedings` - Conference papers
- `@incollection` - Book chapters
- `@book` - Books
- `@phdthesis` - Doctoral dissertations
- `@misc` - Other publications (preprints, technical reports, etc.)

### Example BibTeX Entry

```bibtex
@article{yourkey_year,
	title = {Your Paper Title},
	author = {First Author and Second Author and Your Name},
	journal = {Journal Name},
	year = {2025},
	volume = {10},
	number = {3},
	pages = {100--115},
	doi = {10.1234/example.doi},
	url = {https://example.com/paper}
}
```

## What the Script Does

### generate_publications.py

**Parses BibTeX**: Extracts all publication metadata from `my_publications.bib`

**Generates Publication Pages**: Creates an individual HTML page for each publication with:
- Clean title (LaTeX formatting removed)
- Author list
- Publication metadata (year, journal, volume, pages, DOI)
- Links to view publication and DOI
- Proper semantic HTML with Schema.org markup

**Generates Publications Index**: Creates `/docs/publications/index.html` with:
- Organized list of all publications
- Grouped by publication type
- Reverse chronological order (newest first)
- Links to individual publication pages

**Cleans Up**: Removes old placeholder publication files

## File Locations

| File | Purpose |
|------|---------|
| `/my_publications.bib` | Your master BibTeX bibliography |
| `/generate_publications.py` | Python script to generate all publication pages |
| `/docs/publications/index.html` | Main publications listing page (auto-generated) |
| `/docs/publication/*.html` | Individual publication pages (auto-generated) |

## Deployment

The site is deployed to GitHub Pages using the `/docs/` folder as the root:

1. **Repository**: [github.com/LambdaLambdaLambda/albertocarraro](https://github.com/LambdaLambdaLambda/albertocarraro)
2. **Site URL**: https://lambdalambdalambda.github.io/albertocarraro/
3. **Settings**: GitHub Pages configured to publish from `master` branch, `/docs` folder

### Asset Paths

All asset paths (CSS, images, fonts) include the subdirectory `/albertocarraro/` to work correctly when deployed to a GitHub Pages subdirectory:
- Stylesheets: `/albertocarraro/assets/css/main.css`
- Images: `/albertocarraro/images/profile.png`
- Feed: `/albertocarraro/feed.xml`

## Troubleshooting

### Script Errors

If you get a Python error when running the script:
1. Ensure Python 3 is installed: `python3 --version`
2. Check that `my_publications.bib` is valid BibTeX format
3. Verify the file paths in the script match your setup

### Broken Links

If publication pages show 404 errors:
1. Verify the `/docs/publication/` folder has generated `.html` files
2. Check that filenames match the links in the index
3. Ensure the base path `/albertocarraro/` is correct (adjust if using a different subdirectory)

### LaTeX Formatting in Titles

The script automatically removes LaTeX braces from titles (e.g., `{RGB}-{D}` → `RGB-D`). If titles don't look right:
1. Check your BibTeX entry format
2. Run the script again to regenerate
3. Verify the title field in the BibTeX doesn't have extra braces

## Customization

### Organizing Publications by Type

Edit the `generate_publications_index()` function in `generate_publications.py` to customize how publications are grouped. Currently supports:
- Journal Articles
- Book Chapters  
- Conference Papers
- Theses
- Other Publications

### Changing Publication Metadata Display

Edit the `generate_html()` function to customize what metadata appears on each publication page (volume, issue, pages, DOI, etc.).

### Site Styling

Modify `/docs/assets/css/main.css` to change the site appearance. Publication pages use the same stylesheet.

## Requirements

- **Python 3.6+** - for running `generate_publications.py`
- **Git** - for version control
- **BibTeX bibliography** - your `my_publications.bib` file

## License

This academic website template is based on [AcademicPages](https://github.com/academicpages/academicpages.github.io), which is a fork of [Minimal Mistakes Jekyll Theme](https://mademistakes.com/work/minimal-mistakes-jekyll-theme/).

## Quick Start

```bash
# 1. Update your bibliography
nano my_publications.bib

# 2. Regenerate all publication pages
python3 generate_publications.py

# 3. Commit changes
git add -A
git commit -m "Update publications"

# 4. Push to GitHub
git push origin master

# 5. Visit your site (changes may take 1-2 minutes to appear)
# https://lambdalambdalambda.github.io/albertocarraro/
```

---

**Last Updated**: January 15, 2026
