# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import tomllib
import pathlib


project = 'SamGIS'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

toml_path = pathlib.Path(__file__).parent.parent / 'pyproject.toml'
with open(toml_path, "rb") as f:
    toml = tomllib.load(f)

pyproject = toml["project"]
version = pyproject["version"]
release = version
authors_list = list(pyproject["authors"])
author = ""
for author_element in authors_list:
    if len(author) > 1:
        author += ", "
    if isinstance(author_element, str):
        author += f"{author_element}"
    else:
        name = author_element.get("name")
        email = author_element.get("email")
        author += f"{name} <{email}>"

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

autodoc_mock_imports = ["fastapi", "starlette"]
# Napoleon settings
napoleon_google_docstring = True
# sphinx_autodoc_typehints settings
typehints_defaults = "comma"

templates_path = ['_templates']
exclude_patterns = [
    '_build', 'Thumbs.db', '.DS_Store', 'build/*', 'machine_learning_models', 'machine_learning_models/*',
    "sam-quantized/machine_learning_models", "sam-quantized/machine_learning_models/*"
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
