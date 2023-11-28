# freesurfer6_pipeline
Run Freesurfer version 6 recon-all workflow with or without hippocampal subfields segmentations and collect all stats outputs in a single file in json format.

## Build docker image

```bash

docker build -t freesurfer6_pipeline -f docker/Dockerfile .

```

## Or pull from docker hub
```
docker pull dznerheinlandstudie/rheinlandstudie:freesurfer6_pipeline
```

## Run pipeline: 

### Using Docker

The pipeline can be run with docker by running the container as follow:


```bash

 docker run --rm -v /path/to/fs_license.txt:/opt/freesurfer/license.txt \
                 -v /path/to/input_scans:/input \
                 -v /path/to/work_folder:/work \
                 -v /path/to/fsoutput:/output \
        dznerheinlandstudie/rheinlandstudie:freesurfer6_pipeline \
        run_fs_pipeline \
        -s /input \
        --subjects test_subject_01 \
        -w /work \
        -o /output \ 
        -a 3T qcache -fT1T2 -p 4 -t 2

```

Command line options are described briefly if the pipeline is started with ```-h ``` option.


### Using Singularity

The pipeline can be run with Singularity by running the singularity image as follow:

```bash

export SINGULARITY_DOCKER_USERNAME=username
export SINGULARITY_DOCKER_PASSWORD=password


singularity build freesurfer6_pipeline.sif docker://dznerheinlandstudie/rheinlandstudie:freesurfer6_pipeline

```

When the singularity image is created, then it can be run as follow:

```bash

singularity run -B /path/to/fs_license.txt:/opt/freesurfer/license.txt \
                -B /path/to/input_scans:/input \
                -B /path/to/work_folder:/work \
                -B /path/to/fsoutput:/output \
            freesurfer6_pipeline.sif run_fs_pipeline \
            -s  /input \
        --subjects test_subject_01 \
        -w /work \
        -o /output \
        -a 3T qcache -fT1T2 -p 4 -t 2
```



