# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
BUILDDIR      = docs/_build
SOURCEDIR     = .

SPHINXSRC   ?= sphinx-apidoc
OUTDIR   ?= docs/source/
SOURCES   ?= modulos

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

update:
	@$(SPHINXSRC) -o "$(OUTDIR)" "$(SOURCES)" -f

test:
	pytest -q --show-capture=no --disable-warnings --tb=no

format:
	djlint . --reformat
	black .
	isort .

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
