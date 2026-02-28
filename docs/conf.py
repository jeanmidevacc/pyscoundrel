"""Sphinx configuration for PyScoundrel documentation."""

import sys
from pathlib import Path

# Make the src package importable for autodoc
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# -- Project information -----------------------------------------------------
project = "PyScoundrel"
copyright = "2024, Jean-Michel Daignan"
author = "Jean-Michel Daignan"
release = "0.1.2"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build"]

# -- autodoc -----------------------------------------------------------------
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

# -- Napoleon (Google-style docstrings) --------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False

# -- MyST (Markdown support) -------------------------------------------------
myst_enable_extensions = ["colon_fence"]

# -- HTML output -------------------------------------------------------------
html_theme = "furo"
html_title = "PyScoundrel"
