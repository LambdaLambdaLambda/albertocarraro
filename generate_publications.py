#!/usr/bin/env python3
"""
Generate HTML publication files from BibTeX bibliography.
"""

import re
import os
from pathlib import Path
from datetime import datetime

def parse_field_value(field_str):
    """Parse a BibTeX field value handling nested braces and quotes."""
    field_str = field_str.strip()
    
    # Check if it's quoted
    if field_str.startswith('"') and field_str.endswith('"'):
        return field_str[1:-1]
    
    # Handle braced content
    if field_str.startswith('{') and field_str.endswith('}'):
        # Remove outer braces and handle nested ones
        content = field_str[1:-1]
        return content
    
    return field_str

def parse_bibtex(filename):
    """Parse BibTeX file and extract publications."""
    publications = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by entry markers (@article, @inproceedings, @incollection, etc.)
    entries = re.findall(r'@(\w+)\{([^,]+),(.+?)\n\}', content, re.DOTALL)
    
    for entry_type, key, fields in entries:
        entry = {'type': entry_type, 'key': key}
        
        # Parse each field more carefully
        # Look for patterns like: field_name = value,
        current_pos = 0
        while current_pos < len(fields):
            # Find next field assignment
            match = re.search(r'(\w+)\s*=\s*', fields[current_pos:])
            if not match:
                break
            
            field_name = match.group(1).lower()
            value_start = current_pos + match.end()
            
            # Extract the value (either {...} or "...")
            value_end = value_start
            if value_start < len(fields):
                if fields[value_start] == '{':
                    # Find matching closing brace
                    brace_count = 0
                    for i in range(value_start, len(fields)):
                        if fields[i] == '{':
                            brace_count += 1
                        elif fields[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                value_end = i + 1
                                break
                elif fields[value_start] == '"':
                    # Find matching closing quote
                    value_end = fields.find('"', value_start + 1) + 1
            
            if value_end > value_start:
                raw_value = fields[value_start:value_end]
                field_value = parse_field_value(raw_value)
                field_value = clean_latex(field_value.strip())
                entry[field_name] = field_value
                current_pos = value_end
            else:
                current_pos += 1
        
        publications.append(entry)
    
    # Sort by year (descending)
    publications.sort(key=lambda x: int(x.get('year', '0')), reverse=True)
    
    return publications

def clean_latex(text):
    """Clean LaTeX formatting from text."""
    if not text:
        return text
    
    # Keep removing outermost braces until none remain
    while '{' in text:
        # Remove outermost braces
        old_text = text
        text = re.sub(r'^[{](.+)[}]$', r'\1', text)  # Remove surrounding braces
        text = re.sub(r'\{([^{}]+)\}', r'\1', text)  # Remove single-level braces
        
        # If no change, break to avoid infinite loop
        if text == old_text:
            break
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_authors(authors_str):
    """Format author string from BibTeX."""
    if not authors_str:
        return ""
    
    # Split by 'and'
    authors = [a.strip() for a in authors_str.split(' and ')]
    
    if len(authors) == 1:
        return authors[0]
    elif len(authors) == 2:
        return f"{authors[0]} and {authors[1]}"
    else:
        return ", ".join(authors[:-1]) + f", and {authors[-1]}"

def get_date_for_filename(pub):
    """Create filename-friendly date from publication info."""
    year = pub.get('year', '2020')
    month = pub.get('month', '01')
    
    # Convert month name to number
    months = {
        'jan': '01', 'january': '01',
        'feb': '02', 'february': '02',
        'mar': '03', 'march': '03',
        'apr': '04', 'april': '04',
        'may': '05',
        'jun': '06', 'june': '06',
        'jul': '07', 'july': '07',
        'aug': '08', 'august': '08',
        'sep': '09', 'september': '09',
        'oct': '10', 'october': '10',
        'nov': '11', 'november': '11',
        'dec': '12', 'december': '12',
    }
    
    if month.lower() in months:
        month = months[month.lower()]
    elif not month.isdigit():
        month = '01'
    
    return f"{year}-{month:0>2}"

def get_publication_title(pub):
    """Extract and clean publication title."""
    title = pub.get('title', 'Untitled')
    # Clean LaTeX formatting
    title = clean_latex(title)
    return title.strip()

def generate_publication_slug(pub):
    """Generate URL slug for publication."""
    title = pub.get('title', 'untitled').lower()
    # Remove special characters and clean up
    slug = re.sub(r'[^a-z0-9\s]', '', title)
    slug = '-'.join(slug.split()[:5])  # First 5 words
    return slug

def generate_html(pub):
    """Generate HTML content for a publication."""
    
    title = get_publication_title(pub)
    date_str = get_date_for_filename(pub)
    slug = generate_publication_slug(pub)
    pub_key = slug
    
    # Get publication details
    authors = format_authors(pub.get('author', 'Unknown Author'))
    year = pub.get('year', 'n.d.')
    journal = pub.get('journal', pub.get('booktitle', 'Unknown'))
    url = pub.get('url', '')
    doi = pub.get('doi', '')
    pages = pub.get('pages', '')
    volume = pub.get('volume', '')
    number = pub.get('number', '')
    
    # Build citation string
    citation_parts = [authors, f"({year})."]
    citation_parts.append(f'"{title}."')
    
    if journal:
        citation_parts.append(f"<i>{journal}</i>,")
    
    if volume:
        citation_parts.append(volume)
    if number:
        citation_parts.append(f"({number})")
    if pages:
        citation_parts.append(f"pp. {pages}")
    
    citation = " ".join(citation_parts)
    
    # Build links for citation
    links = []
    if url:
        links.append(f'<a href="{url}">View Publication</a>')
    if doi:
        links.append(f'<a href="https://doi.org/{doi}">DOI</a>')
    
    links_html = " | ".join(links) if links else ""
    
    # Build optional HTML elements
    volume_html = f'<li><strong>Volume:</strong> {volume}</li>' if volume else ''
    pages_html = f'<li><strong>Pages:</strong> {pages}</li>' if pages else ''
    doi_html = f'<li><strong>DOI:</strong> <a href="https://doi.org/{doi}">{doi}</a></li>' if doi else ''
    links_footer = f'<br/>{links_html}' if links_html else ''
    
    html = f"""

<!doctype html>
<html lang="en" class="no-js">
  <head>
    

<meta charset="utf-8">



<!-- begin SEO -->









<title>{title} - Your Name / Site Title</title>



<meta name="description" content="{title}">





  <meta property="article:published_time" content="{year}-01-01T00:00:00+00:00">



  <link rel="canonical" href="/albertocarraro/publication/{date_str}-{pub_key}">





  

  <script type="application/ld+json">
    {{
      "@context" : "http://schema.org",
      "@type" : "ScholarlyArticle",
      "name" : "{title}",
      "author": "{authors}",
      "datePublished": "{year}"
    }}
  </script>

<!-- end SEO -->

<!-- Open Graph protocol data (https://ogp.me/), used by social media -->
<meta property="og:locale" content="en-US">
<meta property="og:site_name" content="Your Name / Site Title"> 
<meta property="og:title" content="{title}">

  <meta property="og:type" content="article">


  <meta property="og:description" name="description" content="{title}">


  <meta property="og:url" content="/albertocarraro/publication/{date_str}-{pub_key}">



<!-- end Open Graph protocol -->

<link href="/albertocarraro/feed.xml" type="application/atom+xml" rel="alternate" title="Your Name / Site Title Feed">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<script>
  document.documentElement.className = document.documentElement.className.replace(/\\bno-js\\b/g, '') + ' js ';
</script>

<!-- For all browsers -->
<link rel="stylesheet" href="/albertocarraro/assets/css/main.css">

    

<!-- start custom head snippets -->

<!-- Support for Academicons -->
<link rel="stylesheet" href="/albertocarraro/assets/css/academicons.css"/>

<!-- favicon from https://commons.wikimedia.org/wiki/File:OOjs_UI_icon_academic-progressive.svg -->
<link rel="apple-touch-icon" sizes="180x180" href="/albertocarraro/images/apple-touch-icon-180x180.png"/>
<link rel="icon" type="image/svg+xml" href="/albertocarraro/images/favicon.svg"/>
<link rel="icon" type="image/png" href="/albertocarraro/images/favicon-32x32.png" sizes="32x32"/>
<link rel="icon" type="image/png" href="/albertocarraro/images/favicon-192x192.png" sizes="192x192"/>
<link rel="manifest" href="/albertocarraro/images/manifest.json"/>
<link rel="icon" href="/albertocarraro/images/favicon.ico"/>
<meta name="theme-color" content="#ffffff"/>

<!-- end custom head snippets -->

  </head>

  <body>

    <!--[if lt IE 9]>
<div class="notice--danger align-center" style="margin: 0;">You are using an <strong>outdated</strong> browser. Please <a href="http://browsehappy.com/">upgrade your browser</a> to improve your experience.</div>
<![endif]-->
    
<div class="masthead">
  <div class="masthead__inner-wrap">
    <div class="masthead__menu">
      <nav id="site-nav" class="greedy-nav">
        <button><span class="navicon"></span></button>
        <ul class="visible-links">
          <li class="masthead__menu-item masthead__menu-item--lg persist ">
            <a href="/albertocarraro/">Your Name / Site Title</a>
          </li>
          
            
            <li class="masthead__menu-item ">
              <a href="/albertocarraro/publications/">Publications</a>
            </li>
          
            
            <li class="masthead__menu-item ">
              <a href="/albertocarraro/talks/">Talks</a>
            </li>
          
            
            <li class="masthead__menu-item ">
              <a href="/albertocarraro/teaching/">Teaching</a>
            </li>
          
            
            <li class="masthead__menu-item ">
              <a href="/albertocarraro/portfolio/">Portfolio</a>
            </li>
          
            
            <li class="masthead__menu-item ">
              <a href="/albertocarraro/year-archive/">Blog Posts</a>
            </li>
          
            
            <li class="masthead__menu-item ">
              <a href="/albertocarraro/cv/">CV</a>
            </li>
          
            
            <li class="masthead__menu-item ">
              <a href="/albertocarraro/markdown/">Guide</a>
            </li>
          
          <li id="theme-toggle" class="masthead__menu-item persist tail">
            <a role="button" aria-labelledby="theme-icon"><i id="theme-icon" class="fa-solid fa-sun" aria-hidden="true" title="toggle theme"></i></a>
          </li>
        </ul>
        <ul class="hidden-links hidden"></ul>
      </nav>
    </div>
  </div>
</div>


    <div id="main" role="main">
  <div class="sidebar sticky">
  <div itemscope itemtype="http://schema.org/Person">
    <div class="author__avatar">
        <img src="/albertocarraro/images/profile.png" class="author__avatar" alt="Alberto Carraro, PhD"  fetchpriority="high" />
    </div>

    <div class="author__content">
      <h3 class="author__name">Alberto Carraro, PhD</h3>
      <p class="author__bio">Teacher, trainer, scientist, researcher</p>
    </div>

    <div class="author__urls-wrapper">
      <button class="btn btn--inverse">Follow</button>
      <ul class="author__urls social-icons">
        <li class="author__desktop"><i class="fas fa-fw fa-location-dot icon-pad-right" aria-hidden="true"></i>Earth</li>
        <li class="author__desktop"><i class="fas fa-fw fa-building-columns icon-pad-right" aria-hidden="true"></i>Red Brick University</li>
        <li><a href="mailto:none@example.org"><i class="fas fa-fw fa-envelope icon-pad-right" aria-hidden="true"></i>Email</a></li>
        <li><a href="https://scholar.google.com/citations?user=PS_CX0AAAAAJ"><i class="ai ai-google-scholar ai-fw icon-pad-right"></i>Google Scholar</a></li>
        <li><a href="https://orcid.org/yourorcidurl"><i class="ai ai-orcid ai-fw icon-pad-right"></i>ORCID</a></li>
        <li><a href="https://github.com/academicpages"><i class="fab fa-fw fa-github icon-pad-right" aria-hidden="true"></i>GitHub</a></li>
      </ul>
    </div>
  </div>
  </div>

  <article class="page" itemscope itemtype="http://schema.org/CreativeWork">
    <meta itemprop="headline" content="{title}">
    <meta itemprop="description" content="{authors}">
    <meta itemprop="datePublished" content="{year}">
    
    <div class="page__inner-wrap">
      <header>
        <h1 class="page__title" itemprop="headline">{title}</h1>
        <p>Published in <i>{journal}</i>, {year}</p>
      </header>

      <section class="page__content" itemprop="text">
        <h2>Authors</h2>
        <p>{authors}</p>
        
        <h2>Publication Details</h2>
        <ul>
          <li><strong>Year:</strong> {year}</li>
          <li><strong>Journal/Venue:</strong> {journal}</li>
          {volume_html}
          {pages_html}
          {doi_html}
        </ul>
      </section>

      <footer class="page__meta">
        <p style="font-size: smaller">{citation}
        {links_footer}</p>
      </footer>
    </div>
  </article>

</div>
</body>
</html>
"""
    
    return html, date_str, pub_key

def generate_publications_index(output_file, pub_links):
    """Generate the publications index HTML file."""
    
    # Sort publications by year (descending)
    pub_links.sort(key=lambda x: int(x['year']), reverse=True)
    
    # Group by type
    articles = [p for p in pub_links if p['type'] in ['article']]
    books = [p for p in pub_links if p['type'] in ['book']]
    inproceedings = [p for p in pub_links if p['type'] in ['inproceedings', 'conference']]
    incollections = [p for p in pub_links if p['type'] in ['incollection']]
    others = [p for p in pub_links if p['type'] not in ['article', 'book', 'inproceedings', 'conference', 'incollection', 'phdthesis', 'misc']]
    thesis = [p for p in pub_links if p['type'] in ['phdthesis']]
    misc = [p for p in pub_links if p['type'] in ['misc']]
    
    # Read the template (keeping header and footer from original)
    with open(output_file, 'r', encoding='utf-8') as f:
        original = f.read()
    
    # Extract header (everything before <div class="archive">)
    header_end = original.find('<div class="archive">')
    header = original[:header_end] if header_end != -1 else original
    
    # Extract footer (everything after </div>\n  </div>)
    footer_start = original.find('  </div>\n</div>\n\n\n    <div class="page__footer">')
    footer = original[footer_start:] if footer_start != -1 else ''
    
    # Build publication entries
    def build_pub_entry(pub):
        """Build HTML for a single publication entry."""
        filename = pub['filename']
        title = pub['title']
        journal = pub['journal']
        year = pub['year']
        
        # Extract date and slug from filename (YYYY-MM-slug.html)
        # Remove .html and use as full path
        link_path = filename[:-5]  # Remove .html
        link = f"/albertocarraro/publication/{link_path}"
        
        html = f'''
<div class="list__item">
  <article class="archive__item" itemscope itemtype="http://schema.org/CreativeWork">
    <h2 class="archive__item-title" itemprop="headline">
      <a href="{link}" rel="permalink">{title}</a>
    </h2>
    
    <p>Published in <i>{journal}</i>, {year}</p>
    
    <p class="archive__item-excerpt" itemprop="description">{pub['authors']}</p>
  </article>
</div>
'''
        return html
    
    # Build content sections
    content = '<div class="archive">\n    <h1 class="page__title">Publications</h1>\n'
    content += '  <div class="wordwrap">You can also find my articles on <a href="https://scholar.google.com/citations?user=PS_CX0AAAAAJ">my Google Scholar profile</a>.</div>\n\n'
    
    if articles:
        content += '\n    <h2>Journal Articles</h2><hr />\n'
        for pub in articles:
            content += build_pub_entry(pub)
    
    if incollections:
        content += '\n    <h2>Book Chapters</h2><hr />\n'
        for pub in incollections:
            content += build_pub_entry(pub)
    
    if inproceedings:
        content += '\n    <h2>Conference Papers</h2><hr />\n'
        for pub in inproceedings:
            content += build_pub_entry(pub)
    
    if thesis:
        content += '\n    <h2>Theses</h2><hr />\n'
        for pub in thesis:
            content += build_pub_entry(pub)
    
    if misc or others:
        content += '\n    <h2>Other Publications</h2><hr />\n'
        for pub in misc + others:
            content += build_pub_entry(pub)
    
    content += '\n  </div>\n</div>\n'
    
    # Combine and write
    new_html = header + content + footer
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_html)


