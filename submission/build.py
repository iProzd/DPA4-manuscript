"""Assemble a Science Advances submission from the manuscript sources."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import bibtexparser
import fitz


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent
BUILD = PACKAGE / "build"
INPUT_PATTERN = re.compile(r"\\input\{([^}]+)\}")
CITE_PATTERN = re.compile(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}")


def without_comments(text: str) -> str:
    """Remove ordinary LaTeX comments without consuming escaped percent signs."""
    return re.sub(r"(?<!\\)%[^\n]*", "", text)


def expand(path: Path) -> str:
    """Expand local input files into a portable manuscript source."""
    text = without_comments(path.read_text())

    def include(match: re.Match[str]) -> str:
        relative = Path(match.group(1)).with_suffix(".tex")
        local = path.parent / relative
        return expand(local if local.is_file() else ROOT / relative)

    return INPUT_PATTERN.sub(include, text)


def body(path: str) -> str:
    """Read a declaration without its opening section heading."""
    return re.sub(r"\A\s*\\section\{[^}]+\}\s*", "", expand(ROOT / path), count=1)


def prepare_references(text: str) -> int:
    """Export cited entries without changing their bibliographic content."""
    keys = list(dict.fromkeys(
        key.strip() for match in CITE_PATTERN.findall(text) for key in match.split(",")
    ))
    database = bibtexparser.loads((ROOT / "ref.bib").read_text())
    entries = database.entries_dict
    selected = []
    for key in keys:
        entry = dict(entries[key])
        for field in ("abstract", "file", "groups", "owner", "timestamp"):
            entry.pop(field, None)
        selected.append(entry)
    database.entries = selected
    (BUILD / "references.bib").write_text(bibtexparser.dumps(database))
    return len(selected)


def assemble() -> dict[str, int]:
    """Create the combined source and its local figure dependencies."""
    BUILD.mkdir(exist_ok=True)
    common = expand(ROOT / "preamble/common.tex")
    preamble = r"""\documentclass[12pt]{article}
