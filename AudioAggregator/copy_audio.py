import re
import os
import shutil
import glob
import traceback


def recursivelyGetAudioFiles(dir):
    ''' get the files in a directory
    at this point, dir should be something like:
    C:/audiodirectory/
    returns a list of paths to audio files
    '''
    output = []
    folders = []
    try:
        folders = [x for x in os.scandir(dir) if not x.is_file()]
    except:
        folders = []
    types = ("*.wav", "*.mp3", "*.flac", "*.ogg", "*.mp4", "*.mov", "*.m4v")
    for type in types:
        try:
            output.extend([(x, re.search(r"([^\\/]*$)", x).group(0)) for x in glob.glob(os.path.join(dir, type))])
        except:
            traceback.print_exc()
    for folder in folders:
        path = os.path.splitext(folder)[0]
        output.extend(recursivelyGetAudioFiles(path + "/"))
    return output
    
print("Note: This will MAKE A COPY of all audio files found.")
print("Make sure you have space.")
print("Give an input directory. Enter nothing to default to current working dir")
indir = input()
if indir == "":
    indir = os.getcwd()
elif indir[-1] != "/":
    indir += "/"  
    
theList = recursivelyGetAudioFiles(indir)

if len(theList) == 0:
    print("No audio files found in this directory.")
    exit()

print("Give an output directory: ")
outdir = input()
if outdir[-1] != "/":
    outdir += "/"

for file in theList:
    try:
        shutil.copyfile(file[0], outdir + file[1])
    except:
        print()
        traceback.print_exc()
        print()
        print(file)
        print()