"""MkDocs build hooks, registered under `hooks:` in mkdocs.yml."""

# Pages whose main content is a table wider than the text column. The
# right-hand table of contents is dropped there so the table fits without
# sideways scrolling. Front matter would do the same, but GitHub would then
# show it at the top of the file.
WIDE_TABLE_PAGES = {
    "frontier/problem-shapes.md",
    "machines/toolkit.md",
    "hunt/notes/A3-product-theorem.md",
}


def on_page_markdown(markdown, page, **kwargs):
    if page.file.src_uri in WIDE_TABLE_PAGES:
        hide = page.meta.setdefault("hide", [])
        if "toc" not in hide:
            hide.append("toc")
    return markdown
