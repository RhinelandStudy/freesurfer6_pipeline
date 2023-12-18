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
Created on Mon Jul 17 12:56:06 2017

@author: shahidm
"""

from .parse_stats import Subject
from .parse_hsfs_stats import HSFSSubject

from nipype.interfaces.base import BaseInterface, \
    BaseInterfaceInputSpec, traits, Directory, File, TraitedSpec
from nipype.utils.filemanip import copyfile
import os
import json


class JsonifyStatsInputSpec(BaseInterfaceInputSpec):
    subjects_dir = Directory(exists=True, desc='Subjects Directory', mandatory=True)
    subject_id = traits.String(desc='Subject ID', mandatory=True)
    parse_hsfs = traits.Bool(desc='if true, parse ?h.hippoSFVolumes-ID.txt file(s)', default=False)
    segstats_file = traits.File(exists=True,desc='SegStats file')

class JsonifyStatsOutputSpec(TraitedSpec):
    json_file = File(exists=True, desc="output json file")


class JsonifyStats(BaseInterface):
    input_spec = JsonifyStatsInputSpec
    output_spec = JsonifyStatsOutputSpec

    def _run_interface(self, runtime):

        statsdir = os.path.join(self.inputs.subjects_dir, self.inputs.subject_id, 'stats')
        #new_segstats_filename = os.path.join(statsdir, os.path.basename(self.inputs.segstats_file))
        #copy segstats_file to stats dir
        #copyfile(self.inputs.segstats_file, new_segstats_filename, copy=True, hashmethod='content')

        fname = os.path.join(statsdir, self.inputs.subject_id + '_stats.json')
        subject = Subject(self.inputs.subjects_dir, self.inputs.subject_id)
        outdict = subject.get_measures_dict()
        if self.inputs.parse_hsfs==True:
            hsfs_subject = HSFSSubject(self.inputs.subjects_dir, self.inputs.subject_id)
            hsfs_dict = hsfs_subject.get_measures_dict()
            outdict.update(hsfs_dict)
        with open(fname, 'w') as fp:
            json.dump(outdict, fp)
        
        return runtime

    def _list_outputs(self):
        
        outputs = self._outputs().get()
        fname = os.path.join(self.inputs.subjects_dir, self.inputs.subject_id, 'stats', self.inputs.subject_id + '_stats.json')
        outputs["json_file"] = os.path.abspath(fname)
        
        return outputs

