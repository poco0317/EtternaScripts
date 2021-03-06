import xml.etree.ElementTree
e = xml.etree.ElementTree.parse("Stats.xml").getroot()

packnames = set()

##
#   This just generates a list of unique packs that the user has scores on from Stats.xml
#   The reason for this is that Etterna.xml will not generate scores (and Etterna itself will
#   not generate an XML) for scores which cannot be calculated from files.
#   So if you don't load the song, the score will not be calculated.
#   Using this, you can find out which packs you need to properly generate an Etterna.xml from your stats.xml.
##

def getSection(xml, sectionName):
    for section in xml:
        if section.tag == sectionName:
            return section
    return None

section = getSection(e, "SongScores")
if section is not None:

    for song in section:
        try:
            packnames.add(song.attrib["Dir"].split("/")[1])
        except:
            pass

    print("\n".join(sorted(packnames)))
else:
    print("Failed due to missing section")