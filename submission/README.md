# Science Advances submission workspace

This directory contains the current Research Article submission package for Science Advances. The title, scientific text, numerical results, author order, and correspondence designations are taken from the manuscript. The abstract has an explicitly authorized minimal length reduction; other scientific content is not rewritten during submission preparation.

## Upload files

- `main_submission.pdf`: main manuscript, figures, tables, unified references, and declarations.
- `supplementary_materials.pdf`: supplementary text, Fig. S1, and Tables S1 to S24, using the same reference numbers as the main manuscript.
- `combined_manuscript.pdf`: main manuscript followed by the Supplementary Materials, for a combined-PDF field.
- `cover_letter.pdf`: one-page cover letter signed by Han Wang.
- `manuscript_source.zip`: portable LaTeX, bibliography, style, and the figure files actually used.

The files are local preparation artifacts. The CTS draft ID is **aem8043**, with status **Not Submitted** as observed on 2026-09-28. No manuscript files have been uploaded yet.

## Editable sources

- Scientific text: the existing `../chap/` files.
- Bibliographic metadata: `../ref.bib`; complete author lists are stored here, while the bibliography style controls abbreviation.
- Title page and author formatting: `front_matter.tex`, which directly includes the original `../chap/abstract.tex`.
- Cover letter: `cover_letter.tex`.
- Author/contact memo: `authors.md`.
- Previously approved reviewer exclusions: `reviewer_exclusions.md`.
- Build and export: `build.py`.

There is no separate rewritten abstract or reference-override database. Eight incomplete author lists in the original bibliography have been completed from the sources listed below. Other bibliographic fields and the paper's scientific text are retained.

## Portal metadata

Title:

```text
Pushing the accuracy–cost frontier of machine-learning interatomic potentials
```

Short title:

```text
Accurate and efficient interatomic potentials
```

Teaser (113 characters including the final period; for the submission form):

```text
DPA4 combines rotational symmetry and conservative training to improve the accuracy and cost of atomistic models.
```

Journal: Science Advances. Article type: Research Article. Primary editorial contact: Han Wang.

## Requirements and remaining items

The [official author guide](https://www.science.org/content/page/science-advances-information-authors?referrer=https%3A%2F%2Fcn.bing.com%2F) was read directly in Safari on 2026-09-28 after non-GUI retrieval returned HTTP 403. The user completed registration and logged in through Safari at the [AAAS submission portal](https://cts.sciencemag.org/scc/).

The accessible [AAAS-sourced Science-family template](https://www.overleaf.com/latex/templates/science-and-science-family-journals-template/ptkzkvxkznbh) supports the formatting used here: numbered parenthetical citations, references before acknowledgments, and a shared reference list for the main text and supplement. The package retains the manuscript's mathematical and table packages for initial submission.

The official abstract limit is 150 words. At the user's explicit request, the first background sentence was shortened and the final summary sentence removed; the five intervening sentences remain unchanged. An independent subagent reviewed the wording and scope. TeXcount reports 148 words, compared with 186 in the previous abstract. The preparation script directly includes `../chap/abstract.tex` and performs no further shortening.

The official guide requires five suggested reviewers with names, affiliations and email addresses, and permits up to three exclusions. It also requests a Deputy or Section Editor suggestion and an Associate Editor suggestion. No suggested reviewers or editors have been approved or entered. The first author and corresponding authors require personally authenticated ORCID records; authors must authenticate their own IDs.

The official guide confirms a unified reference list with complete author lists for journal citations, and single-spaced supplementary text and tables. The combined PDF must include the main text, figures, tables and Supplementary Materials; upload the supplementary PDF separately as well. The package applies these formatting requirements without rewriting scientific content.

Before final submission, resolve reviewer/editor suggestions and ORCID authentication; refresh any related-manuscript disclosure; resolve payment coverage if requested; and inspect the portal-generated proof.

## Rebuild and verification

Run from the repository root:

```sh
/Users/outisli/Software/miniforge3/envs/dpmd/bin/python submission/build.py
```

The script uses the existing environment's BibTeX parser and PyMuPDF, invokes LaTeX/BibTeX, and exports the PDFs and portable source archive. The ignored `build/` directory holds intermediate files and `verification.json`. Export rejects unresolved references, overflowing text, and LaTeX warnings. Visual inspection must follow a rebuild.

Verified on 2026-09-28: main manuscript 47 pages, single-spaced Supplementary Materials 31 pages, cover letter 1 page; 4 main figures, 5 main tables, 1 supplementary figure, 24 supplementary tables, and 62 references. The approved abstract and scientific sections match the manuscript sources. All eight bibliography changes affect only author fields. The current submission build has no unresolved citations/references or LaTeX layout warnings. Both `../main.tex` and `../main_arxiv.tex` also compile; the latter reports underfull spacing warnings.

## Bibliography provenance

Only the author fields of these eight entries were completed on 2026-09-28:

| Citation key | Metadata source |
| --- | --- |
| `zhang2018end` | [arXiv:1805.09003](https://arxiv.org/abs/1805.09003) |
| `batatia2023foundation` | [arXiv:2401.00096](https://arxiv.org/abs/2401.00096) |
| `jain2013materials` | [Crossref: 10.1063/1.4812323](https://api.crossref.org/works/10.1063/1.4812323) |
| `eastman2023spice` | [Crossref: 10.1038/s41597-022-01882-6](https://api.crossref.org/works/10.1038/s41597-022-01882-6) |
| `smith2020psi4` | [Crossref: 10.1063/5.0006002](https://api.crossref.org/works/10.1063/5.0006002); the III suffixes for Schaefer and DePrince are also confirmed in the [Psi4 official bibliography](https://psicode.org/psi4manual/1.10.x/bibliography.html#smith-2020-184108) |
| `yang2024mattersim` | [arXiv:2405.04967](https://arxiv.org/abs/2405.04967) |
| `zhang2024dpa2` | [Crossref: 10.1038/s41524-024-01493-2](https://api.crossref.org/works/10.1038/s41524-024-01493-2) |
| `levine2025open` | [arXiv:2505.08762](https://arxiv.org/abs/2505.08762) |

The bibliography style is a renamed LPPL-licensed derivative of this [public Science-family style copy](https://gitlab.com/gain4crops/2024-paper/-/raw/main/sciencemag.bst), with automatic author truncation removed. Original copyright and license notices are retained.
