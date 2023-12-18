#!/usr/bin/env python

# Copyright 2023 Population Health Sciences, German Center for Neurodegenerative Diseases (DZNE)
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from __future__ import print_function
from .fs_pipeline import create_fs_pipeline 

from nipype import config, logging

#import logging as lgng

import os, sys,glob
import argparse
from itertools import chain


def create_anat_pipeline(scans_dir, work_dir, output_dir, subject_ids, nthreads, reconargs,
                        useT2=False, hsfsT1=False, hsfsT2=False, hsfsT1T2=False,
                        wfname='fs_pipeline'):

    fswf = create_fs_pipeline(scans_dir, subject_ids, work_dir, output_dir, nthreads, reconargs, useT2, hsfsT1, hsfsT2, hsfsT1T2, wfname)
    
    #fswf.inputs.inputnode.subject_ids = subject_ids
    
    return fswf
    
    
def main():
    """
    Command line wrapper for preprocessing data
    """
    descr = 'Run FS pipelines for Structural MRI data (T1, T2).'
    epilogstr = 'Example-1: {prog} -s ~/data/scans -w ~/data/work -p 2 -o ~/data/outputs ' \
                '[--subjects [subjid1 subjid2...] ] \n' \
                'nExample-2: {prog} -s ~/data/scans -w ~/data/work -o ~/data/outputs -p 10 -a [3T hires ...] '\
                ' -fT1T2 \n\n'

    parser = argparse.ArgumentParser(description=descr,
                                     epilog=epilogstr.format(prog=os.path.basename\
                                             (sys.argv[0])),\
                                     formatter_class=argparse.\
                                     RawTextHelpFormatter)

    parser.add_argument('-s', '--scansdir', help='Scans directory where data' \
                        ' is already downloaded for each subject and '\
                          'has T1 and T2 scans.', required=True)

    parser.add_argument('-w', '--workdir', help='Processing directory for the workflow where data' \
                        ' is processed for each subject.', required=True)

    parser.add_argument('-o', '--outputdir', help='Freesurfer outputs aka SUBJECTS_DIR',required=True)

    parser.add_argument('--subjects', help='One or more subject IDs'\
                        '(space separated), if omitted, all subjects in the -s scans directory are processed.', \
                        default=None, required=False, nargs='+', action='append')
    parser.add_argument('-a','--reconargs', help='recon-all additional args e.g -a 3T',
                        action='store', nargs='*')
    
    parser.add_argument('-b', '--debug', help='debug mode', action='store_true', default=False)
    
    parser.add_argument('-p', '--processes', help='parallel processes', \
                        default=1, type=int)
    
    parser.add_argument('-t', '--threads', help='openmp/ITK threads', default=1,\
                        type=int)
    
    parser.add_argument('-m', '--memory', help='Max memory in GBs for the WF', default=64,\
                        type=int)

    parser.add_argument('-u', '--useT2', action='store_true',help='Use T2 for surface refinement',\
                        required=False, default=False)
    
    parser.add_argument('-fT1', '--hsfsT1',action='store_true',help='Run hippocampal-subfields-T1'\
                        ' module using only T1 volume', required=False, default=False)

    parser.add_argument('-fT2', '--hsfsT2',action='store_true',help='Run hippocampal-subfields-T2'\
                        ' module using only T2 volume', required=False, default=False)

    parser.add_argument('-fT1T2', '--hsfsT1T2',action='store_true',help='Run hippocampal-subfields-T1T2'\
                        ' module using both T1 and T2 volumes', required=False, default=False)
    
    parser.add_argument('-n', '--wfname', help='Pipeline workflow name, default fs_pipeline.', 
                        default='fs_pipeline')
    
    args = parser.parse_args()
    
    scans_dir = os.path.abspath(os.path.expandvars(args.scansdir))
    if not os.path.exists(scans_dir):
        raise IOError("Scans directory does not exist.")
        
    
    subject_ids = []
    
    if args.subjects:
        subject_ids = list(chain.from_iterable(args.subjects))
    else:
        subject_idsdir = glob.glob(scans_dir.rstrip('/') + '/*')
        for sidir in subject_idsdir:
            subject_ids.append(os.path.basename(sidir.rstrip('/')))


    useT2 = args.useT2
    
    hsfsT1 = args.hsfsT1
    hsfsT2 = args.hsfsT2
    hsfsT1T2 = args.hsfsT1T2

    nthreads = args.threads
    wfname = args.wfname

    print("Creating fs pipeline workflow...")
    work_dir = os.path.abspath(os.path.expandvars(args.workdir))
    output_dir = os.path.abspath(os.path.expandvars(args.outputdir))

    if not os.path.exists(work_dir):
        os.makedirs(args.workdir)

    if not os.path.exists(output_dir):
        os.makedirs(args.outputdir)

    reconargs = '-time'
    if args.reconargs:
        argstr = ' -'.join(args.reconargs)
        reconargs = '-time -%s' % argstr


    config.update_config({
        'logging': {'log_directory': args.workdir, 'log_to_file': True},
        'execution': {'job_finished_timeout' : 65,
                      'poll_sleep_duration' : 30,
                      'hash_method' : 'content',
                      'local_hash_check' : False,
                      'stop_on_first_crash':False,
                      'crashdump_dir': args.workdir,
                      'crashfile_format': 'txt'
                       },
                       })

    #config.enable_debug_mode()
    logging.update_logging(config)

    anat_pipeline = create_anat_pipeline(scans_dir, work_dir, output_dir, subject_ids,nthreads,
                                           reconargs, useT2, hsfsT1, hsfsT2, hsfsT1T2,
                                           wfname=wfname)
    
    # Visualize workflow
    if args.debug:
        anat_pipeline.write_graph(graph2use='colored', simple_form=True)

     
    anat_pipeline.run(
                            plugin='MultiProc', 
                            plugin_args={'n_procs' : args.processes
                            }
                           )
    

    print('Done FS pipeline!!!')

    
if __name__ == '__main__':
    sys.exit(main())
