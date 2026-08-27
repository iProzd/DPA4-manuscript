# Cover letter

Dear Editors,

Please consider our manuscript, "Pushing the accuracy–cost frontier of machine-learning interatomic potentials," for publication as an Article in *Nature Communications*.

Equivariant machine-learning interatomic potentials achieve high accuracy against quantum-mechanical reference calculations, but their computational cost remains a barrier to routine energy-conserving training and large-scale deployment. We introduce DPA4, a family of six conservative SE(3)-equivariant models spanning 0.48 to 25.2 million parameters. Its edge-local interaction couples different angular degrees without incurring the full cost of SO(3) tensor products, while a compiler-compatible energy-to-force path accelerates conservative training. Together, these designs target predictive accuracy, inference throughput, training efficiency and parameter efficiency.

In the compliant Matbench Discovery leaderboard comparison, DPA4-Pro ranks first in all four reported metrics. In a common-protocol comparison with ten representative compliant baselines, all five evaluated DPA4 variants are non-dominated in combined performance score (CPS) and saturated inference throughput among the 15 models tested; DPA4-Plus lies within 0.001 CPS of the strongest baseline while achieving 11.9-fold higher throughput. The advantage extends across materials and molecular benchmarks: DPA4-Pro has the lowest energy error among the models compared on OMat24 and lower total-energy and force errors than UMA-M-1.1, the strongest conservative baseline in our OMol25 comparison, while DPA4-Plus attains the lowest aggregate energy and force errors in our SPICE-MACE-OFF comparison. These results use conservative energy-gradient training alone, without auxiliary denoising or direct-force pretraining; in a controlled ablation, combining graph compilation with bf16 automatic mixed precision provides a 3.1-fold wall-clock speedup over the uncompiled FP32 baseline.

We believe this work is appropriate for the diverse readership of *Nature Communications* because it presents a general architectural and systems advance rather than an improvement restricted to a single benchmark. Its evaluation across four datasets spanning inorganic crystals and organic molecules connects machine learning, materials science, computational chemistry and scientific computing. The scale-spanning model family provides explicit accuracy–cost operating points for structure relaxation, high-throughput screening and molecular-dynamics workflows.

This manuscript reports original work and is not under consideration elsewhere. No related manuscript from the authors is under review or in press. A preprint is available at https://arxiv.org/abs/2606.02419. We have not had any prior discussions about this work with a *Nature Communications* editor.

We do not provide suggested reviewers. We request the exclusion of Gábor Csányi (University of Cambridge, gc121@cam.ac.uk) and Shyue Ping Ong (University of California San Diego, ongsp@eng.ucsd.edu) to avoid potential professional conflicts arising from their groups' development of closely related machine-learning interatomic-potential technologies.

Thank you for considering our manuscript.

Corresponding author for editorial correspondence:
Han Wang
HEDPS, CAPT, College of Engineering, Peking University, Beijing 100871, P. R. China
National Key Laboratory of Computational Physics, Institute of Applied Physics and Computational Mathematics, Fenghao East Road 2, Beijing 100094, P. R. China
Email: wang_han@iapcm.ac.cn
