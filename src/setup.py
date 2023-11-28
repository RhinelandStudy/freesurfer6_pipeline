#!/usr/bin/env python

"""
#Rhineland Study MRI Post-processing pipelines
#rs_fs_pipeline: Anatomical structural scans processing pipeline with Freesurfer
"""
import os
import sys
from glob import glob
if os.path.exists('MANIFEST'): os.remove('MANIFEST')


def main(**extra_args):
    from setuptools import setup
    setup(name='fs_pipeline',
          version='1.0.0',
          description='RhinelandStudy Freesurfer Pipeline',
          long_description="""RhinelandStudy processing for structural T1/T2/Flair scans """ + \
          """It also offers support for performing additional option to run hippocampal-subfields segmentation (requiers MCRv8) and extracting additional statistics from FS segmentations.""" + \
          """More pipelines addition is work in progress.""",
          author= 'shahidm',
          author_email='mohammad.shahid@dzne.de',
          url='http://www.dzne.de/',
          packages = ['fs_pipeline'],
          entry_points={
            'console_scripts': [
                             "run_fs_pipeline=fs_pipeline.run_fs_pipeline:main",
                             "run_fs_qc_creator=fs_pipeline.run_fs_qc_creator:main"
                              ]
                       },
          license='DZNE License',
          classifiers = [c.strip() for c in """\
            Development Status :: 1.0 
            Intended Audience :: Developers
            Intended Audience :: Science/Research
            Operating System :: OS Independent
            Programming Language :: Python
            Topic :: Software Development
            """.splitlines() if len(c.split()) > 0],    
          maintainer = 'RheinlandStudy MRI-IT group, DZNE',
          maintainer_email = 'mohammad.shahid@dzne.de',
          package_data = {'':['']}, 
          install_requires=["nipype","pycrypto","psycopg2","pyxnat"],
          **extra_args
         )

if __name__ == "__main__":
    main()

