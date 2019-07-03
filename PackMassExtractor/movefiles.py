import shutil
import glob
import traceback

##
#   The purpose of this is to essentially remove 1 folder from an entire directory listing.
#   It was written because when I extracted all of SMO to one location, I ended up with things like
#   "songs/packname/packname/song/"
#   The proper format is "songs/packname/song/" and that is what this script tries to accomplish.
##

print("This requires an input directory and an output directory.")
print("These should probably be unique.")
print("Enter the directory from which to pull files.")
cool = input()
print("Enter the directory to throw all those files.")
epic = input()

files = glob.glob(f"{cool}*")
for f in files:
    try:
        g = glob.glob(f+"/*")
        if len(g) > 0:
            shutil.move(g[0], f"{epic}/")
    except:
        print("Failed to move a file... "+f)
        traceback.print_exc()