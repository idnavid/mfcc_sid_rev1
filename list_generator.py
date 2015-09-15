#! /usr/bin/python

import sys

in_file_list = sys.argv[1]
HCopy = '/export/bin/HCopy '
config = '/home/nxs113020/bin/create_mfcc.conf '
out_dir = ' /scratch2/nxs113020/feature_extraction/mfcc_sid/features/'

out_jobs = './mfcc.jobs'
fout = open(out_jobs,'w')
for i in open(in_file_list):
  file_name = i.strip()
  base_name = file_name.split('/')[-1].split('.wav')[0].strip()
  out_name = out_dir+base_name+'.htk'
  fout.write(HCopy+'-C '+config+file_name+out_name+'\n')

