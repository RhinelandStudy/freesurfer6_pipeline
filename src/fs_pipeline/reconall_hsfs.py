# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""Provides interfaces to various commands provided by FreeSurfer

   BORROWED & MODIFIED FROM THE ACTUAL SOURCE TO RUN ONLY FOR HIPPOCAMPAL SUBFIELDS

   Change directory to provide relative paths for doctests
   >>> import os
   >>> filepath = os.path.dirname( os.path.realpath( __file__ ) )
   >>> datadir = os.path.realpath(os.path.join(filepath, '../../testing/data'))
   >>> os.chdir(datadir)

"""
from __future__ import print_function, division, unicode_literals, absolute_import

import os


from nipype import logging, LooseVersion
from nipype.interfaces.io import FreeSurferSource
from  nipype.interfaces.base import (File, traits,
                    Directory, InputMultiPath,
                    CommandLine,
                    CommandLineInputSpec, isdefined)
from nipype.utils.filemanip import check_depends

from nipype.interfaces.freesurfer.base import Info

__docformat__ = 'restructuredtext'
iflogger = logging.getLogger('interface')

# Keeping this to avoid breaking external programs that depend on it, but
# this should not be used internally
FSVersion = Info.looseversion().vstring


class ReconAllHSFSInputSpec(CommandLineInputSpec):
    subject_id = traits.Str("recon_all", argstr='-subjid %s',
                            desc='subject name', usedefault=True)
    directive = traits.Enum('all', 'autorecon1',
                            # autorecon2 variants
                            'autorecon2', 'autorecon2-volonly',
                            'autorecon2-perhemi', 'autorecon2-inflate1',
                            'autorecon2-cp', 'autorecon2-wm',
                            # autorecon3 variants
                            'autorecon3', 'autorecon3-T2pial',
                            # Mix of autorecon2 and autorecon3 steps
                            'autorecon-pial', 'autorecon-hemi',
                            # Not "multi-stage flags"
                            'localGI', 'qcache',
                            argstr='-%s', desc='process directive',
                            position=0)
    hemi = traits.Enum('lh', 'rh', desc='hemisphere to process',
                       argstr="-hemi %s")
    T1_files = InputMultiPath(File(exists=True), argstr='-i %s...',
                              desc='name of T1 file to process')
    T2_file = File(exists=True, argstr="-T2 %s", min_ver='5.3.0',
                   desc='Convert T2 image to orig directory')
    use_T2 = traits.Bool(argstr="-T2pial", min_ver='5.3.0',
                         desc='Use converted T2 to refine the cortical surface')
    openmp = traits.Int(argstr="-openmp %d",
                        desc="Number of processors to use in parallel")
    parallel = traits.Bool(argstr="-parallel",
                           desc="Enable parallel execution")
    hires = traits.Bool(argstr="-hires", min_ver='6.0.0',
                        desc="Conform to minimum voxel size (for voxels < 1mm)")
    mprage = traits.Bool(argstr='-mprage',
                         desc=('Assume scan parameters are MGH MP-RAGE '
                               'protocol, which produces darker gray matter'))
    big_ventricles = traits.Bool(argstr='-bigventricles',
                                 desc=('For use in subjects with enlarged '
                                       'ventricles'))
    brainstem = traits.Bool(argstr='-brainstem-structures',
                            desc='Segment brainstem structures')
    hippocampal_subfields_T1 = traits.Bool(
        argstr='-hippocampal-subfields-T1', min_ver='6.0.0',
        desc='segment hippocampal subfields using input T1 scan')
    hippocampal_subfields_T2 = traits.Tuple(
        File(exists=True), traits.Str(),
        argstr='-hippocampal-subfields-T2 %s %s', min_ver='6.0.0',
        desc=('segment hippocampal subfields using T2 scan, identified by '
              'ID (may be combined with hippocampal_subfields_T1)'))
    expert = File(exists=True, argstr='-expert %s',
                  desc="Set parameters using expert file")
    xopts = traits.Enum("use", "clean", "overwrite", argstr='-xopts-%s',
                        desc="Use, delete or overwrite existing expert options file")
    subjects_dir = Directory(exists=True, argstr='-sd %s', hash_files=False,
                             desc='path to subjects directory', genfile=True)
    flags = InputMultiPath(traits.Str, argstr='%s', desc='additional parameters')

    # Expert options
    talairach = traits.Str(desc="Flags to pass to talairach commands", xor=['expert'])
    mri_normalize = traits.Str(desc="Flags to pass to mri_normalize commands", xor=['expert'])
    mri_watershed = traits.Str(desc="Flags to pass to mri_watershed commands", xor=['expert'])
    mri_em_register = traits.Str(desc="Flags to pass to mri_em_register commands", xor=['expert'])
    mri_ca_normalize = traits.Str(desc="Flags to pass to mri_ca_normalize commands", xor=['expert'])
    mri_ca_register = traits.Str(desc="Flags to pass to mri_ca_register commands", xor=['expert'])
    mri_remove_neck = traits.Str(desc="Flags to pass to mri_remove_neck commands", xor=['expert'])
    mri_ca_label = traits.Str(desc="Flags to pass to mri_ca_label commands", xor=['expert'])
    mri_segstats = traits.Str(desc="Flags to pass to mri_segstats commands", xor=['expert'])
    mri_mask = traits.Str(desc="Flags to pass to mri_mask commands", xor=['expert'])
    mri_segment = traits.Str(desc="Flags to pass to mri_segment commands", xor=['expert'])
    mri_edit_wm_with_aseg = traits.Str(desc="Flags to pass to mri_edit_wm_with_aseg commands", xor=['expert'])
    mri_pretess = traits.Str(desc="Flags to pass to mri_pretess commands", xor=['expert'])
    mri_fill = traits.Str(desc="Flags to pass to mri_fill commands", xor=['expert'])
    mri_tessellate = traits.Str(desc="Flags to pass to mri_tessellate commands", xor=['expert'])
    mris_smooth = traits.Str(desc="Flags to pass to mri_smooth commands", xor=['expert'])
    mris_inflate = traits.Str(desc="Flags to pass to mri_inflate commands", xor=['expert'])
    mris_sphere = traits.Str(desc="Flags to pass to mris_sphere commands", xor=['expert'])
    mris_fix_topology = traits.Str(desc="Flags to pass to mris_fix_topology commands", xor=['expert'])
    mris_make_surfaces = traits.Str(desc="Flags to pass to mris_make_surfaces commands", xor=['expert'])
    mris_surf2vol = traits.Str(desc="Flags to pass to mris_surf2vol commands", xor=['expert'])
    mris_register = traits.Str(desc="Flags to pass to mris_register commands", xor=['expert'])
    mrisp_paint = traits.Str(desc="Flags to pass to mrisp_paint commands", xor=['expert'])
    mris_ca_label = traits.Str(desc="Flags to pass to mris_ca_label commands", xor=['expert'])
    mris_anatomical_stats = traits.Str(desc="Flags to pass to mris_anatomical_stats commands", xor=['expert'])
    mri_aparc2aseg = traits.Str(desc="Flags to pass to mri_aparc2aseg commands", xor=['expert'])


class ReconAllHSFSOutputSpec(FreeSurferSource.output_spec):
    subjects_dir = Directory(exists=True, desc='Freesurfer subjects directory.')
    subject_id = traits.Str(desc='Subject name for whom to retrieve data')


class ReconAllHSFS(CommandLine):
    """Uses recon-all to generate surfaces and parcellations of structural data
    from anatomical images of a subject.

    Examples
    --------

    >>> from nipype.interfaces.freesurfer import ReconAll
    >>> reconall = ReconAll()
    >>> reconall.inputs.subject_id = 'foo'
    >>> reconall.inputs.directive = 'all' ###ms
    >>> reconall.inputs.subjects_dir = '.'
    >>> reconall.inputs.T1_files = 'structural.nii'
    >>> reconall.cmdline # doctest: +ALLOW_UNICODE
    'recon-all -all -i structural.nii -subjid foo -sd .'
    >>> reconall.inputs.flags = "-qcache"
    >>> reconall.cmdline # doctest: +ALLOW_UNICODE
    'recon-all -all -i structural.nii -qcache -subjid foo -sd .'
    >>> reconall.inputs.flags = ["-cw256", "-qcache"]
    >>> reconall.cmdline # doctest: +ALLOW_UNICODE
    'recon-all -all -i structural.nii -cw256 -qcache -subjid foo -sd .'

    Hemisphere may be specified regardless of directive:

    >>> reconall.inputs.flags = []
    >>> reconall.inputs.hemi = 'lh'
    >>> reconall.cmdline # doctest: +ALLOW_UNICODE
    'recon-all -all -i structural.nii -hemi lh -subjid foo -sd .'

    ``-autorecon-hemi`` uses the ``-hemi`` input to specify the hemisphere
    to operate upon:

    >>> reconall.inputs.directive = 'autorecon-hemi'
    >>> reconall.cmdline # doctest: +ALLOW_UNICODE
    'recon-all -autorecon-hemi lh -i structural.nii -subjid foo -sd .'

    Hippocampal subfields can accept T1 and T2 images:

    >>> reconall_subfields = ReconAll()
    >>> reconall_subfields.inputs.subject_id = 'foo'
    >>> reconall_subfields.inputs.directive = 'all'
    >>> reconall_subfields.inputs.subjects_dir = '.'
    >>> reconall_subfields.inputs.T1_files = 'structural.nii'
    >>> reconall_subfields.inputs.hippocampal_subfields_T1 = True
    >>> reconall_subfields.cmdline # doctest: +ALLOW_UNICODE
    'recon-all -all -i structural.nii -hippocampal-subfields-T1 -subjid foo -sd .'
    >>> reconall_subfields.inputs.hippocampal_subfields_T2 = (
    ... 'structural.nii', 'test')
    >>> reconall_subfields.cmdline # doctest: +ALLOW_UNICODE
    'recon-all -all -i structural.nii -hippocampal-subfields-T1T2 structural.nii test -subjid foo -sd .'
    >>> reconall_subfields.inputs.hippocampal_subfields_T1 = False
    >>> reconall_subfields.cmdline # doctest: +ALLOW_UNICODE
    'recon-all -all -i structural.nii -hippocampal-subfields-T2 structural.nii test -subjid foo -sd .'
    """

    _cmd = 'recon-all'
    _additional_metadata = ['loc', 'altkey']
    input_spec = ReconAllHSFSInputSpec
    output_spec = ReconAllHSFSOutputSpec
    _can_resume = True
    force_run = False

    # Steps are based off of the recon-all tables [0,1] describing, inputs,
    # commands, and outputs of each step of the recon-all process,
    # controlled by flags.
    #
    # Each step is a 3-tuple containing (flag, [outputs], [inputs])
    # A step is considered complete if all of its outputs exist and are newer
    # than the inputs. An empty input list indicates input mtimes will not
    # be checked. This may need updating, if users are working with manually
    # edited files.
    #
    # [0] https://surfer.nmr.mgh.harvard.edu/fswiki/ReconAllTableStableV5.3
    # [1] https://surfer.nmr.mgh.harvard.edu/fswiki/ReconAllTableStableV6.0
    _autorecon1_steps = [
        ('motioncor', ['mri/rawavg.mgz', 'mri/orig.mgz'], []),
        ('talairach', ['mri/orig_nu.mgz',
                       'mri/transforms/talairach.auto.xfm',
                       'mri/transforms/talairach.xfm',
                       # 'mri/transforms/talairach_avi.log',
                       ], []),
        ('nuintensitycor', ['mri/nu.mgz'], []),
        ('normalization', ['mri/T1.mgz'], []),
        ('skullstrip', ['mri/transforms/talairach_with_skull.lta',
                        'mri/brainmask.auto.mgz',
                        'mri/brainmask.mgz'], []),
        ]
    if Info.looseversion() < LooseVersion("6.0.0"):
        _autorecon2_volonly_steps = [
            ('gcareg', ['mri/transforms/talairach.lta'], []),
            ('canorm', ['mri/norm.mgz'], []),
            ('careg', ['mri/transforms/talairach.m3z'], []),
            ('careginv', ['mri/transforms/talairach.m3z.inv.x.mgz',
                          'mri/transforms/talairach.m3z.inv.y.mgz',
                          'mri/transforms/talairach.m3z.inv.z.mgz',
                          ], []),
            ('rmneck', ['mri/nu_noneck.mgz'], []),
            ('skull-lta', ['mri/transforms/talairach_with_skull_2.lta'], []),
            ('calabel', ['mri/aseg.auto_noCCseg.mgz',
                         'mri/aseg.auto.mgz',
                         'mri/aseg.mgz'], []),
            ('normalization2', ['mri/brain.mgz'], []),
            ('maskbfs', ['mri/brain.finalsurfs.mgz'], []),
            ('segmentation', ['mri/wm.seg.mgz',
                              'mri/wm.asegedit.mgz',
                              'mri/wm.mgz'], []),
            ('fill', ['mri/filled.mgz',
                      # 'scripts/ponscc.cut.log',
                      ], []),
            ]
        _autorecon2_lh_steps = [
            ('tessellate', ['surf/lh.orig.nofix'], []),
            ('smooth1', ['surf/lh.smoothwm.nofix'], []),
            ('inflate1', ['surf/lh.inflated.nofix'], []),
            ('qsphere', ['surf/lh.qsphere.nofix'], []),
            ('fix', ['surf/lh.orig'], []),
            ('white', ['surf/lh.white', 'surf/lh.curv', 'surf/lh.area',
                       'label/lh.cortex.label'], []),
            ('smooth2', ['surf/lh.smoothwm'], []),
            ('inflate2', ['surf/lh.inflated', 'surf/lh.sulc',
                          'surf/lh.inflated.H', 'surf/lh.inflated.K'], []),
            # Undocumented in ReconAllTableStableV5.3
            ('curvstats', ['stats/lh.curv.stats'], []),
            ]
        _autorecon3_lh_steps = [
            ('sphere', ['surf/lh.sphere'], []),
            ('surfreg', ['surf/lh.sphere.reg'], []),
            ('jacobian_white', ['surf/lh.jacobian_white'], []),
            ('avgcurv', ['surf/lh.avg_curv'], []),
            ('cortparc', ['label/lh.aparc.annot'], []),
            ('pial', ['surf/lh.pial', 'surf/lh.curv.pial', 'surf/lh.area.pial',
                      'surf/lh.thickness'], []),
            # Misnamed outputs in ReconAllTableStableV5.3: ?h.w-c.pct.mgz
            ('pctsurfcon', ['surf/lh.w-g.pct.mgh'], []),
            ('parcstats', ['stats/lh.aparc.stats'], []),
            ('cortparc2', ['label/lh.aparc.a2009s.annot'], []),
            ('parcstats2', ['stats/lh.aparc.a2009s.stats'], []),
            # Undocumented in ReconAllTableStableV5.3
            ('cortparc3', ['label/lh.aparc.DKTatlas40.annot'], []),
            # Undocumented in ReconAllTableStableV5.3
            ('parcstats3', ['stats/lh.aparc.a2009s.stats'], []),
            ('label-exvivo-ec', ['label/lh.entorhinal_exvivo.label'], []),
            ]
        _autorecon3_added_steps = [
            ('cortribbon', ['mri/lh.ribbon.mgz', 'mri/rh.ribbon.mgz',
                            'mri/ribbon.mgz'], []),
            ('segstats', ['stats/aseg.stats'], []),
            ('aparc2aseg', ['mri/aparc+aseg.mgz',
                            'mri/aparc.a2009s+aseg.mgz'], []),
            ('wmparc', ['mri/wmparc.mgz', 'stats/wmparc.stats'], []),
            ('balabels', ['label/BA.ctab', 'label/BA.thresh.ctab'], []),
            ]
    else:
        _autorecon2_volonly_steps = [
            ('gcareg', ['mri/transforms/talairach.lta'], []),
            ('canorm', ['mri/norm.mgz'], []),
            ('careg', ['mri/transforms/talairach.m3z'], []),
            ('calabel', ['mri/aseg.auto_noCCseg.mgz',
                         'mri/aseg.auto.mgz',
                         'mri/aseg.mgz'], []),
            ('normalization2', ['mri/brain.mgz'], []),
            ('maskbfs', ['mri/brain.finalsurfs.mgz'], []),
            ('segmentation', ['mri/wm.seg.mgz',
                              'mri/wm.asegedit.mgz',
                              'mri/wm.mgz'], []),
            ('fill', ['mri/filled.mgz',
                      # 'scripts/ponscc.cut.log',
                      ], []),
            ]
        _autorecon2_lh_steps = [
            ('tessellate', ['surf/lh.orig.nofix'], []),
            ('smooth1', ['surf/lh.smoothwm.nofix'], []),
            ('inflate1', ['surf/lh.inflated.nofix'], []),
            ('qsphere', ['surf/lh.qsphere.nofix'], []),
            ('fix', ['surf/lh.orig'], []),
            ('white', ['surf/lh.white.preaparc', 'surf/lh.curv',
                       'surf/lh.area', 'label/lh.cortex.label'], []),
            ('smooth2', ['surf/lh.smoothwm'], []),
            ('inflate2', ['surf/lh.inflated', 'surf/lh.sulc'], []),
            ('curvHK', ['surf/lh.white.H', 'surf/lh.white.K',
                        'surf/lh.inflated.H', 'surf/lh.inflated.K'], []),
            ('curvstats', ['stats/lh.curv.stats'], []),
            ]
        _autorecon3_lh_steps = [
            ('sphere', ['surf/lh.sphere'], []),
            ('surfreg', ['surf/lh.sphere.reg'], []),
            ('jacobian_white', ['surf/lh.jacobian_white'], []),
            ('avgcurv', ['surf/lh.avg_curv'], []),
            ('cortparc', ['label/lh.aparc.annot'], []),
            ('pial', ['surf/lh.pial', 'surf/lh.curv.pial',
                      'surf/lh.area.pial', 'surf/lh.thickness',
                      'surf/lh.white'], []),
            ('parcstats', ['stats/lh.aparc.stats'], []),
            ('cortparc2', ['label/lh.aparc.a2009s.annot'], []),
            ('parcstats2', ['stats/lh.aparc.a2009s.stats'], []),
            ('cortparc3', ['label/lh.aparc.DKTatlas.annot'], []),
            ('parcstats3', ['stats/lh.aparc.DKTatlas.stats'], []),
            ('pctsurfcon', ['surf/lh.w-g.pct.mgh'], []),
            ]
        _autorecon3_added_steps = [
            ('cortribbon', ['mri/lh.ribbon.mgz', 'mri/rh.ribbon.mgz',
                            'mri/ribbon.mgz'], []),
            ('hyporelabel', ['mri/aseg.presurf.hypos.mgz'], []),
            ('aparc2aseg', ['mri/aparc+aseg.mgz',
                            'mri/aparc.a2009s+aseg.mgz',
                            'mri/aparc.DKTatlas+aseg.mgz'], []),
            ('apas2aseg', ['mri/aseg.mgz'], ['mri/aparc+aseg.mgz']),
            ('segstats', ['stats/aseg.stats'], []),
            ('wmparc', ['mri/wmparc.mgz', 'stats/wmparc.stats'], []),
            # Note that this is a very incomplete list; however the ctab
            # files are last to be touched, so this should be reasonable
            ('balabels', ['label/BA_exvivo.ctab',
                          'label/BA_exvivo.thresh.ctab',
                          'label/lh.entorhinal_exvivo.label',
                          'label/rh.entorhinal_exvivo.label'], []),
            ]

    # Fill out autorecon2 steps
    _autorecon2_rh_steps = [
        (step, [out.replace('lh', 'rh') for out in outs], ins)
        for step, outs, ins in _autorecon2_lh_steps]
    _autorecon2_perhemi_steps = [
        (step, [of for out in outs
                for of in (out, out.replace('lh', 'rh'))], ins)
        for step, outs, ins in _autorecon2_lh_steps]
    _autorecon2_steps = _autorecon2_volonly_steps + _autorecon2_perhemi_steps

    # Fill out autorecon3 steps
    _autorecon3_rh_steps = [
        (step, [out.replace('lh', 'rh') for out in outs], ins)
        for step, outs, ins in _autorecon3_lh_steps]
    _autorecon3_perhemi_steps = [
        (step, [of for out in outs
                for of in (out, out.replace('lh', 'rh'))], ins)
        for step, outs, ins in _autorecon3_lh_steps]
    _autorecon3_steps = _autorecon3_perhemi_steps + _autorecon3_added_steps

    # Fill out autorecon-hemi lh/rh steps
    _autorecon_lh_steps = (_autorecon2_lh_steps + _autorecon3_lh_steps)
    _autorecon_rh_steps = (_autorecon2_rh_steps + _autorecon3_rh_steps)

    _steps = _autorecon1_steps + _autorecon2_steps + _autorecon3_steps

    _binaries = ['talairach', 'mri_normalize', 'mri_watershed',
                 'mri_em_register', 'mri_ca_normalize', 'mri_ca_register',
                 'mri_remove_neck', 'mri_ca_label', 'mri_segstats',
                 'mri_mask', 'mri_segment', 'mri_edit_wm_with_aseg',
                 'mri_pretess', 'mri_fill', 'mri_tessellate', 'mris_smooth',
                 'mris_inflate', 'mris_sphere', 'mris_fix_topology',
                 'mris_make_surfaces', 'mris_surf2vol', 'mris_register',
                 'mrisp_paint', 'mris_ca_label', 'mris_anatomical_stats',
                 'mri_aparc2aseg']

    def _gen_subjects_dir(self):
        return os.getcwd()

    def _gen_filename(self, name):
        if name == 'subjects_dir':
            return self._gen_subjects_dir()
        return None

    def _list_outputs(self):
        """
        See io.FreeSurferSource.outputs for the list of outputs returned
        """
        if isdefined(self.inputs.subjects_dir):
            subjects_dir = self.inputs.subjects_dir
        else:
            subjects_dir = self._gen_subjects_dir()

        if isdefined(self.inputs.hemi):
            hemi = self.inputs.hemi
        else:
            hemi = 'both'

        outputs = self._outputs().get()

        outputs.update(FreeSurferSource(subject_id=self.inputs.subject_id,
                                        subjects_dir=subjects_dir,
                                        hemi=hemi)._list_outputs())
        outputs['subject_id'] = self.inputs.subject_id
        outputs['subjects_dir'] = subjects_dir
        return outputs

    def _is_resuming(self):
        subjects_dir = self.inputs.subjects_dir
        if not isdefined(subjects_dir):
            subjects_dir = self._gen_subjects_dir()
        if os.path.isdir(os.path.join(subjects_dir, self.inputs.subject_id,
                                      'mri')):
            return True
        return False

    def _format_arg(self, name, trait_spec, value):
        if name == 'T1_files':
            if self._is_resuming():
                return None
        if name == 'hippocampal_subfields_T1' and \
                isdefined(self.inputs.hippocampal_subfields_T2):
            return None
        if all((name == 'hippocampal_subfields_T2',
                isdefined(self.inputs.hippocampal_subfields_T1) and
                self.inputs.hippocampal_subfields_T1)):
            argstr = trait_spec.argstr.replace('T2', 'T1T2')
            return argstr % value
        if name == 'directive' and value == 'autorecon-hemi':
            if not isdefined(self.inputs.hemi):
                raise ValueError("Directive 'autorecon-hemi' requires hemi "
                                 "input to be set")
            value += ' ' + self.inputs.hemi
        if all((name == 'hemi',
                isdefined(self.inputs.directive) and
                self.inputs.directive == 'autorecon-hemi')):
            return None
        return super(ReconAllHSFS, self)._format_arg(name, trait_spec, value)

    @property
    def cmdline(self):
        cmd = super(ReconAllHSFS, self).cmdline

        # Adds '-expert' flag if expert flags are passed
        # Mutually exclusive with 'expert' input parameter
        cmd += self._prep_expert_file()

        if not self._is_resuming():
            return cmd
        subjects_dir = self.inputs.subjects_dir
        if not isdefined(subjects_dir):
            subjects_dir = self._gen_subjects_dir()

        # Check only relevant steps
        directive = self.inputs.directive
        if not isdefined(directive):
            steps = []
#        elif directive == 'autorecon1':
#            steps = self._autorecon1_steps
#        elif directive == 'autorecon2-volonly':
#            steps = self._autorecon2_volonly_steps
#        elif directive == 'autorecon2-perhemi':
#            steps = self._autorecon2_perhemi_steps
#        elif directive.startswith('autorecon2'):
#            if isdefined(self.inputs.hemi):
#                if self.inputs.hemi == 'lh':
#                    steps = (self._autorecon2_volonly_steps +
#                             self._autorecon2_lh_steps)
#                else:
#                    steps = (self._autorecon2_volonly_steps +
#                             self._autorecon2_rh_steps)
#            else:
#                steps = self._autorecon2_steps
#        elif directive == 'autorecon-hemi':
#            if self.inputs.hemi == 'lh':
#                steps = self._autorecon_lh_steps
#            else:
#                steps = self._autorecon_rh_steps
#        elif directive == 'autorecon3':
#            steps = self._autorecon3_steps
        else:
            steps = self._steps

        """
        no_run = True
        flags = []
        for step, outfiles, infiles in steps:
            flag = '-{}'.format(step)
            noflag = '-no{}'.format(step)
            if noflag in cmd:
                continue
            elif flag in cmd:
                no_run = False
                continue

            subj_dir = os.path.join(subjects_dir, self.inputs.subject_id)
            if check_depends([os.path.join(subj_dir, f) for f in outfiles],
                             [os.path.join(subj_dir, f) for f in infiles]):
                flags.append(noflag)
            else:
                no_run = False

        if no_run and not self.force_run:
            iflogger.info('recon-all complete : Not running')
            return "echo recon-all: nothing to do"
        
        cmd += ' ' + ' '.join(flags)
        """
        iflogger.info('resume recon-all : %s' % cmd)
        return cmd

    def _prep_expert_file(self):
        if isdefined(self.inputs.expert):
            return ''

        lines = []
        for binary in self._binaries:
            args = getattr(self.inputs, binary)
            if isdefined(args):
                lines.append('{} {}\n'.format(binary, args))

        if lines == []:
            return ''

        contents = ''.join(lines)
        if not isdefined(self.inputs.xopts) and \
                self._get_expert_file() == contents:
            return ' -xopts-use'

        expert_fname = os.path.abspath('expert.opts')
        with open(expert_fname, 'w') as fobj:
            fobj.write(contents)
        return ' -expert {}'.format(expert_fname)

    def _get_expert_file(self):
        # Read pre-existing options file, if it exists
        if isdefined(self.inputs.subjects_dir):
            subjects_dir = self.inputs.subjects_dir
        else:
            subjects_dir = self._gen_subjects_dir()

        xopts_file = os.path.join(subjects_dir, self.inputs.subject_id,
                                  'scripts', 'expert-options')
        if not os.path.exists(xopts_file):
            return ''
        with open(xopts_file, 'r') as fobj:
            return fobj.read()

