# Configuration file for the Sphinx documentation builder.
# -- Project information

import os
import sys
import time
from datetime import datetime

from sphinx.application import Sphinx

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(path, '../..', 'ui'))
sys.path.insert(0, os.path.join(path, '../..', 'nn'))

project = 'DeepEthoProfile'
copyright = '2022, WinterLab-Berlin'
author = 'Andrei Istudor'

release = '0.1'
version = '0.1.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'

autoclass_content = 'both'
autodoc_class_signature = 'separated'
#autodoc_typehints = "description"

autodoc_mock_imports = [
    'PyQt5', 'PyQt5.QtWidgets', 'PyQt5.QtWidgets.QMainWindow',
    'torch'
    ]
