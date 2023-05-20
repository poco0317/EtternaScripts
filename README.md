# EtternaScripts
Within the many folders here, you will find a bunch of small scripts I've written as time passed which has facilitated my development or fascination with Etterna and Stepmania in some way.

All scripts are written based on Python 3.7 with the intent of requiring as few extra libraries as possible other than numpy or matplotlib.

## AudioAggregator
I wrote this when I wanted a way to be able to copy every audio file in my Songs directory to a single location so that I could listen to them without needing to use the Stepmania Jukebox.
This script should work infinitely recursively, so it won't just work on a Stepmania Songs folder.

Execution: Run the script and supply an input directory (with any number of subdirectories within it) and an output directory.

## MP3Converter
I wrote this when I wanted to convert every audio file in my game to the ogg format. Of course later on I figured out that doing this caused most songs to desync. Nevertheless, here is the script.

Execution: REQUIRES FFMEG. FFMPEG either needs to be in PATH or in the same directory as the script. The script needs to be located within the Songs directory OR a single pack's directory. Upon correctly running (there are instructions), it should then convert most files properly and also change the associated sm files accordingly.

Note: This is only written with dwi and sm compatibility in mind. Files with invalid utf 8 may break dramatically.

## OldLeaderboardifier
This takes a modern Etterna.xml and outputs a csv version of its scores for spreadsheet viewing purposes.

Execution: Run the script and supply an input filename, player name, and output filename

## PackMassExtractor
I wrote this because at one point I mirrored all of StepmaniaOnline to a single location and decided that extracting it to run in the game was a good idea. Well, 7zip did a good enough job of extracting all the pack zips to a single directory. Then I was left with many folders with improper structure so they couldn't immediately be loaded into the game. One level of directories needed to be removed in order for them to load from a single folder.

So this program accomplishes the following simply: Go through every folder in the input directory. Inside of each of these folders, move the first found subdirectory to the output location. Repeat. It is not totally recursive, and is primarily useful for the Stepmania pack format.

Execution: Run the script and provide an input and output directory according to the instructions.


## PackStatAggregator
This takes a folder of zipped packs (because it was written specifically for a compressed mirror of StepmaniaOnline) and parses all sm and dwi files metadata. It builds a csv where each line is the pack name matched with the earliest date and time of the modified sm/dwi file in the pack. The purpose is to get an idea of what the earliest created pack might be.

Execution: Place the script into a folder containing many zipped packs. Run. Consume the output.csv.


## StatsReader
Simply output the list of unique packs that a single Stats.xml contains. Place this script into the same directory as a Stats.xml and run it.

Why? Etterna cannot generate an Etterna.xml for a Stats.xml which points to nonexistent songs. For the game to be able to verify that scores are real and to generate an actual SSR value for them, it has to be able to match them with songs that are loaded. So the game requires that all songs are loaded in order to generate an Etterna.xml from an older Stats.xml. This script is used to quickly grab a list of packs from the Stats.xml in order to easily acquire those packs to load into Etterna and generate the Etterna.xml properly.


## XMLAnalyzer
I wrote this because everyone deserves an analysis of their sessions. This script will parse a given Etterna.xml and provide you with several options. You may choose to build a graph of the skillsets over time, build a graph of all PBs filtered by skillset or percentage, or build a graph of every single score on the profile filtered by skillset or percentage. The PB graph can also filter out scores which do not have the selected skillset as the highest when using the skillset filter. Each option has a sane default. A custom size for the output graphs can be defined at the end of each process.

Execution: Run the script and read the prompt.

Example Images:

<img src="https://user-images.githubusercontent.com/2531164/60688638-10699900-9e7c-11e9-8687-00015fc0a9bd.png" width="720">
<img src="https://user-images.githubusercontent.com/2531164/60688647-1eb7b500-9e7c-11e9-87a8-79a364448300.png" width="720">
<img src="https://user-images.githubusercontent.com/2531164/60688651-211a0f00-9e7c-11e9-856d-63bed945282b.png" width="720">


## XMLMerger
I wrote this script because sometimes people have multiple Etterna.xml files or profiles and they might need to merge them for some reason. Of course the game can actually already do this, but sometimes you don't have access to the game or the process may take far longer than you want. So what this does is not so carefully mash two given Etterna.xml files together. It can even take the same one twice. I wouldn't recommend it. The comments in the code very slightly explain why some decisions regarding merging were done. In short, I was lazy. But the resulting profile will still run. It may look very malformed in an XML viewer or text editor, but the game handles it well.

Execution: Run the script and read the prompt.