def main():
    """Main function."""
    bib_file = '/Users/acarraro/GitHub/albertocarraro/my_publications.bib'
    output_dir = '/Users/acarraro/GitHub/albertocarraro/docs/publication'
    index_file = '/Users/acarraro/GitHub/albertocarraro/docs/publications/index.html'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse bibliography
    print("Parsing BibTeX file...")
    publications = parse_bibtex(bib_file)
    print(f"Found {len(publications)} publications")
    
    # Delete old dummy files
    old_files = [
        '2009-10-01-paper-title-number-1.html',
        '2010-10-01-paper-title-number-2.html',
        '2015-10-01-paper-title-number-3.html',
        '2024-02-17-paper-title-number-4.html',
    ]
    
    for old_file in old_files:
        old_path = os.path.join(output_dir, old_file)
        if os.path.exists(old_path):
            os.remove(old_path)
            print(f"Deleted {old_file}")
    
    # Generate HTML files for publications
    print("\nGenerating publication HTML files...")
    pub_links = []
    for pub in publications:
        html, date_str, slug = generate_html(pub)
        filename = f"{date_str}-{slug}.html"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        title = get_publication_title(pub)
        journal = pub.get('journal', pub.get('booktitle', 'Unknown'))
        year = pub.get('year', 'n.d.')
        
        # Store publication link info for index generation
        pub_links.append({
            'filename': filename,
            'title': title,
            'journal': journal,
            'year': year,
            'type': pub.get('type', 'article'),
            'authors': format_authors(pub.get('author', 'Unknown Author'))
        })
        
        print(f"Created {filename}: {title}")
    
    # Generate publications index
    print(f"\nGenerating publications index...")
    generate_publications_index(index_file, pub_links)
    print(f"Generated publications index at {index_file}")
    
    print(f"\nGenerated {len(publications)} publication files in {output_dir}")

if __name__ == '__main__':
    main()
