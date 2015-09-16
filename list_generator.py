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

# Configuration file:
# Currently extracts 12 dimensional MFCCs + D + DD (=36 dimensional). w/o Co
config = './create_mfcc.conf '

# Directory to store features:
out_dir = ' /erasable/nxs113020/features/'
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
