# Configuration file for the Sphinx documentation builder.

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'pyCA'
copyright = '2016-2026, Damian Sowinski'
author = 'Damian Sowinski'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinxcontrib.bibtex',
    'sphinx_copybutton',
    'myst_nb',
]

# Citations render as footnotes at the bottom of each page (footcite /
# footbibliography). The master copy of references.bib lives in the website
# repo at assets/data/references.bib; the entries used here are mirrored in
# docs/references.bib so the repo builds standalone.
bibtex_bibfiles = ['references.bib']

# The copy button strips the doctest prompts so pasted commands run as-is.
# Both prompts must be listed: copybutton_only_copy_prompt_lines defaults to
# True, so matching only '>>> ' would silently drop the continuation lines of
# a multi-line doctest from the copied text.
copybutton_prompt_text = r'>>> |\.\.\. '
copybutton_prompt_is_regexp = True
# Copy buttons go on code, not on the outputs of notebook cells.
copybutton_selector = 'div:not(.output) > div.highlight pre'

# Pages written as Jupyter notebooks (docs/*.ipynb) are run from top to
# bottom on every build, so the outputs a reader sees always come from the
# code beside them and the repository stores the notebooks without outputs.
# A cell that raises fails the build.
nb_execution_mode = 'force'
nb_execution_raise_on_error = True
nb_execution_timeout = 900

# Notebook text writes math as $...$ and $$...$$, which Jupyter and Colab
# render too, where the {math} role would show up as raw markup.
myst_enable_extensions = ['dollarmath']

# Every notebook page gets buttons that open it, runnable, on Binder and on
# Google Colab (see docs/_templates/page.html).  Both services read the
# notebook from this public repository and branch.
html_context = {
    'launch_repo': 'EternalTime/CellularAutomata',
    'launch_branch': 'master',
    'launch_path': 'docs',
}

# Bibliography style: the entry's url is carried by its title as a link
# instead of being printed as a bare URL after the entry.
import pybtex.plugin
from pybtex.style.formatting.unsrt import Style as UnsrtStyle
from pybtex.style.template import field, href, optional, sentence, tag


class LinkedTitleStyle(UnsrtStyle):
    def format_title(self, e, which_field, as_sentence=True):
        formatted_title = field(
            which_field, apply_func=lambda text: text.capitalize()
        )
        if 'url' in e.fields:
            formatted_title = href[field('url', raw=True), formatted_title]
        if as_sentence:
            return sentence[formatted_title]
        return formatted_title

    def format_btitle(self, e, which_field, as_sentence=True):
        formatted_title = tag('em')[field(which_field)]
        # Link only the entry's own title, not e.g. an incollection's
        # booktitle, so each entry carries exactly one link.
        if 'url' in e.fields and which_field == 'title':
            formatted_title = href[field('url', raw=True), formatted_title]
        if as_sentence:
            return sentence[formatted_title]
        return formatted_title

    def format_web_refs(self, e):
        # The url now lives on the title; print nothing here.
        return sentence[optional[self.format_eprint(e)]]


pybtex.plugin.register_plugin(
    'pybtex.style.formatting', 'linkedtitle', LinkedTitleStyle
)
bibtex_default_style = 'linkedtitle'

templates_path = ['_templates']
source_suffix = {
    '.rst': 'restructuredtext',
    '.ipynb': 'myst-nb',
}
exclude_patterns = ['_build', '**.ipynb_checkpoints']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']


# -- Plain dash between a parameter's type and its description -------------
# Sphinx and napoleon join them with " -- ", which smart quotes draw as an
# en dash.

from docutils import nodes
from sphinx.transforms import SphinxTransform


class PlainDashFieldSeparator(SphinxTransform):
    default_priority = 700  # before smart quotes, which run at 750

    def apply(self, **kwargs):
        for body in self.document.findall(nodes.field_body):
            for text in list(body.findall(nodes.Text)):
                if " -- " in text and not isinstance(text.parent, nodes.literal):
                    plain = nodes.Text(str(text).replace(" -- ", " - "))
                    text.parent.replace(text, plain)


def setup(app):
    app.add_transform(PlainDashFieldSeparator)
