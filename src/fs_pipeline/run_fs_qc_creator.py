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
from nipype import config, logging

import os, sys,re
import argparse
from itertools import chain

from .fs_qc_creator import create_qc_wf
    
def main():
    """
    Command line wrapper for uploading data
    """
    descr = 'QC Snapshots creator from results obtained with Freesurfer.'
    epilogstr = 'Example-1: {prog}  -o ~/data/outsubjectsdir  ' \
                '[--subjects [subjid1 subjid2...] ] -w ~/data/work [-j] [-z] \n' \
                'nExample-2: {prog} -o ~/data/outputsubjectsdir  -w ~/data/work -p 10 '\
                '\n\n'

    parser = argparse.ArgumentParser(description=descr,
                                     epilog=epilogstr.format(prog=os.path.basename\
                                             (sys.argv[0])),\
                                     formatter_class=argparse.\
                                     RawTextHelpFormatter)

    parser.add_argument('-w', '--workdir', help='Processing directory where workflow data' \
                        ' is processed for each subject.', required=True)

    parser.add_argument('-o', '--outputdir', help='Freesurfer outputs direcroty (subjects_dir)',required=True)

    parser.add_argument('--subjects', help='One or more subject IDs'\
                        '(space separated).', \
                        default=None, required=False, nargs='+', action='append')
        
    parser.add_argument('-p', '--processes', help='parallel processes', \
                        default=1, type=int)
    
        
    args = parser.parse_args()
    
    
    output_dir = os.path.abspath(os.path.expanduser(args.outputdir))
    if not os.path.exists(output_dir):
        raise ValueError("Error. %s directory doesn't exist." % output_dir)
                
    subject_ids = []
    #explicity check for uuid like subjects and freesurfer output directory
    if args.subjects:
        subject_id_list = list(chain.from_iterable(args.subjects))
        for subjid in subject_id_list:
            subdir_list = os.listdir( os.path.join(output_dir, subjid))
            if set(['mri', 'label','stats', 'surf']).issubset(subdir_list):
                subject_ids.append(subjid)
            else:
                print("Warning: %s doesn't look like a Freesurfer output directory, skipped.\n" % subjid)
  
    else:
        subject_id_list = [s.rstrip('/') for s in os.listdir(output_dir) if re.match(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', s)]
        for subjid in subject_id_list:
            subject_dir=os.path.join(output_dir, subjid)
            if os.path.isdir(subject_dir):
                subdir_list = os.listdir( subject_dir )
                if set(['mri', 'label','stats', 'surf']).issubset(subdir_list):
                    subject_ids.append(subjid)
                else:
                    print("Warning: %s doesn't look like a Freesurfer output directory, skipped.\n" % subjid) 
                
    if len(subject_ids) ==0:
	raise ValueError("Error: No subject ids found in %s."% output_dir)

    work_dir = os.path.abspath(os.path.expanduser(args.workdir))
    if not os.path.exists(work_dir):
        os.makedirs(args.workdir)
        
        

    config.update_config({
        'logging': {'log_directory': work_dir, 'log_to_file': True},
        'execution': {'job_finished_timeout' : 65,
                      'poll_sleep_duration' : 30,
                      'hash_method' : 'content',
                      'local_hash_check' : False,
                      'stop_on_first_crash':False,
                      'crashdump_dir': work_dir,
                      'crashfile_format': 'txt'
                       },
                       })

    #config.enable_debug_mode()
    logging.update_logging(config)
        

    cwf = create_qc_wf(output_dir, subject_ids, work_dir, name="fs_qc_snapshot")
     
    cwf.run(plugin='MultiProc',   plugin_args={'n_procs' : args.processes  } )
    
    print('Done FS QC Snapshots creation!!!')

    
if __name__ == '__main__':
    sys.exit(main())
