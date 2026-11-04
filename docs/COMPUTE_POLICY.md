# Compute policy

User instruction, 20 October 2026. This policy governs authorized jobs; it does not authorize a solver run.

Before each new CPU/GPU job, inspect iis-lab, mdx1 and mdx2 through their existing SSH aliases. Compare CPU count, load per core, measured idle time, processes, available RAM, GPU model/free VRAM/utilization and software support. Save the dated snapshot in the project state folder and the run history in 07_Team. Respect schedulers and other users' allocations. A direct user host instruction takes priority.

Use every free compatible GPU for large numerical work when the implementation supports it. Measure one representative unit on GPU and CPU and select the faster device, or both. Geometry parsing and other CPU-only tools should use useful CPU parallelism rather than claim GPU acceleration.

Submit independent units to one pool, longest first, sized to free cores and measured memory needs. For process pools, set OMP_NUM_THREADS=1, OPENBLAS_NUM_THREADS=1 and MKL_NUM_THREADS=1 so workers and threads match free capacity. Fix idle compatible resources and serial bottlenecks before the full batch. Estimate total work from the measured unit rate and checkpoint each completed unit.

Do not set wall-clock or runtime limits. A scientific budget defines candidates, cases, seeds or folds, not elapsed time. Physical RAM/VRAM is the hard resource limit; do not invent fixed GiB caps. Do not stop or reject a healthy experiment based on remaining disk or swapping activity.

Stage exact inputs and isolated compatible software. Record versions, input revision, commands and process/session IDs. Verify live logs and output before reporting execution status. Reassess resources at useful checkpoints; preserve restart state before a justified migration and never interrupt unrelated jobs.

Infrastructure interruption or a code bug is recovered from checkpoints with the same method once its cause is fixed. Record the recovery; it does not require a new scientific approval. A method change belongs in the study plan.

Cleanup follows the current user authorization: first inspect processes and dependencies, identify obsolete generated outputs, preserve source inputs and the evidence needed to interpret prior claims, then record exactly what was removed. Do not infer that an old instruction to retain full checkpoints still governs after the user explicitly authorizes their removal.
