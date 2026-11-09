# Sample metadata rules

1. `sample_id` must be present and unique.
2. `sample_id` must match `AG1-[0-9]{3}`.
3. `species` must use the accepted scientific name `Zea mays`.
4. `tissue` must be one of: `leaf`, `root`, or `seed`.
5. `genotype` must not be empty.
6. `treatment` must be either `control` or `edited`.
7. Both `read_1` and `read_2` are required for paired-end samples.
8. Read 1 filenames must end in `_R1.fastq.gz`.
9. Read 2 filenames must end in `_R2.fastq.gz`.
10. The sample identifier in each FASTQ filename must match `sample_id`.
