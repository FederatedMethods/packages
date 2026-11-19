"""
Shared navigation bar for the generated HTML pages.
"""

# (file name, label) for each page, in display order
NAV_PAGES = [
    ("index.html", "Summary"),
    ("packages.html", "Packages"),
    ("functions.html", "Functions"),
    ("stats.html", "Stats"),
    ("faq.html", "FAQ"),
]


def get_navbar(active_page=None):
    """
    Return the HTML for the navigation bar.
    Args:
        active_page (str): File name of the current page (e.g. 'index.html'), which is highlighted.
    """
    links = ''
    for file_name, label in NAV_PAGES:
        css_class = ' class="active"' if file_name == active_page else ''
        links += f'<a href="./{file_name}"{css_class}>{label}</a>'
    return f'<nav class="navbar">{links}</nav>'
