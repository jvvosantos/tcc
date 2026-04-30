"""PocketRE shared library.

All experiment scripts are thin configuration files that delegate the
heavy lifting to the helpers below.

Modules
-------
- labels     : registry of label verbalization variants (BASELINE, IMPROVED, ...)
- io         : load/save dataset and result JSON files
- inference  : NLI and zero-shot Hugging Face pipeline wrappers
- metrics    : precision / recall / F1 helpers and reporting

To test a new label variant, edit `labels.py` (see its docstring).
"""
