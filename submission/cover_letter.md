# Cover letter

Dear Editors,

Please consider our manuscript, "Pushing the accuracy–cost frontier of machine-learning interatomic potentials," for publication as an Article in *Nature Communications*.

High-accuracy equivariant machine-learning interatomic potentials remain expensive to train and deploy. We introduce DPA4, a family of six conservative SE(3)-equivariant models that combines a more expressive edge-local interaction with a compiler-compatible energy-to-force training path. The architecture is designed to improve the accuracy–cost trade-off without relying on auxiliary denoising or direct-force pretraining.

The main evidence is a common-protocol accuracy–throughput comparison on Matbench Discovery: all five evaluated DPA4 variants are non-dominated among the 15 models tested, and DPA4-Plus reaches an overall leaderboard score comparable to that of the strongest baseline at 11.9-fold higher saturated throughput. Evaluations on OMat24, OMol25 and SPICE-MACE-OFF show that the same design retains leading accuracy across inorganic crystals and organic molecules. A controlled ablation further shows that compiled mixed-precision execution accelerates conservative training by 3.1-fold relative to the uncompiled FP32 baseline.

We believe this work is appropriate for the diverse readership of *Nature Communications* because it addresses a general problem shared by machine learning, materials science, computational chemistry and scientific computing: making accurate atomistic models practical for structure relaxation, high-throughput screening and molecular dynamics. The scale-spanning DPA4 family provides users with explicit accuracy–cost operating points rather than a single fixed computational regime.

This manuscript reports original work and is not under consideration elsewhere. No related manuscript from the authors is under review or in press. A preprint is available at https://arxiv.org/abs/2606.02419. We have not had any prior discussions about this work with a *Nature Communications* editor.

We do not provide suggested reviewers. We request the exclusion of Gábor Csányi (University of Cambridge, gc121@cam.ac.uk) and Shyue Ping Ong (University of California San Diego, ongsp@eng.ucsd.edu) to avoid potential professional conflicts arising from their groups' development of closely related machine-learning interatomic-potential technologies.

Thank you for considering our manuscript.

Corresponding author for editorial correspondence:
Han Wang
HEDPS, CAPT, College of Engineering, Peking University, Beijing 100871, P. R. China
National Key Laboratory of Computational Physics, Institute of Applied Physics and Computational Mathematics, Fenghao East Road 2, Beijing 100094, P. R. China
Email: wang_han@iapcm.ac.cn
