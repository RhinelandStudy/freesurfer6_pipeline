#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""
Created on Tue Mar 16 09:57:31 2017

@author: shahidm
"""

import os
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as util
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.freesurfer import ReconAll, SegStats
from .reconall_hsfs import ReconAllHSFS
from .jsonify_stats import JsonifyStats
from nipype.interfaces.io import FreeSurferSource    
from .screenshot import create_mri_screenshots

def get_full_path(subjectid, data_dir, filepattern):
    
    import os,glob
    sfilename=None
    full_path=None
    sfilenames=glob.glob(os.path.join(data_dir,subjectid, filepattern))
    if len(sfilenames) >0:
        sfilename=sfilenames[0]
        if sfilename:
            full_path=os.path.join(data_dir,subjectid, sfilename)
            

    return full_path

def get_T2_path_tup(subjectid, data_dir,ID):
    import os, glob
    t2filetup=()
    t2filename=None
    
    t2filenames=glob.glob(os.path.join(data_dir, subjectid, '*T2*.nii.gz'))
    if len(t2filenames)>0:
        t2filename=t2filenames[0]
        if t2filename:
            full_path = os.path.join(data_dir,subjectid, t2filename)
            #the ID is the ID required to distinguish hsfsT2 or hsfsT1T2
            t2filetup=(full_path, ID)    
        
    return t2filetup

def get_summary_filename(subjectid,subjects_dir):
    
    import os
    
    return os.path.join(subjects_dir, subjectid, 'stats', 'wmgm.aseg.stats')

    
def create_fs_pipeline(scans_dir, subject_ids, work_dir, fs_base_sub_dir, nthreads, reconargs,
                         useT2=False, hsfsT1=False, hsfsT2=False,
                         hsfsT1T2=False, wfname='fs_pipeline'):
   
    awf = pe.Workflow(name=wfname)
    
    inputnode = pe.Node(interface=IdentityInterface(fields=['subject_ids']),
                        name='inputnode')
    inputnode.iterables = [('subject_ids', subject_ids)] 
    inputnode.inputs.subject_ids = subject_ids
    
    reconall = None
   
    subjectsdir = fs_base_sub_dir
 
    if useT2:
        reconall = pe.Node(interface=ReconAll(), name='reconall_wT2')
        
        reconall.inputs.use_T2=True

        awf.connect(inputnode, 'subject_ids', reconall, 'subject_id')
        awf.connect(inputnode, ('subject_ids', get_full_path, scans_dir,
                               "*T1*.nii.gz"), reconall, 'T1_files')
        
        awf.connect(inputnode, ('subject_ids', get_full_path, scans_dir,
                               "*T2*.nii.gz"), reconall, 'T2_file')
        
    else:
        reconall = pe.Node(interface=ReconAll(), name='reconall_T1')
        awf.connect(inputnode, 'subject_ids', reconall, 'subject_id')
        awf.connect(inputnode, ('subject_ids', get_full_path, scans_dir,
                               "*T1*.nii.gz"), reconall, 'T1_files')

    
    reconall.inputs.subjects_dir = subjectsdir
    reconall.inputs.directive = 'all'
    reconall.inputs.terminal_output='none'
    reconall.inputs.openmp=nthreads
    
    awf.base_dir = os.path.abspath(work_dir)
            
    reconall.inputs.args = reconargs


    #additional stats file from given ROI ids
    segstats = pe.Node(interface=SegStats(subjects_dir=subjectsdir), name='segstats')
    segstats.inputs.default_color_table = True
    segstats.inputs.segment_id = ['41','2','42','3','77']


    #collect results from all the stats files and put into a json file
    jsonify_stats = pe.Node(interface=JsonifyStats(), name='jsonifystats')
    jsonify_stats.inputs.subjects_dir = subjectsdir

    #qc snapshots
    qcsnapshots = pe.Node(interface=util.Function(input_names=['path_orig','path_aseg','out_dir','subject_id', 'num_slices','padd','spacing','image_extension'],
                                                  output_names=['dual_sagittal','dual_axial'],
                                                  function=create_mri_screenshots),name='create_qc_snapshots')

    qcsnapshots.inputs.out_dir=subjectsdir
    qcsnapshots.inputs.num_slices=60
    qcsnapshots.inputs.padd=4
    qcsnapshots.inputs.spacing=3
    qcsnapshots.inputs.image_extension='png'


    if hsfsT1 or hsfsT2 or hsfsT1T2:
        jsonify_stats.inputs.parse_hsfs=True
        
    
    if hsfsT1:
        reconall_hsfsT1 = pe.Node(interface=ReconAllHSFS(), name='reconall_hsfsT1')
        
        reconall_hsfsT1.inputs.subjects_dir = subjectsdir
        reconall_hsfsT1.inputs.terminal_output='none'
        reconall_hsfsT1.inputs.args = reconargs.replace('-qcache','')
        reconall_hsfsT1.inputs.hippocampal_subfields_T1 = True
        
        awf.connect(reconall, 'subject_id',   reconall_hsfsT1, 'subject_id')
        awf.connect(reconall, 'aseg',       qcsnapshots, 'path_aseg')
        awf.connect(reconall, 'orig',       qcsnapshots, 'path_orig')
        awf.connect(reconall, 'subject_id', qcsnapshots, 'subject_id')

        awf.connect(reconall_hsfsT1, 'aseg',  segstats, 'segmentation_file')
        awf.connect(reconall_hsfsT1, 'norm',  segstats, 'partial_volume_file')
        awf.connect(inputnode, ('subject_ids', get_summary_filename, subjectsdir),
                    segstats, 'summary_file')
        awf.connect(reconall_hsfsT1, 'subject_id',    jsonify_stats, 'subject_id')
        awf.connect(segstats,        'summary_file',  jsonify_stats, 'segstats_file')
        
    if hsfsT2:
        reconall_hsfsT2 = pe.Node(interface=ReconAllHSFS(), name='reconall_hsfsT2')

        reconall_hsfsT2.inputs.subjects_dir = subjectsdir
        reconall_hsfsT2.inputs.terminal_output='none'
        reconall_hsfsT2.inputs.args = reconargs.replace('-qcache','')
        reconall_hsfsT2.inputs.hippocampal_subfields_T1 = False
        

        awf.connect(reconall, 'subject_id', reconall_hsfsT2, 'subject_id')
        awf.connect(reconall, 'aseg',       qcsnapshots, 'path_aseg')      
        awf.connect(reconall, 'orig',       qcsnapshots, 'path_orig')
        awf.connect(reconall, 'subject_id', qcsnapshots, 'subject_id')

        awf.connect(inputnode, ('subject_ids', get_T2_path_tup, scans_dir,'T2'),
                    reconall_hsfsT2, 'hippocampal_subfields_T2')
        
        awf.connect(reconall_hsfsT2, 'aseg', segstats, 'segmentation_file')
        awf.connect(reconall_hsfsT2, 'norm', segstats, 'partial_volume_file')
        awf.connect(inputnode, ('subject_ids', get_summary_filename, subjectsdir),
                    segstats, 'summary_file')        
        awf.connect(reconall_hsfsT2, 'subject_id',    jsonify_stats, 'subject_id')
        awf.connect(segstats,        'summary_file',  jsonify_stats, 'segstats_file')
        
    if hsfsT1T2:
       reconall_hsfsT1T2 = pe.Node(interface=ReconAllHSFS(), name='reconall_hsfsT1T2')

       reconall_hsfsT1T2.inputs.subjects_dir = subjectsdir
       reconall_hsfsT1T2.inputs.terminal_output='none'
       reconall_hsfsT1T2.inputs.args = reconargs.replace('-qcache','')
       reconall_hsfsT1T2.inputs.hippocampal_subfields_T1 = True
       
       awf.connect(reconall, 'subject_id', reconall_hsfsT1T2, 'subject_id')
       awf.connect(reconall, 'aseg',       qcsnapshots, 'path_aseg')      
       awf.connect(reconall, 'orig',       qcsnapshots, 'path_orig')
       awf.connect(reconall, 'subject_id', qcsnapshots, 'subject_id')

       awf.connect(inputnode, ('subject_ids', get_T2_path_tup, scans_dir,'T1T2'),
                   reconall_hsfsT1T2, 'hippocampal_subfields_T2')
       
       awf.connect(reconall_hsfsT1T2, 'aseg', segstats, 'segmentation_file')
       awf.connect(reconall_hsfsT1T2, 'norm', segstats, 'partial_volume_file')
       awf.connect(inputnode, ('subject_ids', get_summary_filename, subjectsdir),
                    segstats, 'summary_file')       
       awf.connect(reconall_hsfsT1T2, 'subject_id',    jsonify_stats, 'subject_id')
       awf.connect(segstats,          'summary_file',  jsonify_stats, 'segstats_file')
    
    #wf order change if hsfs done/not done
    if not hsfsT1 and not hsfsT2 and not hsfsT1T2:
        awf.connect(reconall, 'aseg', segstats, 'segmentation_file')
        awf.connect(reconall, 'norm', segstats, 'partial_volume_file')
        awf.connect(reconall, 'aseg',       qcsnapshots, 'path_aseg')      
        awf.connect(reconall, 'orig',       qcsnapshots, 'path_orig')
        awf.connect(reconall, 'subject_id', qcsnapshots, 'subject_id')

        awf.connect(inputnode, ('subject_ids', get_summary_filename, subjectsdir),
                    segstats, 'summary_file')            
        awf.connect(reconall, 'subject_id',    jsonify_stats, 'subject_id')
        awf.connect(segstats, 'summary_file',  jsonify_stats, 'segstats_file')
        
    
    return awf
    
