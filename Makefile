PYTHON := python

# Default target: runs the RPAL processor with the specified file
go:
	$(PYTHON) myrpal.py $(file)

# Target to print the AST
ast:
	$(PYTHON) myrpal.py -ast $(file) 

# Target to print the standardized AST
sast:
	$(PYTHON) myrpal.py -sast $(file) 

clean:
	rm -rf __pycache__ *.pyc

# Phony targets to avoid conflicts with files named 'go', 'ast', or 'sast'
.PHONY: go ast sast clean
