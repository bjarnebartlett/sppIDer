__author__ = 'Quinn'

import argparse, multiprocessing, sys, re, subprocess, time

################################################################
# This script runs the full sppIDer pipeline.
# Before running this you must make your combination reference genome with the script combineRefGenomes.py
# This script will map short-read data to a combination reference genome and parse the outputs to create a summary of
# where and how well the reads map to each species in the combinaiton reference genome.
#
#Program Requirements: bwa, samtools, bedtools, R, Rpackage ggplot2, Rpackage dplyr
#Input: Output name, Combination reference genome, fastq short-read files
#
################################################################

parser = argparse.ArgumentParser(description="Run bedtools sppider part")
parser.add_argument('--out', help="Output prefix, required", required=True)
parser.add_argument('--byBP', help="Calculate coverage by basepair, optional, DEFAULT, can't be used with -byGroup", dest='bed', action='store_true')
parser.add_argument('--byGroup', help="Calculate coverage by chunks of same coverage, optional, can't be used with -byBP", dest='bed', action='store_false')
parser.set_defaults(bed=True)
args = parser.parse_args()

# docker vars
scriptDir = "/tmp/sppIDer/"
workingDir = "/tmp/sppIDer/working/"
numCores = str(multiprocessing.cpu_count())

outputPrefix = args.out
start = time.time()
def calcElapsedTime( endTime ):
    trackedTime = str()
    if 60 < endTime < 3600:
        min = int(endTime) / 60
        sec = int(endTime - (min * 60))
        trackedTime = "%s mins %s secs" % (min, sec)
    elif 3600 < endTime < 86400:
        hr = int(endTime) / 3600
        min = int((endTime - (hr * 3600)) / 60)
        sec = int(endTime - ((hr * 60) * 60 + (min * 60)))
        trackedTime = "%s hrs %s mins %s secs" % (hr, min, sec)
    elif 86400 < endTime < 604800:
        day = int(endTime) / 86400
        hr = int((endTime - (day * 86400)) / 3600)
        min = int((endTime - (hr * 3600 + day * 86400)) / 60)
        sec = int(endTime - ((day * 86400) + (hr * 3600) + (min * 60)))
        trackedTime = "%s days %s hrs %s mins %s secs" % (day, hr, min, sec)
    elif 604800 < endTime:
        week = int(endTime) / 604800
        day = int((endTime)-(week * 604800) / 86400)
        hr = int((endTime - (day * 86400 + week * 604800)) / 3600)
        min = int((endTime - (hr * 3600 + day * 86400 + week * 604800)) / 60)
        sec = int(endTime - ((week * 604800) + (day * 86400) + (hr * 3600) + (min * 60)))
        trackedTime = "%s weeks %s days %s hrs %s mins %s secs" % (week, day, hr, min, sec)
    else:
        trackedTime = str(int(endTime)) + " secs"
    return trackedTime

trackerOut = open(workingDir + outputPrefix + "_sppIDerRun.info", 'w')
trackerOut.write("outputPrefix="+args.out+"\n")
if args.bed == False:
    trackerOut.write("coverage analysis option =  by coverage groups, bedgraph format -bga\n")
else: trackerOut.write("coverage analysis option = by each base pair -d\n")
trackerOut.close()

########################## samtools - set variable only###########################
bamSortOut = outputPrefix + ".sort.bam"

########################## bedgraph Coverage ###########################
sortOut = bamSortOut
if args.bed == True:
    bedOutD = outputPrefix + "-d.bedgraph"
    bedFileD = open(workingDir + bedOutD, 'w')
    subprocess.call(["genomeCoverageBed", "-d", "-ibam", sortOut], stdout=bedFileD, cwd=workingDir)
    bedFileD.close()
else:
    bedOut = outputPrefix + ".bedgraph"
    bedFile = open(workingDir + bedOut, 'w')
    subprocess.call(["genomeCoverageBed", "-bga", "-ibam", sortOut], stdout=bedFile, cwd=workingDir)
    bedFile.close()
print("bedgraph complete")
currentTime = time.time()-start
elapsedTime = calcElapsedTime(currentTime)
print("Elapsed time: " + elapsedTime)
trackerOut = open(workingDir + outputPrefix + "_sppIDerRun.info", 'a')
trackerOut.write("\nbedgraph complete\nElapsed time: " + elapsedTime)
trackerOut.close()
