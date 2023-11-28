from collections import OrderedDict
import os

def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]



def get_lut():

    if "FREESURFER_HOME" in os.environ:
        lookup_table_path = os.path.join(os.environ.get('FREESURFER_HOME'), 'FreeSurferColorLUT.txt')
    else:
        lookup_table_path = '/opt/freesurfer/FreeSurferColorLUT.txt'

    lut = OrderedDict()
    with open(lookup_table_path, 'r') as f:
        for line in f:
            if line[0] == '#' or line[0] == '\n':
                pass
            else:
                clean_line = remove_values_from_list(line.split(' '), '')
                rgb = [int(clean_line[2]), int(clean_line[3]), int(clean_line[4])]
                lut[str(clean_line[0])] = rgb
    return lut

