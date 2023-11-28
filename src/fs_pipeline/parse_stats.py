# -*- coding: utf-8 -*-

"""
Created on Mon Jul 17 12:56:06 2017

name='Recon-all Stats',
author='Scott Burns',
author_email='scott.s.burns@gmail.com',
description='recon-stats is a simple package to parse stats'
           ' files from Freesurfer\recon-all',
license='BSD (3-clause)',
url='http://github.com/sburns/recon-stats'

"""


import os
from os.path import isdir, join, basename



class Subject(object):
    def __init__(self, subjects_dir, name):

        self.name = name
        self.stat_dir = join(subjects_dir, name, 'stats')

        if not isdir(self.stat_dir):
            raise ValueError("Not a subject directory or this subject doesn't have a 'stats' dir")

    def get_measures(self):
        measures = []
        for root, d, fnames in os.walk(self.stat_dir):
            for fname in fnames:
                fullname = join(root, fname)
                #print "parsing ",fullname
                if Parser.can_parse(fullname):
                    p = Parser(fullname)
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
        

class Measure(object):
    """Basic class for storing statistical measures"""
    def __init__(self, sfn, structure, measure, value, units, descrip=None,
            short_name=None):
        self.sfn = sfn.replace('rh.','').replace('lh.','')
        self.structure = structure.lower()
        self.measure = measure.lower()
        self.value = float(value)
        self.units = units.lower()
        self.descrip = descrip
        self.short_name = short_name

    def __repr__(self):
        return "<Measure(%s(%s)[%s]:%0.4f)>" % \
            (self.structure, self.measure, self.units, self.value)

    def name(self):
        if self.measure:
            return '%s_%s_%s' % (self.sfn, self.structure,self.measure)
        else:
            return '%s_%s' % (self.sfn, self.structure)

    def label(self):
        return '%s %s(%s)' % (self.sfn, self.structure, self.descrip, self.units)

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

