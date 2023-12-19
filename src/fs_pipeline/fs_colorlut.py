
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

