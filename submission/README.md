# Nature Communications submission workspace

This directory contains working submission files for the DPA4 manuscript.
It is not ready for upload until every blocking item below is resolved.

## Official sources

- [How to submit](https://www.nature.com/ncomms/submit/how-to-submit)
- [Article requirements](https://www.nature.com/ncomms/submit/article)
- [Editorial process](https://www.nature.com/ncomms/submit/editorial-process)
- [Applied science and engineering research](https://www.nature.com/ncomms/submit/applied-science-research)
- [Authorship policy](https://www.nature.com/nature-portfolio/editorial-policies/authorship)
- [Competing interests policy](https://www.nature.com/nature-portfolio/editorial-policies/competing-interests)
- [Data and code policy](https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards)
- [Artificial intelligence policy](https://www.nature.com/nature-portfolio/editorial-policies/ai)
- [Open access fees and funding](https://www.nature.com/ncomms/open-access)

## Current submission files

- `main_submission.tex` and `main_submission.pdf`: main manuscript only.
- `supplementary_information.tex` and `supplementary_information.pdf`: standalone Supplementary Information with independent page numbering and Supplementary References.
- `cover_letter.md`: reviewed cover-letter draft for the submission system; the signatory is intentionally deferred until author confirmation.
- `reviewer_exclusions.md`: verified reviewer-exclusion names, affiliations, email addresses and rationale.

The repository entry points `main.tex` and `main_arxiv.tex` remain the combined manuscript-and-Supplementary-Information builds used for internal verification and arXiv preparation.

## Verified format status

- Article title: 8 words; the journal recommends no more than 15.
- Abstract: 185 words and no references; the journal limit is 200 words.
- Main text: approximately 5,921 words excluding Methods, references and legends; the journal recommends approximately 5,000.
- Methods: approximately 5,618 words; the journal states that Methods are typically below 3,000 words, but initial submissions are format-flexible.
- Main display items: 9 figures and tables; the journal allows up to 10 as a guide.
- Main references: 56 in the standalone manuscript; the journal recommends no more than 70.
- Both PDFs are below the 30 MB per-file limit.
- The standalone Supplementary Information uses its own reference list, numbered from 1.
- The current builds contain no LaTeX errors, unresolved references or citations, multiply defined labels, or overfull boxes.
- The manuscript is publicly available as [arXiv:2606.02419](https://arxiv.org/abs/2606.02419), first submitted on 1 June 2026 and last revised as v4 on 20 August 2026. The arXiv author list matches the manuscript author list. The arXiv title is `DPA4: Pushing the Accuracy-Cost Frontier of Interatomic Potentials with EMFA SO(2) Convolution`.

## Confirmed submission metadata

- Submission title: `Pushing the accuracy–cost frontier of machine-learning interatomic potentials`.
- Submitting author: Tiancheng Li; the Nature Communications MTS account has been registered.
- Corresponding authors: Jianming Xue, Linfeng Zhang, Duo Zhang and Han Wang.
- Final author order: Tiancheng Li; Wentao Li; Anyang Peng; Jianming Xue; Linfeng Zhang; Duo Zhang; Han Wang.
- Equal-contribution and joint-supervision designations: none.
- Present-address statements: none required.
- Figure, schematic and table provenance: all are original author-created material; no third-party publication permissions are required.
- Competing Interests statement: `The authors declare no competing interests.`
- Funding statement: all confirmed grants are reported in a separate `Funding` section; no standalone Acknowledgments section is required.
- Author Contributions statement: drafted for all seven authors; final approval by every author remains required before submission.
- Generative-AI assistance: Cursor, Claude Code and Codex were used primarily for software development and to a lesser extent for language editing; the disclosure is included in the Methods section.
- Peer-review model: standard peer review.
- Prior discussion with a Nature Communications editor: none.
- Preprint: [arXiv:2606.02419](https://arxiv.org/abs/2606.02419); do not opt in to the In Review / Research Square service.
- Tiancheng Li ORCID: [0009-0009-2459-0635](https://orcid.org/0009-0009-2459-0635), publicly verified against the name Tiancheng Li.
- Related manuscripts: DPA4C and DPA4-Spin are not submitted, under review, accepted or in press; no related manuscript needs to be uploaded with this submission.
- Data and code restrictions: none arising from commercial, licensing or confidentiality constraints.
- Public checkpoints: the 20 trained DPA4 checkpoints used for the reported benchmarks are available at [AI Square](https://www.aissquare.com/models/detail?pageType=models&name=DPA4-Paper&id=436).
- Data and Code Availability statements are separate sections, following the Nature Communications manuscript checklist.
- No separate source-data workbook is planned for the initial submission; additional supporting data will be prepared only if requested by the editor.
- Reviewer exclusions: Gábor Csányi and Shyue Ping Ong, owing to potential professional conflicts arising from their groups' development of closely related machine-learning interatomic-potential technologies.
- Suggested reviewers: none; reviewer suggestions are optional, and only the two exclusions above will be provided.
- Cover letter: independently reviewed and revised; Han Wang is listed as the corresponding contact, while the signatory is intentionally deferred until final confirmation.

## Blocking manuscript content

- Obtain every author's approval of the Author Contributions statement.

## Information required from the authors

- ORCID for each corresponding author and, if available, every co-author.
- APC payer or institutional/funder coverage: pending confirmation from the authors or institution. The current listed APC is GBP 5,490, USD 7,350 or EUR 6,150, plus applicable taxes, determined at acceptance.
- Confirmation that all authors approve the manuscript, author order, contribution statement and submission.

## Submission-system gate

Before the final submit action:

1. Rebuild both PDFs from clean sources.
2. Run the LaTeX warning, reference and file-size checks.
3. Render every page and inspect the title page, tables, figures, equations, references and SI transitions.
4. Verify that title, abstract, authors, affiliations and statements match the MTS fields exactly.
5. Download and inspect the MTS-generated submission proof.
6. Obtain explicit author approval before the final submission click.