class Parser(object):

    parseable = ('aseg.stats',
                 'wmparc.stats',
                 'lh.aparc.stats',
                 'rh.aparc.stats',
                 'lh.aparc.pial.stats',
                 'rh.aparc.pial.stats',
                 'lh.aparc.a2009s.stats',
                 'rh.aparc.a2009s.stats',
                 'lh.aparc.DKTatlas.stats',
                 'rh.aparc.DKTatlas.stats',
                 'lh.BA_exvivo.thresh.stats',
                 'rh.BA_exvivo.thresh.stats',
                 'lh.w-g.pct.stats',
                 'rh.w-g.pct.stats',
                 'wmgm.aseg.stats'
                 )
    parseableforheader = ('aseg',
                 'wmparc',
                 'lh.aparc',
                 'rh.aparc',
                 'lh.aparc.pial',
                 'rh.aparc.pial',
                 'lh.aparc.a2009s',
                 'rh.aparc.a2009s',
                 'lh.aparc.DKTatlas',
                 'rh.aparc.DKTatlas',
                 'lh.BA_exvivo.thresh',
                 'rh.BA_exvivo.thresh',
                 'lh.w-g.pct',
                 'rh.w-g.pct',
                 'wmgm.aseg'
                 )
 
    topVars = {'aseg':['BrainSegVol',
                       'BrainSegVolNotVentSurf',
                       'eTIV',
                       'BrainSegVol-to-eTIV',
                       'MaskVol-to-eTIV',
                       'SubCortGrayVol',
                       'SupraTentorialVolNotVent',
                       'SupraTentorialVol',
                       'CortexVol',
                       'TotalGrayVol',
                       'lhCerebralWhiteMatterVol',
                       'rhCerebralWhiteMatterVol',
                       'CerebralWhiteMatterVol'],
               'lh.aparc.DKTatlas':['WhiteSurfArea',
                                    'MeanThickness'],
               'rh.aparc.DKTatlas':['WhiteSurfArea',
                                    'MeanThickness'],
               'wmparc':['lhCerebralWhiteMatterVol',
                         'rhCerebralWhiteMatterVol',
                         'CerebralWhiteMatterVol']
               }
               
    

    @classmethod
    def can_parse(cls, fname):
        return basename(fname) in cls.parseable

    def __init__(self, fname):
        self.type = basename(fname)
        self.statsfilename = os.path.splitext(self.type)[0]
        
        with open(fname) as f:
            self.raw = map(lambda x: x.strip(), f.read().splitlines())
        self.parser_fxn = self.get_parser()
        self.measures = self.parse()

    def __repr__(self):
        return "<Parser(%s)>" % self.type

    def get_parser(self):
        def _common(raw):
            """Johanna: 
                take the top common part only from:
                    aseg.stats,
                    ?h.aparc.DKTatlas.stats
                    and wmparc.stats files
            UPDATE: 11.10.2017. From Johanna. We should include the top part from each stats file and not discard any measure.
            """
            hemi=_hemi(raw)
            #some stats files do not have lh or rh hemi tag
            if not hemi == 'lh' or not hemi == 'rh':
                if 'lh' in self.statsfilename:
                    hemi='lh_'
                elif 'rh' in self.statsfilename:
                    hemi='rh_'
                else:
                    hemi=''
            else:
                hemi=hemi+'_'

            if any(s in self.statsfilename for s in self.parseableforheader):
                measure_lines = filter(lambda x: x.startswith('# Measure'), raw)
                measures = []
                for ml in measure_lines:
                    splat = ml.replace('# Measure', '').split(',')
                    pieces = map(lambda x: x.strip(), splat)
                    #some stats files from new fs6.0 lack a comma in common headers
                    if len(pieces)==4:
                        meas, descrip, val, units = pieces
                        meas = descrip.split()[0]
                        descrip = descrip.split()[1:]
                    else:
                        str, meas, descrip, val, units = pieces
                    #UPDATE: 11.10.2017. From Johanna. We should include the top part from each stats file and not discard any measure.
                    #therefore, the exclude line below is commented.
                    #if meas in self.topVars[self.statsfilename]:
                    m = Measure(self.statsfilename, hemi+ meas.replace('-','_'), '', val, units, descrip=descrip)
                    measures.append(m)
                return measures

        def _get_columns(raw):
            tablecol = filter(lambda x: x.startswith('# TableCol'), raw)
            ncols = int(filter(lambda x: x.startswith('# NTableCols'), raw)[0].split('# NTableCols')[1])
            columns = []
            for i in range(1, ncols + 1):
                i_table_rows = filter(lambda x: ' %d ' % i in x, tablecol)
                tup = (
                        i - 1,
                        filter(lambda x: 'ColHeader' in x, i_table_rows)[0].split(' ColHeader ')[-1].strip(),
                        filter(lambda x: 'FieldName' in x, i_table_rows)[0].split(' FieldName ')[-1].strip(),
                        filter(lambda x: 'Units' in x, i_table_rows)[0].split(' Units ')[-1].strip(),
                    )
                columns.append(tup)
            return columns

        def _grab(columns, col_name, ss_row):
            i, name, field, units = filter(lambda x: x[1] == col_name, columns)[0]
            return ss_row[i], field, units

        def _aseg(raw):
            common = _common(raw)
            columns = _get_columns(raw)
            rows = filter(lambda x: not x.startswith('#'), raw)
            measures = []
            
            for row in rows:
                ss_row = row.strip().split()
                #jk->ms select few measures
                #measure_cols = ['Volume_mm3', 'normMean', 'normStdDev', 'normMin', 'normMax', 'normRange']
                measure_cols = ['NVoxels', 'Volume_mm3']
                measures.extend(_parse_row(ss_row, columns, measure_cols))
            
            return common + measures

        def _wmparc(raw):
            common = _common(raw)
            columns = _get_columns(raw)
            rows = filter(lambda x: not x.startswith('#'), raw)
            measures = []
            
            for row in rows:
                ss_row = row.strip().split()
                #jk->ms select few measures
                #measure_cols = ['Volume_mm3', 'normMean', 'normStdDev', 'normMin', 'normMax', 'normRange']
                measure_cols = ['NVoxels', 'Volume_mm3']
                measures.extend(_parse_row(ss_row, columns, measure_cols))
            
            return common + measures
            
        def _parse_row(ss_row, columns, columns_to_measure, hemi=None):
            struct, _, _ = _grab(columns, 'StructName', ss_row)
            struct = struct.replace('-', '_')
            measures = []
            for col in columns_to_measure:
                value, descrip, units = _grab(columns, col, ss_row)
                m = Measure(self.statsfilename, struct, col, value, units, descrip=descrip)
                if hemi:
                    m.structure = '%s_%s' % (hemi, m.structure)
                    # m.descrip = '%s %s' % (hemi, m.descrip)
                measures.append(m)
            return measures

        def _hemi(raw):

            hemi=''
            hemi_strlist = filter(lambda x: x.startswith('# hemi'), raw)

            if hemi_strlist and len(hemi_strlist)>=1:
                hemi = filter(lambda x: x.startswith('# hemi'), raw)[0].split('hemi')[1].strip()
            else:
                hemi_strlist = filter(lambda x: x.startswith('# InVolFile '), raw)
                if hemi_strlist and len(hemi_strlist) >=1:
                    hemi = filter(lambda x: x.startswith('# InVolFile '), raw)[0].split('/')[-1].split('.')[0].strip()
            
            return hemi

        def _aparc(raw):
            # need common part here too
            common = _common(raw)
            # update these measures with hemisphere
            hemi = _hemi(raw)
            
            #for meas in common:
            #    meas.structure = hemi + meas.structure
            
            rows = filter(lambda x: not x.startswith('#'), raw)
            columns = _get_columns(raw)
            measures = []
            
            for row in rows:
                ss_row = row.strip().split()
                #wh->ms select few cols
                measure_cols = ['NumVert', 'SurfArea', 'GrayVol', 'ThickAvg',
                    'ThickStd', 'MeanCurv', 'GausCurv', 'FoldInd', 'CurvInd']
                measures.extend(_parse_row(ss_row, columns, measure_cols, hemi=hemi))
            

            return common + measures

        def _a2009s(raw):
            # need common part here too
            common = _common(raw)
            hemi = _hemi(raw)
            rows = filter(lambda x: not x.startswith('#'), raw)
            columns = _get_columns(raw)
            measures = []
            
            for row in rows:
                ss_row = row.strip().split()
                measure_cols = ['NumVert', 'SurfArea', 'GrayVol', 'ThickAvg',
                    'ThickStd', 'MeanCurv', 'GausCurv', 'FoldInd', 'CurvInd']
                measures.extend(_parse_row(ss_row, columns, measure_cols, hemi=hemi))
            
            return common + measures

        def _wgpct(raw):
            # need common part here too
            common = _common(raw)
            hemi = _hemi(raw)
            rows = filter(lambda x: not x.startswith('#'), raw)
            columns = _get_columns(raw)
            measures = []
            
            for row in rows:
                ss_row = row.strip().split()
                measure_cols = ['NVertices', 'Area_mm2',  'Mean', 'StdDev', 'Min', 'Max', 'Range', 'SNR']
                measures.extend(_parse_row(ss_row, columns, measure_cols, hemi=hemi))
            
            return common + measures

        def _wmgm(raw):
            # Don't need to do common
            #common = _common(raw)
            hemi = ""
            rows = filter(lambda x: not x.startswith('#'), raw)
            columns = _get_columns(raw)
            measures = []
            
            for row in rows:
                ss_row = row.strip().split()
                measure_cols = ['NVoxels', 'Volume_mm3']
                measures.extend(_parse_row(ss_row, columns, measure_cols, hemi=hemi))
            
            return measures
            
        key_parsers = {
            'aseg.stats': _aseg,
            'wmparc.stats': _wmparc,
            'lh.aparc.stats': _aparc,
            'rh.aparc.stats': _aparc,
            'lh.aparc.pial.stats':_aparc,
            'rh.aparc.pial.stats': _aparc,
            'lh.aparc.a2009s.stats': _aparc,
            'rh.aparc.a2009s.stats': _aparc,
            'lh.aparc.DKTatlas.stats':_aparc,
            'rh.aparc.DKTatlas.stats':_aparc,
            'lh.BA_exvivo.thresh.stats':_aparc,
            'rh.BA_exvivo.thresh.stats':_aparc,
            'lh.w-g.pct.stats':_wgpct,
            'rh.w-g.pct.stats':_wgpct,
            'wmgm.aseg.stats':_wmgm,
        }
        return key_parsers[self.type]

    def parse(self):
        return self.parser_fxn(self.raw)
