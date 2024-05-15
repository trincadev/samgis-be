# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
import tomllib


project = 'SamGIS'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
sys.path.insert(0, os.path.abspath('..'))

# Pull general sphinx project info from pyproject.toml
# Modified from https://stackoverflow.com/a/75396624/1304076
with open("../pyproject.toml", "rb") as f:
    toml = tomllib.load(f)

pyproject = toml["tool"]["poetry"]
version = pyproject["version"]
release = version
authors_list = [author for author in pyproject["authors"]]
author = ", ".join(authors_list) if len(authors_list) > 1 else authors_list[0]
copyright = f"2023-now {author}"

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinxcontrib.openapi',
    'myst_parser',
    # 'sphinx_autodoc_defaultargs'
]
# Napoleon settings
napoleon_google_docstring = True
typehints_defaults = "comma"

templates_path = ['_templates']
exclude_patterns = [
    '_build', 'Thumbs.db', '.DS_Store', 'build/*', 'machine_learning_models', 'machine_learning_models/*'
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'restructuredtext',
    '.md': 'markdown',
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
        'donate.html',
    ]
}
html_static_path = ['_static']
html_theme_options = {
    "description": "Segment Anything applied to geodata",
    "fixed_sidebar": True,
    "sidebar_collapse": False,
    'globaltoc_collapse': False
}
