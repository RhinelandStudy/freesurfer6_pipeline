#!/usr/bin/env python3
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
Created on Mon Dec  2 11:04:49 2019

@author: moazemim
"""
import os

def map_aseg2label(aseg):
    import numpy
    from .fs_colorlut import get_lut 
    import numpy as np
    import matplotlib.colors
    '''
    Function to perform look-up table mapping of aseg.mgz data to label space (continue labels)
    '''
    labels=np.unique(aseg)
    # retrieve freesurfer color map lookup table
    cdict = get_lut()
    colors = np.zeros((len(labels), 3))
    mapped_aseg = np.zeros_like(aseg)

    for idx, value in enumerate(labels):
        mapped_aseg[aseg==value]=idx
        r, g, b = cdict[str(value)]
        colors[idx]=[r, g, b]

    colors = np.divide(colors ,255)
    cmap = matplotlib.colors.ListedColormap(colors)

    return mapped_aseg,cmap



# calculates the bounding boxes of the 3 axes
def bbox_3D(img,padd):
    import numpy as np

    min_shape=np.min(img.shape)

    idx=np.where(img>0)
    idx_min=max(np.min(idx),padd)
    idx_max=min(np.max(idx),min_shape-padd)

    return idx_min,idx_max

# creates the screenshotsof both original and overlay images. Supports both axial and sagittal views
def save_slices_dual(slices_orig, slices_overlay, out_dir, suffix='',image_extension='png'):
    import numpy as np
    import matplotlib.image as mpimg
    img_orig = mpimg.imread(slices_orig)
    img_over = mpimg.imread(slices_overlay)
    out_file = os.path.join(out_dir, 'img_%s.'% suffix +image_extension)
    mpimg.imsave(out_file, np.concatenate((img_orig, img_over)),dpi=30)
    #print ("Output %s is generated"%out_file)
    return out_file
        

# this finction saves screenshots of the overlayed aseg+orig volumes in a sequence. Supports both axial and sagittal views
def save_slices_overlay(orig_grid_path, aseg_grid_path, out_dir, suffix=''):
    import matplotlib.image as mpimg    
    img_orig = mpimg.imread(orig_grid_path)
    img_aseg = mpimg.imread(aseg_grid_path)
    out_file = os.path.join(out_dir, 'img_%s.png' % suffix)
    mpimg.imsave(out_file, 0.3*img_orig+ 0.7 * img_aseg,dpi=30)
    #print ("Output %s is generated"%out_file)
    return out_file
    
    
# this finction saves screenshots of the aseg or orig volumes in a grid layout (this sequence layout is a simpler version). Supports both axial and sagittal views
def save_slices_grid(slices, cmap, out_dir, suffix='', rot_angle=0,order=3):
    import numpy as np
    import matplotlib.image as mpimg
    from scipy import ndimage

    out_file = os.path.join(out_dir,'img_%s.png' % suffix)
    nrows = 1  # can be adjusted to support grid layout
    ncols = int(float(len(slices)))  # can be adjusted to support grid layout
    img = np.zeros((nrows,ncols),dtype=object)
    grid = []
    for i in range(nrows):
        for j in range(ncols):
                img[i,j] = ndimage.rotate(slices[i*ncols+j], rot_angle,order=order)
        row = np.concatenate((img[i]), axis=1)
        grid.append(row)
    grid = np.concatenate((grid), axis=0)
    if "aseg" in suffix:
        mpimg.imsave(out_file, grid, cmap=cmap, vmin=0 ,vmax=int(np.max(grid)),dpi=30)
    else:
        mpimg.imsave(out_file, grid, cmap=cmap,dpi=30)
    #print ("Output %s is generated"%out_file)
    return out_file

#################################################################
########     The highest level function to be called      #######
######## arguments:
######## 1. path to orig file                             #######
######## 2. path to aseg file                             #######
######## 3. output path, in which the screenshots will be put  ##
######## 4. number of steps between sclices in each axis  ####### 
#################################################################    
def create_mri_screenshots(path_orig, path_aseg, out_dir,subject_id,
                           num_slices=60,padd=4,spacing=3,image_extension='png'):
    '''
    Function to create axial and sagittal screenshoots from the freesurfer mri outputs.
    The screenshot is generated from a crop volume containing only aseg labels

    :arg
        path_orig : path to the orig.mgz volume from the freesurfer output
        path_aseg : path to the aseg.mgz volume from the freesurfer output
        out_dir   : directory path for storing the generated screenshoots
        num_slices(int) : The number of slices to be plot for each cross-sectional plane (default : 60)
        padd (int) : number of extra slices to add in each direction of a crop aseg volume. (default : 4)
        spacing(int) : include spacing between  plot images (default : 3)
        image_extension ('jpep','png') : type of image to be created (default : png)

    :return
        None
    '''

    import os
    import nibabel as nib
    import numpy as np    
    from fs_pipeline.screenshot import (map_aseg2label,bbox_3D,save_slices_dual,save_slices_overlay,save_slices_grid)

    out_dir=os.path.join(out_dir,subject_id, 'qcsnapshots')

    if not os.path.exists(out_dir):
        os.makedirs(out_dir) 

    #load original image from file
    orig = nib.load(path_orig)
    orig_data = orig.get_data()
    
    #load aseg image from file
    aseg = nib.load(path_aseg)
    aseg_data = aseg.get_data()

    #map aseg labels to a continue label space and extract cmap colors
    aseg_map,cmap=map_aseg2label(aseg_data)
    
    # calculate bounding boxes of the volume
    idx_min,idx_max=bbox_3D(aseg_data,padd)


    #Add Padd slices to the bouding box
    padd=int(padd)
    spacing = int(spacing)
    idx_min -= padd
    idx_max += padd

    #Calculate new volume size and asign values
    size=idx_max-idx_min


    idx_max = idx_min+size

    spacing_size=size+2*spacing

    new_orig=np.zeros(shape=(size,size,size))
    new_aseg=np.zeros(shape=(size,size,size))

    new_orig[:,:,:]=orig_data[int(idx_min):int(idx_max),int(idx_min):int(idx_max),int(idx_min):int(idx_max)]
    new_aseg[:,:,:]=aseg_map[int(idx_min):int(idx_max),int(idx_min):int(idx_max),int(idx_min):int(idx_max)]

    

    #Plot sagittal images
    # stack sagittal slices
    slices_orig = []
    slices_aseg = []
    #Extract Starting and finish point for the sagittal plane
    sagittal_labels_idx=np.where(new_aseg>0)
    sagittal_start=max(np.min(sagittal_labels_idx[0])-padd//2,0)
    sagittal_finish=min(np.max(sagittal_labels_idx[0])+padd//2,new_aseg.shape[0])

    sagittal_idx=np.round(np.linspace(sagittal_start,sagittal_finish,num_slices))

    for i in sagittal_idx[:-1]:
        slice=int(i)
        aseg_slice=np.zeros((spacing_size,spacing_size))
        orig_slice=np.zeros((spacing_size,spacing_size))

        aseg_slice[spacing:-spacing,spacing:-spacing]=new_aseg[slice, :, :]
        orig_slice[spacing:-spacing, spacing:-spacing] =new_orig[slice, :, :]

        slices_aseg.append(aseg_slice)
        slices_orig.append(orig_slice)

    # create screenshots for sagittal view
    img_orig = save_slices_grid(slices_orig, "gray", out_dir, 'orig_sagittal', 0,order=3)
    img_aseg = save_slices_grid(slices_aseg, cmap, out_dir, 'aseg_sagittal', 0,order=0,)
    img_over = save_slices_overlay(img_orig, img_aseg, out_dir, 'overlay_sagittal')
    save_slices_dual(img_orig, img_over, out_dir, "dual_sagittal",image_extension=image_extension)
    
    # remove intermediate files to save space 
    os.remove(img_orig)
    #print ("File %s is removed"%img_orig)
    os.remove(img_aseg)
    #print ("File %s is removed"%img_aseg)
    os.remove(img_over)
    #print ("File %s is removed"%img_over)
    
    # stack axial slices 
    slices_orig = []
    slices_aseg = []
    # Extract Starting and finish point for the axial plane
    axial_labels_idx=np.where(new_aseg>0)
    axial_start=max(np.min(axial_labels_idx[1])-padd//2,0)
    axial_finish=min(np.max(axial_labels_idx[1])+padd//2,new_aseg.shape[1])
    axial_idx=np.round(np.linspace(axial_start,axial_finish,num_slices))

    for i in axial_idx[:-1]:
        slice=int(np.floor(i))
        aseg_slice = np.zeros((spacing_size, spacing_size))
        orig_slice = np.zeros((spacing_size, spacing_size))
        aseg_slice[spacing:-spacing,spacing:-spacing] = new_aseg[:, slice, :]
        orig_slice[spacing:-spacing,spacing:-spacing] = new_orig[:, slice, :]
        slices_aseg.append(aseg_slice)
        slices_orig.append(orig_slice)

    # create screenshots for axial view
    img_orig = save_slices_grid(slices_orig, "gray", out_dir, 'orig_axial',90,order=3,)
    img_aseg = save_slices_grid(slices_aseg, cmap, out_dir, 'aseg_axial',90,order=0,)
    img_over = save_slices_overlay(img_orig, img_aseg, out_dir, 'overlay_axial')
    save_slices_dual(img_orig, img_over, out_dir, "dual_axial",image_extension=image_extension)
    
    # remove intermediate files to save space 
    os.remove(img_orig)
    #print ("File %s is removed"%img_orig)
    os.remove(img_aseg)
    #print ("File %s is removed"%img_aseg)
    os.remove(img_over)
    #print ("File %s is removed"%img_over)

    del cmap ,orig,new_orig,aseg, aseg_map, new_aseg

    dual_sagittal = os.path.abspath(out_dir + "dual_sagittal" + image_extension)
    dual_axial = os.path.abspath(out_dir + "dual_axial" + image_extension)

    return dual_sagittal,dual_axial

