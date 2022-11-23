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
sys.path.insert(0, os.path.join(path, '../../ui'))
sys.path.insert(0, os.path.join(path, '../../nn'))

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
    'sphinx.ext.autosectionlabel'
]
#'sphinx.ext.viewcode',

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}

# -- Options for EPUB output
epub_show_urls = 'footnote'

#autoclass_content = 'both'
autodoc_class_signature = 'mixed'
autodoc_member_order = 'bysource'
#autodoc_typehints = "description"
add_module_names = False

autodoc_mock_imports = [
    # 'PyQt5', 'PyQt5.QtWidgets', 'PyQt5.QtCore', 'PyQt5.QtWidgets.QMainWindow',
    'torch', 'torch.nn', 'torch.nn.functional',
    'scipy', 'torch.optim', 'random', 
    'pandas',
    'av',
    'cv2',
    'sklearn', 'sklearn.metrics'
    ]
