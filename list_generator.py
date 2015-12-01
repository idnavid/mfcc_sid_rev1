#! /usr/bin/python

# Grab a list of audio files and create a list of SGE 
# jobs to extract HTK features. 
import sys
import os.path
import os

### Read inputs:
# python list_generator.py audio_list.txt sph/wav/etc.
in_file_list = sys.argv[1]
if not(os.path.exists(in_file_list)):
    print "audio list was not found!"
    exit()

try:
    in_format = sys.argv[2] # For now the code only understands wav and sph.
except:
    print "audio format not specified. Assuming wav"
    in_format = 'wav'


### Pre-defined values:
HCopy = '/export/bin/HCopy '
FeatureSelect = '/export/bin/FeatureSelect '

# Configuration file:
# Currently extracts 12 dimensional MFCCs + D + DD (=36 dimensional). w/o Co
config = './create_mfcc.conf '

# Directory to store features:
out_dir = ' /erasable/nxs113020/mfcc_opensad/'
os.system('mkdir -p'+out_dir)
wav_dir = ' /erasable/nxs113020/wavs/' # To store wavs constructed from sph files.

# convert sph to wav command:
sph2wav = 'sph2pipe -f wav -p -c %s %s > %s/%s_%s.wav'

# Job list:
out_jobs = './mfcc.jobs'



fout = open(out_jobs,'w')
for i in open(in_file_list):
    file_name = i.strip()
    if (in_format == 'wav'):
        base_name = file_name.split('/')[-1].split('.wav')[0].strip()
        out_name = out_dir+base_name+'.htk'
        wav_name = file_name
        fout.write(HCopy+'-C '+config+wav_name+out_name+'\n')
    if (in_format == 'sph'):
        # First convert sph to wav:
        channel = file_name.split(':')[1]
        actual_file_name = file_name.split(':')[0]
        base_name = actual_file_name.split('/')[-1].split('.sph')[0].strip()
        wav_name = '%s/%s_%s.wav'%(wav_dir,base_name,channel)
        command1 = sph2wav%(channel,actual_file_name,wav_dir,base_name,channel)
        out_name = out_dir+base_name+'_'+channel+'.htk'
        fout.write(command1+';'+HCopy+'-C '+config+wav_name+out_name+'\n')

fout.close()

os.system("/home/nxs113020/bin/myJsplit -b 1 -M 400 %s"%(out_jobs))

exit()
## VAD jobs:
vad_dir = '/erasable/nxs113020/vad_labels/'

vad_command = 'python /scratch/nxs113020/speech_activity_detection/sad.py %s /scratch/nxs113020/speech_activity_detection/config_sad %s/%s idx'

fout = open('vad_jobs','w')
for i in open(in_file_list):
    file_name = i.strip() 
    if (in_format == 'wav'):
        wav_name = file_name
        base_name = actual_file_name.split('/')[-1].split('.wav')[0].strip()+'_1'
    if (in_format == 'sph'):
        channel = file_name.split(':')[1]
        actual_file_name = file_name.split(':')[0]
        base_name = actual_file_name.split('/')[-1].split('.sph')[0].strip()
        wav_name = '%s/%s_%s.wav'%(wav_dir,base_name,channel)
    command_line = vad_command%(wav_name,vad_dir,base_name+'_'+channel)
    fout.write(command_line+'\n')
fout.close()

## Create feature selection list. 
# Use VAD labels to replace features with new
# features that only have voiced frames. 
voiced_feature_dir = '/erasable/nxs113020/voiced_features/'

selection_command = FeatureSelect+' -m SFS -i %s/%s -o %s/%s -x %s/%s'

select_voiced_jobs = 'vad_selection_jobs.txt'
fout = open(select_voiced_jobs,'w')
for i in open(in_file_list):
    file_name = i.strip()
    base_name = file_name.split('/')[-1].split('.')[0].strip()
    if ':' in file_name:
        channel = file_name.split(':')[1]
        if (channel == 'A') or (channel == '1'):
            channel = '1'
        if (channel == 'B') or (channel == '2'):
            channel = '2'
    else:
        channel = '1'
    feature_name = base_name+'_'+channel+'.htk'
    vad_file_name = base_name+'_'+channel
    command_line = selection_command%(out_dir,feature_name,voiced_feature_dir,feature_name,vad_dir,vad_file_name)
    fout.write(command_line+'\n')
fout.close()