""" + common + r"""
\usepackage{newtxtext,newtxmath}
\usepackage[letterpaper,margin=1in]{geometry}
\usepackage{cite}
\renewcommand{\citeleft}{(}
\renewcommand{\citeright}{)}
\renewcommand{\citeform}[1]{\textit{#1}}
\usepackage[hidelinks]{hyperref}
\usepackage{microtype}
\usepackage[mathlines]{lineno}
\providecommand{\JournalTitle}[1]{#1}
\renewcommand{\refname}{References and Notes}
\renewenvironment{abstract}{\noindent}{\par}
\renewcommand{\PaperTableStyle}{%
    \centering
    \fontsize{9}{11}\selectfont
    \setlength{\tabcolsep}{3pt}%
    \renewcommand{\arraystretch}{1.10}%
}
\hypersetup{%
    pdftitle={Pushing the accuracy-cost frontier of machine-learning interatomic potentials},
    pdfauthor={Tiancheng Li; Wentao Li; Anyang Peng; Jianming Xue; Linfeng Zhang; Duo Zhang; Han Wang}
}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\setcounter{secnumdepth}{3}
\frenchspacing
\raggedbottom
\sloppy
\onehalfspacing
\begin{document}
\input{front_matter.tex}
\clearpage
\linenumbers
"""
    preamble = preamble.replace(r"\input{front_matter.tex}", expand(PACKAGE / "front_matter.tex"))
    main = "\n".join(expand(ROOT / f"chap/{name}.tex") for name in (
        "introduction", "results", "discussion", "methods"
    ))
    main = main.replace(r"\section{Methods}", r"\section{Materials and Methods}", 1)
    declarations = r"""
\clearpage
\nolinenumbers
\bibliographystyle{science_advances}
\bibliography{references}
\section*{Acknowledgments}
\paragraph*{Funding:}
""" + body("chap/funding.tex") + r"""
\paragraph*{Author contributions:}
""" + body("chap/author_contributions.tex") + r"""
\paragraph*{Competing interests:}
""" + body("chap/competing_interests.tex") + r"""
\paragraph*{Data and materials availability:}
""" + body("chap/data_availability.tex").replace(r"\section{Code availability}", "")
    supplementary = expand(ROOT / "chap/sm.tex")
    start = supplementary.index(r"\section{Mathematical formulation, operators and proofs}")
    supplementary = supplementary[start:]
    counts = {
        "main_figures": main.count(r"\begin{figure}"),
        "main_tables": main.count(r"\begin{table}"),
        "supplementary_figures": supplementary.count(r"\begin{figure}"),
        "supplementary_tables": supplementary.count(r"\begin{table}"),
    }
    contents = (
        "Supplementary Text\n\n"
        f"Fig. S1\n\nTables S1 to S{counts['supplementary_tables']}\n\n"
    )
    declarations += "\n\\subsection*{Supplementary Materials}\n" + contents
    supplement_header = r"""
\clearpage
\typeout{SCIADV-MAIN-PAGES:\number\numexpr\value{page}-1\relax}
\singlespacing
\setcounter{page}{1}
\renewcommand{\thepage}{S\arabic{page}}
\renewcommand{\thefigure}{S\arabic{figure}}
\renewcommand{\thetable}{S\arabic{table}}
\renewcommand{\thesection}{S\arabic{section}}
\renewcommand{\theequation}{S\arabic{equation}}
\renewcommand{\theHfigure}{supp.\arabic{figure}}
\renewcommand{\theHtable}{supp.\arabic{table}}
\renewcommand{\theHsection}{supp.\arabic{section}}
\renewcommand{\theHequation}{supp.\arabic{equation}}
\setcounter{figure}{0}
\setcounter{table}{0}
\setcounter{section}{0}
\setcounter{equation}{0}
\begin{center}
{\Large\bfseries Supplementary Materials for\par}
\vspace{0.5em}
{\large\bfseries Pushing the accuracy--cost frontier of machine-learning interatomic potentials\par}
\vspace{1em}
Tiancheng Li, Wentao Li, Anyang Peng, Jianming Xue$^{*}$, Linfeng Zhang$^{*}$, Duo Zhang$^{*}$, Han Wang$^{*}$\par
\vspace{0.5em}
\small $^{*}$Corresponding authors: jmxue@pku.edu.cn; linfeng.zhang.zlf@gmail.com; zhduodyx@pku.edu.cn; wang\_han@iapcm.ac.cn.
\end{center}
\subsection*{This PDF file includes:}
""" + contents + r"""
Reference numbers refer to the reference list in the main manuscript.
\clearpage
\linenumbers
"""
    text = preamble + main + declarations + supplement_header + supplementary + "\n\\end{document}\n"
    counts["references"] = prepare_references(text)
    (BUILD / "manuscript.tex").write_text(text)
    shutil.copyfile(PACKAGE / "science_advances.bst", BUILD / "science_advances.bst")
    for relative in dict.fromkeys(re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text)):
        destination = BUILD / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)
    return counts


def export(counts: dict[str, int]) -> None:
    """Validate compilation and export the upload PDFs and source archive."""
    log = (BUILD / "manuscript.log").read_text()
    problems = re.findall(
        r"^.*(?:LaTeX Warning:|Overfull|Undefined control sequence|multiply defined).*$",
        log,
        flags=re.MULTILINE,
    )
    if problems:
        raise ValueError("Resolve manuscript diagnostics before export:\n" + "\n".join(problems))
    boundary = re.search(r"SCIADV-MAIN-PAGES:(\d+)", log)
    if boundary is None:
        raise ValueError("The compiled log does not contain the manuscript/SI page boundary.")
    main_pages = int(boundary.group(1))
    with fitz.open(BUILD / "manuscript.pdf") as combined:
        if not 0 < main_pages < len(combined):
            raise ValueError(f"Invalid page boundary: {main_pages} of {len(combined)}")
        if "Supplementary Materials for" not in combined[main_pages].get_text():
            raise ValueError("The supplementary title does not match the split boundary.")
        for name, start, stop in (
            ("main_submission.pdf", 0, main_pages),
            ("supplementary_materials.pdf", main_pages, len(combined)),
        ):
            with fitz.open() as part:
                part.insert_pdf(combined, from_page=start, to_page=stop - 1, links=True)
                part.set_metadata(combined.metadata)
                part.save(PACKAGE / name, garbage=4, deflate=True)
        counts.update({"main_pages": main_pages, "supplementary_pages": len(combined) - main_pages})
    shutil.copyfile(BUILD / "manuscript.pdf", PACKAGE / "combined_manuscript.pdf")
    shutil.copyfile(BUILD / "cover_letter.pdf", PACKAGE / "cover_letter.pdf")
    with ZipFile(PACKAGE / "manuscript_source.zip", "w", ZIP_DEFLATED) as archive:
        for name in ("manuscript.tex", "references.bib", "science_advances.bst", "manuscript.bbl"):
            archive.write(BUILD / name, name)
        for path in sorted((BUILD / "fig").rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(BUILD))
    (BUILD / "verification.json").write_text(json.dumps(counts, indent=2) + "\n")


def main() -> None:
    """Assemble, compile, and export the Science Advances submission files."""
    counts = assemble()
    command = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error"]
    subprocess.run(command + ["manuscript.tex"], cwd=BUILD, check=True)
    subprocess.run(command + ["-outdir=build", "cover_letter.tex"], cwd=PACKAGE, check=True)
    export(counts)
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
