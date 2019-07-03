import re
import os
import glob
import subprocess
import multiprocessing
from multiprocessing.pool import ThreadPool
import traceback
import codecs

amountfinished = 0
def caller(input, output, filename, remaining, path):
    try:
        print("Converting File: "+filename+". "+str(len(processes) - remaining)+" left in queue.")
        g = subprocess.Popen("ffmpeg -y -loglevel 0 -i pipe:0 -c:a libvorbis -q:a 4 -f ogg pipe:1", stdin=input, stdout=output)
        o,e = g.communicate()
        return (True, filename, path)
    except:
        print("\n\n\n-----WARNING: THIS FILE DID NOT CONVERT!!! (will dump a list at the end)\n"+path+"\n\n\n")
        return (False, filename, path)

def replaceLine(searchFor, extFrom, extTo, filename):
    ''' replace a line of text with another line instead '''
    with codecs.open(filename, 'r', encoding='utf-8', errors="ignore") as file:
        lines = file.readlines()
    for i in range(len(lines)):
        if re.search(searchFor, lines[i]):
            lines[i] = searchFor+"ConvertedFile.ogg;\n"
    with codecs.open(filename, 'w', encoding='utf-8', errors="ignore") as file:
        file.writelines( lines )
        
def undoConvert(case):
    ''' undo the replacing of a line of text 
    case should be made up of a file name and a file name with its full path'''
    songFolder = os.path.dirname(case[1])
    metafiles = [content for content in os.scandir(songFolder) if content.is_file()]
    for metafile in metafiles:
        name, ext = os.path.splitext(metafile)
        if ext.lower() == ".dwi":
            try:
                with codecs.open(name+ext, "r", encoding='utf-8', errors='ignore') as file:
                    lines = file.readlines()
                for i in range(len(lines)):
                    if re.search("#FILE:", lines[i]):
                        lines[i] = "#FILE:"+case[0]+"\n"
                with codecs.open(name+ext, "w", encoding='utf-8', errors='ignore') as file:
                    file.writelines( lines )
            except:
                print("*dead*")
                traceback.print_exc()
        elif ext.lower() == ".sm" or ext.lower() == ".ssc":
            try:
                with codecs.open(name+ext, "r", encoding='utf-8', errors='ignore') as file:
                    lines = file.readlines()
                for i in range(len(lines)):
                    if re.search("#MUSIC:", lines[i]):
                        lines[i] = "#MUSIC:"+case[0]+"\n"
                with codecs.open(name+ext, "w", encoding='utf-8', errors='ignore') as file:
                    file.writelines( lines )
            except:
                print("*dead*")
                traceback.print_exc()


    
print("READ THIS BEFORE STARTING")
print("Are you sure you want to do this? This is your last chance to back out.")
print("I will be iterating over every pack you have and converting every mp3 file to ogg.")
print("This will take up a very large amount of cpu resources.")
print("I will be modifying each sm, ssc, and dwi file within those folders to match to a file named 'ConvertedFile.ogg'")
print("If that file does not exist (ie, admin problems, conversion failed, or some dumb shit happened) then you gotta fix it yourself.")
print("I skip cases where no mp3 file is present in the directory. If multiple are present, you may pray to God it works.")
print("Be aware that if any file has some REALLY dumb encoding then a lot of stuff may go missing from it as well.")
print("Sometimes files like to randomly not convert. If that is the case, then we undo the changes done to the folder.")
print("The iteration process is per-pack. Basically, things aren't 'done' until a pack has been fully processed. Then it moves forward.")
print("On top of all of that: If you stop early, none of the converted oggs work. :)")
print("Known bugs:\nMultiple mp3s in one folder can really mess things up.")
print("Converted files are not deleted, therefore your storage requirements may double!!! I went from 55gb to 88gb after using this.")
print("Converted files do not dump data into their folders until the whole process finishes.")
print("\nThis process may take Hit enter to begin or close this to get out.")
input()

print("\n\nEnter a number here to determine how many threads we will create.")
print("A safe number is something less than 10. Definitely 4. Entering a number above 16 could be dangerous. The limit is 32 for your absolute safety.")
print("Often the number used is related to how many cores or threads your CPU has.")
print("These threads will be used to parallel process the conversions of the mp3 files.")
print("With 8 threads and 11500 files, the process took a little over 2 hours.")
print("Enter the number now and then we will begin:")
threads = 0
while (threads < 1 or threads > 32):
    print("Enter a number between 1 and 32.")
    try:
        threads = int(input())
    except:
        pass



packs = [folder for folder in os.scandir() if folder.is_dir()]

failed = []

print("Beginning the reaping... Don't stop this process without restarting again or you will probably have significant issues")
for pack in packs:
    pool = ThreadPool(threads)

    processes = []
    filesOpened = []
    print("Working in Pack: "+pack.name)
    files = [folder for folder in os.scandir(pack) if folder.is_dir()]

    for file in files:
        mp3found = False
        print("\tWorking in Folder: "+file.name)
        metafiles = [content for content in os.scandir(file) if content.is_file()]
        for metafile in metafiles:
            #print("\t\tMetafile: "+metafile.name)
            try:
                name, ext = os.path.splitext(metafile)
                if ext.lower() == ".mp3":
                    mp3found = True
                    output = codecs.open(os.path.dirname(name+ext)+"/ConvertedFile.ogg", "w", errors="ignore")
                    input = codecs.open(name+ext, "r", errors="ignore")
                    filesOpened.append(output)
                    filesOpened.append(input)
                    remaining = len(processes)
                    stds = [input, output, metafile.name, remaining, name+ext]
                    processes.append(pool.apply_async(caller, stds))
            except:
                print("oops")
                traceback.print_exc()
        if mp3found:
            for metafile in metafiles:
                if ext.lower() == ".dwi":
                    try:
                        replaceLine("#FILE:", ".mp3", ".ogg", name+ext)
                    except:
                        print("*dead*")
                        traceback.print_exc()
                if ext.lower() == ".sm" or ext.lower() == ".ssc":
                    try:
                        replaceLine("#MUSIC:", ".mp3", ".ogg", name+ext)
                    except:
                        print("*dead*")
                        traceback.print_exc()
    pool.close()
    pool.join()
    for process in processes:
        condition, filename, path = process.get()
        if condition == False:
            failed.append((filename, path))
    for thing in filesOpened:
        thing.close()
print("Finished queueing all processes. Please wait for them to finish. This may take a very long time.")
print("NOTE that if you reach this point and stop before it finishes you've put yourself in a bad situation because I also have already finished modifying your sm/dwi/ssc files.")

print()
for case in failed:
    print("Failed to convert: "+case[1])
    undoConvert(case)
print(str(len(failed))+" cases failed.")

for thing in filesOpened:
    thing.close()
    
print("Done.")