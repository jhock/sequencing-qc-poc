// 1. Define Parameters relative to the root directory
params.input = "$projectDir/data/samples.csv"
params.output_dir = "$projectDir/results"

process VALIDATE_SAMPLES {
    publishDir params.output_dir, mode: 'copy'

    input:
    path input_csv

    output:
    path "validated_samples.csv"

    script:
    """
    # Execute the python script located in the scripts/ folder
    python3 ${projectDir}/bin/validate_samples.py --input ${input_csv} --output validated_samples.csv
    """
}

workflow {
    input_ch = Channel.fromPath(params.input)
    VALIDATE_SAMPLES(input_ch)
}