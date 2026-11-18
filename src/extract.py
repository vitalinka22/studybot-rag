"""Tools to turn a saved HTML page into clean text."""
from bs4 import BeautifulSoup

# Tags we throw away completely (menus, scripts, photo credits, images ...)
NOISE_TAGS = ["script", "style", "nav", "header", "footer", "aside", "form", "small", "picture", "img"]

# Tags inside a sentence (links, bold, italic ...). We keep their text but remove the tag itself.
INLINE_TAGS = ["a", "i", "b", "em", "strong", "span"]


def read_page(html):
    """Return the page language, its main heading, and the cleaned main content."""
    soup = BeautifulSoup(html, "html.parser")
    language = soup.html.get("lang", "") if soup.html else ""
    main = soup.find("main") or soup.body
    for tag in main.find_all(NOISE_TAGS):
        tag.decompose()
    h1 = main.find("h1")
    heading = h1.get_text(" ", strip=True) if h1 else ""
    if h1:
        h1.decompose()
    return language, heading, main


def key_facts(main):
    """Read the table of key facts (Degree, Language of instruction, ...) into a dictionary."""
    facts = {}
    table = main.find("table")
    if table is None:
        return facts
    for row in table.find_all("tr"):
        th, td = row.find("th"), row.find("td")
        if th and td:
            facts[th.get_text(" ", strip=True)] = td.get_text(" ", strip=True)
    # Delete the table only if we really read facts from it
    if facts:
        table.decompose()
    return facts


def table_to_text(table):
    """Turn a table into readable lines, e.g. 'Semester: Winter semester; Deadline: 15 July'."""
    # Step 1: read every row as a list of cell texts
    rows = []
    for tr in table.find_all("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["th", "td"])]
        if cells:
            rows.append(cells)
    if not rows:
        return ""

    # Step 2: is the first row a heading row (only <th> cells)?
    header = rows[0]
    has_header_row = all(cell.name == "th" for cell in table.find("tr").find_all(["th", "td"]))

    # Step 3: turn each data row into one line
    lines = []
    for cells in (rows[1:] if has_header_row else rows):
        if has_header_row and len(cells) == len(header):
            lines.append("; ".join(f"{h}: {v}" for h, v in zip(header, cells)))
        elif len(cells) == 2:
            lines.append(f"{cells[0]}: {cells[1]}")
        else:
            lines.append(" | ".join(cells))

    # Step 4: one line per row
    return "\n".join(lines)


def sections(main):
    """Split the main content into (heading, text) sections."""
    # Replace every remaining table with its readable text
    for table in main.find_all("table"):
        table.replace_with(table_to_text(table))

    # Remove inline tags so sentences with links don't break into pieces
    for tag in main.find_all(INLINE_TAGS):
        tag.unwrap()
    main.smooth()

    # Mark the headings so we can find them in the text
    for h in main.find_all(["h2", "h3"]):
        h.string = "## " + h.get_text(" ", strip=True)

    result = []
    heading, lines = "Introduction", []
    for line in main.get_text("\n", strip=True).split("\n"):
        if line.startswith("## "):
            if lines:
                result.append((heading, clean(" ".join(lines))))
            heading, lines = line[3:], []
        else:
            lines.append(line)
    if lines:
        result.append((heading, clean(" ".join(lines))))
    return result


def clean(text):
    """Replace runs of spaces and line breaks with a single space."""
    return " ".join(text.split())