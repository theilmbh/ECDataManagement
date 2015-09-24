
# Merge stimuli information from spike2 mat file into Kwik file

import h5py as h5
import tables
import os
import scipy.io as spio
import numpy as np

experiment_folder = '/home/btheilma/experiments/'

# Bird Information
birdID = 1215
birdID_str = 'st' + str(birdID)

bird_folder = experiment_folder + birdID_str 
kwik_folder = bird_folder +'/man_sort/pen2/'
spike2mat_folder = bird_folder + '/matfiles/'

# These are required just because things are not in the right format right now
s2_data_folder = spike2mat_folder + 'Pen01_Rgt_AP500_ML1000__Site01_Z2000__st1215_cat_P01_S01_2ndPen/'
s2_data_file = s2_data_folder + 'Subst1215Pen01Site01Epc01File01_06-30-15+20-42-42_st1215_block.mat'

kwik_data_file = kwik_folder + 'st1215_cat_P01_S01_2ndPen.kwik'

#Import files
        
kkfile = tables.open_file(kwik_data_file, 'r+')
kkfile.get_node('/')
test = np.array(kkfile.get_node('/channel_groups/0/spikes/recording'))
np.shape(test)

recording_60 = []
recording_62 = []
samps_stim_start = []
samps_stim_end = []
stim_name_store = []

print(s2_data_file)

recording_start_seconds = 26.011481
#Open spike2 mat file, readonly
f = h5.File(s2_data_file, 'r')

# Get DigMark Information
f_dm = f['DigMark']

#Convert all DigMark codes to numpy array
codes = np.array(f_dm['codes'])

# Only the first row matters
codes = codes[0, :]
np.shape(codes)

# Get the times for each code
times = np.transpose(np.array(f_dm['times']))

# Get Sampling rate / frequency
dt = f['Port_1']['interval'][0]
fs = 1.0/dt
    
# Build array of samples / times at which events occur: event 60 Start of Stimulus
times_60 = times[codes == 60] - recording_start_seconds
samps_60 = np.floor(fs*times_60)  # this is iffy...

    
# Event 62: End of stimulus
times_62 = times[codes == 62] - recording_start_seconds
samps_62 = np.floor(fs*times_62)

# Event 41: end of intertrial interval trial
times_41 = times[codes == 41] - recording_start_seconds
samps_41 = np.floor(fs*times_41)

# Event 40: start of intertrial interval
times_40 = times[codes == 40] - recording_start_seconds
samps_40 = np.floor(fs*times_40)
    
# Get Stimulus names    
n_stimfiles = (np.size(np.array(f['stimulus_textmark']['text'][0, :])) - 1)/2
stimfile_name_inds = 2*(np.array(range(n_stimfiles)) +1)
for ind in stimfile_name_inds:
    stimname = str()
    for val in np.array(f['stimulus_textmark']['text'][:, ind]):
        if val != 0:
            stimname = stimname + chr(val)
    stim_name_store.append(stimname)    
        
    
    # Build EArrays
    
samps_stim_start = np.squeeze(samps_60)
samps_stim_end = np.squeeze(samps_62)
samps_intertrial_end = np.squeeze(samps_41)
samps_intertrial_start = np.squeeze(samps_40)

kkfile.create_group("/", "event_types", "event_types")
kkfile.create_group("/event_types", "60", "stim_start")
kkfile.createEArray("/event_types/60", 'time_samples', obj=samps_stim_start)
kkfile.createEArray("/event_types/60", "stim_filename", obj=stim_name_store)

kkfile.create_group("/event_types", "62", "stim_end")
kkfile.createEArray("/event_types/62", 'time_samples', obj=samps_stim_end)
kkfile.createEArray("/event_types/62", "stim_filename", obj=stim_name_store)

kkfile.create_group("/event_types", "40", "intertrial_start")
kkfile.createEArray("/event_types/40", 'time_samples', obj=samps_intertrial_start)


kkfile.create_group("/event_types", "41", "intertrial_end")
kkfile.createEArray("/event_types/41", 'time_samples', obj=samps_intertrial_end)

kkfile.close()



    
    
    
