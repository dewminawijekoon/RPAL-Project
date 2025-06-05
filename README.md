## RPAL-Project

This project is a full implementation of a **lexical analyzer**, **parser**, **AST to Standardized Tree converter**, and a **CSE machine** for the **RPAL programming language**. The implementation strictly follows the lexical rules outlined in `RPAL_Lex.pdf` and the grammar defined in `RPAL_Grammar.pdf` included in the Docs folder.

> ⚠️ Tools like `lex`, `yacc`, or similar parser generators are **not used**. All components are implemented manually using **Python**.

The parser produces an **Abstract Syntax Tree (AST)** for a given RPAL program, which is then transformed into a **Standardized Tree (ST)**. The final stage evaluates the program using a **Control Stack Environment (CSE) machine**.

The input is read from a file containing an RPAL program, and the output format is designed to match the behavior of the reference implementation `rpal.exe`.

The interpreter can be run using two methods:

---

## 1. Using Direct Python Commands

1. Open a terminal and navigate to the directory where the interpreter (`myrpal.py`) is located.
2. Run the following commands:

```bash
python myrpal.py input.txt          # Run the RPAL processor
python myrpal.py input.txt -ast     # Print the Abstract Syntax Tree (AST)
python myrpal.py input.txt -sast    # Print the Standardized AST
```

3. More input files can be found in the `inputs/` directory.

---

## 2. Using Makefile (Recommended for UNIX/Linux/Mac or Windows with Git Bash/WSL)

1. Open a terminal and navigate to the directory containing the `Makefile`.
2. Run the following commands:

```bash
make go file=input.txt      # Run the RPAL processor
make ast file=input.txt     # Print the AST
make sast file=input.txt    # Print the Standardized AST
```

> 💡 On Windows, ensure you're using a compatible terminal like **Git Bash**, **PowerShell**, or **WSL**. If you encounter issues, use direct Python commands instead.

