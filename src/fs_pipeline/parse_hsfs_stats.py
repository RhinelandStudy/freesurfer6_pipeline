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


import os
from os.path import isdir, join, basename



class HSFSSubject(object):
    def __init__(self, subjects_dir, name):

        self.name = name
        self.mri_dir = join(subjects_dir, name, 'mri')

        if not isdir(self.mri_dir):
            raise ValueError("Not a subject directory or this subject doesn't have an 'mri' dir")

    def get_measures(self):
        measures = []
        id=''
        hemi=''
        for root, d, fnames in os.walk(self.mri_dir):
            for fname in fnames:
                fullname = join(root, fname)
                if 'hippoSfVolumes' in fname:
                    if 'rh.' in fname:
                        id='_'.join(fname.split('.')[1].split('-')[1:])
                        hemi='rh'
                    if 'lh.' in fname:
                        id='_'.join(fname.split('.')[1].split('-')[1:])
                        hemi='lh'
                    p = HSFSParser(fullname, hemi,id)
                    measures.extend(p.measures)
        self.measures = measures

    def get_measures_dict(self):
        if not hasattr(self, 'measures'):
            self.get_measures()
        data = {}
        for m in self.measures:
            mclass = m.name().split('_')[0]
            mname = '_'.join(m.name().split('_')[1:])
            if mclass in data:
                data[mclass].update({mname:m.value_as_float()})
            else:
                data[mclass] = {mname:m.value_as_float()}
            #data[m.name()] = m.value_as_str()
        return data
        

class HSFSMeasure(object):
    """Basic class for storing statistical measures"""
    def __init__(self, measure, value, hemi,id):
        self.measure = measure.lower()
        self.value = float(value)
        self.hemi = hemi
        self.id = 'hippoSF_'+id


    def __repr__(self):
        return "<Measure(%s(%s)[%s]:%0.4f)>" % \
            (self.hemi, self.measure, self.value)

    def name(self):
        return '%s_%s_%s' % (self.id.replace('-', '_'), self.hemi, self.measure)


    def value_as_str(self):
        return str(self.value)

    def value_as_float(self):
        float_val=None
        try:
           if 'NaN'.lower() in str(self.value).lower():
              float_val = 0.0
           else:
              float_val = float(self.value)
        except ValueError:
           float_val = 0.0
        return float_val

class HSFSParser(object):

    def __init__(self, fname,hemi,id):
        self.type = basename(fname)
        self.hemi=hemi
        self.id = id
        with open(fname) as f:
            self.raw = map(lambda x: x.strip(), f.read().splitlines())
        
        self.measures = self.parse(self.raw)
        

    def __repr__(self):
        return "<Parser(%s)>" % self.type

        
    def parse(self,raw):
        measure_lines = raw #filter(lambda x: x.startswith('# Measure'), raw)
        measures = []
        for ml in measure_lines:
            splat = ml.split()
            pieces = map(lambda x: x.strip(), splat)
            meas, val = pieces
            meas = meas.replace('-', '_')
            m = HSFSMeasure(meas, val,self.hemi,self.id)
            measures.append(m)
        
        return measures
