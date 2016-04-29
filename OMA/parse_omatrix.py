#!/usr/bin/env python
#
# Parse the OMA similarity (sparse) matrix into an edge list format:
# [protein1] [protein2] [sw_score]
#
# Author:  Arnold Kuzniar
# Version: 0.1
#

import os, re
import gzip

DAT_DIR = '/home/arni/Downloads/OMA.1.0.5/Cache/AllAll'
file_pattern = '[A-Z]{5}.gz' # five-letters species acronym

def read_matrix(fname):
   # Example: SOLLC/SOLTU.gz file
   # ... 
   # [20771, 4428, 141.9462445, 160, 174..324, 35..170, 388.887322],
   # ...
   #
   # Metadata:
   # 1) sequential number of protein (as internal ID) in the first FASTA file (SOLLC.fa)
   # 2) sequential number of protein (as internal ID) in the second FASTA file (SOLTU.fa)
   # 3) Smith-Waterman (SW) score of the pairwise optimal alignment
   # 4) evolutionary distance in PAM
   # 5) alignment range in the first protein
   # 6) alignment range in the second protein
   # 7) estimate of variance of evolutionary distance
   #
   with gzip.open(fname, 'r') as f:
      for line in f:
         if line.startswith('[') is True:
            line = re.sub('[\[\]\s):]+', '', line).rstrip(',')
            vec = line.split(',')
            yield vec


def write_graph(filepath):
   dirname, fname = os.path.split(filepath)
   species_1, species_2 = os.path.basename(dirname), os.path.splitext(fname)[0]
   outfile = '%s-%s.graph' % (species_1, species_2)
   print i, outfile
   if os.path.isfile(outfile) is True: return

   with open(outfile, 'a') as fout:
      for vec in read_matrix(filepath):
         try:
            pid_1, pid_2, sw_score = vec[0:3]
            line = '%s%05d\t%s%05d\t%.2f\n' % (species_1, int(pid_1), species_2, int(pid_2), float(sw_score))
            fout.write(line)
         except ValueError:
            pass

for root, dirs, files in os.walk(DAT_DIR):
   for fname in files:
      if re.search(file_pattern, fname):
         filepath = os.path.join(root, fname)
         write_graph(filepath)

