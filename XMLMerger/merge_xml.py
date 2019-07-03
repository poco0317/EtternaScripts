import codecs
import datetime
import math
import xml.etree.ElementTree
import traceback

##
####
#######
##########
#######
#######
#######
####### If you use this for illicit purposes, such as stealing scores from another user and uploading them as your own,
####### we will find you. Someone will. This is meant for archival or data-saving purposes.
#######
#######

print("This will merge 2 individual Etterna XMLs.")
print("Enter the name of the XML to merge into.")
filename = input()

e = None
try:
    e = xml.etree.ElementTree.parse(filename).getroot()
except:
    try:
        with codecs.open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            contents = f.read()
        e = xml.etree.ElementTree.fromstring(contents, xml.etree.ElementTree.XMLParser(encoding='utf-8'))
    except:
        print("You failed to enter a valid choice. I'll try Etterna.xml")
        filename = "Etterna.xml"
        try:
            with codecs.open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                contents = f.read()
            e = xml.etree.ElementTree.fromstring(contents, xml.etree.ElementTree.XMLParser(encoding='utf-8'))
        except:
            print("It still failed.")
            exit()

print("Enter the name of the XML to merge into the main XML.")
filename2 = input()

e2 = None
try:
    e2 = xml.etree.ElementTree.parse(filename2).getroot()
except:
    try:
        with codecs.open(filename2, 'r', encoding='utf-8', errors='ignore') as f:
            contents = f.read()
        e2 = xml.etree.ElementTree.fromstring(contents, xml.etree.ElementTree.XMLParser(encoding='utf-8'))
    except:
        print("You failed to enter a valid choice. I'll try Etterna2.xml")
        filename = "Etterna2.xml"
        try:
            with codecs.open(filename2, 'r', encoding='utf-8', errors='ignore') as f:
                contents = f.read()
            e2 = xml.etree.ElementTree.fromstring(contents, xml.etree.ElementTree.XMLParser(encoding='utf-8'))
        except:
            print("It still failed.")
            exit()


# Each modern Etterna XML usually has up to 6 sections (in a single giant <Stats> section)
# These sections are always in this order:
# GeneralData, Favorites, Permamirror, Playlists, ScoreGoals, PlayerScores
# We want to merge the XMLs to produce a super XML of both while hopefully staying consistent
# in terms of keeping certain TopScore values with scores. That'll be the hardest part.

def findSection(xml, sectionName):
    ''' Find a section of the XML by name. Return None if no section exists.'''
    for x in xml:
        if x.tag == sectionName:
            return x
    return None

# GeneralData. This contains literally general data and info about the profile.
# I'm expecting this to be already filled out so I won't mess with it.

# Favorites. This contains a list of chartkeys as tag endings, simply enough.
# We can merge this.

e_favorite_section = findSection(e, "Favorites")
e2_favorite_section = findSection(e2, "Favorites")
favorite_keys = set()
if e_favorite_section is not None:
    print("Main xml favorite size", len(e_favorite_section))
    for k in list(e_favorite_section):
        favorite_keys.add(k.tag)
if e2_favorite_section is not None:
    print("Second xml favorite size", len(e2_favorite_section))
    for k in list(e2_favorite_section):
        favorite_keys.add(k.tag)
favorites_Element = None
if len(favorite_keys) > 0:
    favorites_Element = xml.etree.ElementTree.Element("Favorites")
    for k in favorite_keys:
        xml.etree.ElementTree.SubElement(favorites_Element, k)
    print("Final xml favorite size", len(favorites_Element))


# Permamirror. This contains a list of chartkeys as permamirror charts, simply enough.
# We can merge this.

e_permamirror_section = findSection(e, "PermaMirror")
e2_permamirror_section = findSection(e2, "PermaMirror")
permamirror_keys = set()
if e_permamirror_section is not None:
    print("Main xml permamirror size", len(e_permamirror_section))
    for k in list(e_permamirror_section):
        permamirror_keys.add(k.tag)
if e2_permamirror_section is not None:
    print("Second xml permamirror size", len(e2_permamirror_section))
    for k in list(e2_permamirror_section):
        permamirror_keys.add(k.tag)
permamirror_Element = None
if len(permamirror_keys) > 0:
    permamirror_Element = xml.etree.ElementTree.Element("PermaMirror")
    for k in permamirror_keys:
        xml.etree.ElementTree.SubElement(permamirror_Element, k)
    print("Final xml permamirror size", len(permamirror_Element))


# Playlists. This contains a list of Playlists. Each Playlist has a Name attribute and contains a Chartlist.
# Each Chartlist contains a bunch of Charts with attributes Key, Pack, Rate, Song, and Steps.
# We can merge this.
# This merge SKIPS playlists that already exist.

e_playlist_section = findSection(e, "Playlists")
e2_playlist_section = findSection(e2, "Playlists")
e3_playlist_section = None
if e_playlist_section is not None or e2_playlist_section is not None:
    e3_playlist_section = xml.etree.ElementTree.Element("Playlists")
    playlists = {}
    if e_playlist_section is not None:
        print("Main xml playlist size", len(e_playlist_section))
        for playlist in list(e_playlist_section):
            name = playlist.attrib["Name"]
            if name not in playlists:
                playlists[name] = []
                for chart in list(playlist[0]):
                    chart_dict = {}
                    for a,v in chart.attrib.items():
                        chart_dict[a] = v
                    playlists[name].append(chart_dict)
    if e2_playlist_section is not None:
        print("Second xml playlist size", len(e2_playlist_section))
        for playlist in list(e2_playlist_section):
            name = playlist.attrib["Name"]
            if name not in playlists:
                playlists[name] = []
                for chart in list(playlist[0]):
                    chart_dict = {}
                    for a,v in chart.attrib.items():
                        chart_dict[a] = v
                    playlists[name].append(chart_dict)
    for playlist, charts in playlists.items():
        playlist_element = xml.etree.ElementTree.SubElement(e3_playlist_section, "Playlist")
        playlist_element.set("Name", playlist)
        chartlist_element = xml.etree.ElementTree.SubElement(playlist_element, "Chartlist")
        for chart in charts:
            chart_element = xml.etree.ElementTree.SubElement(chartlist_element, "Chart")
            for k,v in chart.items():
                chart_element.set(k,v)
    print("Final xml playlist size", len(e3_playlist_section))

# ScoreGoals. This section contains a GoalsForChart for a set Chartkey.
# Each subElement of GoalsForChart is a ScoreGoal containing regular set text for tags about the goal.
# Using the same method as above, merge the lists of goals but restrict to let the first
# XML have priority over the second when it comes to goals per chart. One list will be imported.
e_goal_section = findSection(e, "ScoreGoals")
e2_goal_section = findSection(e2, "ScoreGoals")
e3_goal_section = None
if e_goal_section is not None or e2_goal_section is not None:
    e3_goal_section = xml.etree.ElementTree.Element("ScoreGoals")
    goals = {}
    if e_goal_section is not None:
        print("Main xml goal size",len(e_goal_section))
        for goals_for_chart in list(e_goal_section):
            key = goals_for_chart.attrib["Key"]
            if key not in goals:
                goals[key] = []
                for goal in list(goals_for_chart):
                    goal_dict = {}
                    for attribute in list(goal):
                        goal_dict[attribute.tag] = attribute.text
                    goals[key].append(goal_dict)
    if e2_goal_section is not None:
        print("Second xml goal size",len(e2_goal_section))
        for goals_for_chart in list(e2_goal_section):
            key = goals_for_chart.attrib["Key"]
            if key not in goals:
                goals[key] = []
                for goal in list(goals_for_chart):
                    goal_dict = {}
                    for attribute in list(goal):
                        goal_dict[attribute.tag] = attribute.text
                    goals[key].append(goal_dict)
    for chartgoal, goal_list in goals.items():
        list_element = xml.etree.ElementTree.SubElement(e3_goal_section, "GoalsForChart")
        list_element.set("Key", chartgoal)
        for goal in goal_list:
            goal_element = xml.etree.ElementTree.SubElement(list_element, "ScoreGoal")
            for k,v in goal.items():
                subE = xml.etree.ElementTree.SubElement(goal_element, k)
                subE.text = v
    print("Final goal size",len(e3_goal_section))

# PlayScores.
# This is the largest and most important piece of information.
# Merging this is very tough.
# Consider: Each score is organized by Chart Key. Beyond that, it is organized by lists of scores at a rate.
# Each score has a TopScore status. This status is likely to change (and should be recalculated by the game anyways)
# Due to astronomical amounts of laziness, I have chosen to just cram the elements all into one pile.
# (and also filter out duplicates in the process)
all_scores = {}
e_score_section = findSection(e, "PlayerScores")
e2_score_section = findSection(e2, "PlayerScores")

if e_score_section is not None:
    print("Main xml score size", len(e_score_section))
    for chart in list(e_score_section):
        key = chart.attrib["Key"]
        if key not in all_scores:
            all_scores[key] = chart
        else:
            for scoresat in list(chart):
                all_scores[key].append(scoresat)

if e2_score_section is not None:
    print("Second xml score size", len(e2_score_section))
    for chart in list(e2_score_section):
        key = chart.attrib["Key"]
        if key not in all_scores:
            all_scores[key] = chart
        else:
            for scoresat in list(chart):
                all_scores[key].append(scoresat)
e3_score_section = None
if len(all_scores) > 0:
    e3_score_section = xml.etree.ElementTree.Element("PlayerScores")
    for chart_element in all_scores.values():
        e3_score_section.append(chart_element)
    print("Final xml score size", len(e3_score_section))
        


# Outputting the xml.
root = xml.etree.ElementTree.Element("Stats")
e_generaldata = findSection(e, "GeneralData")
if e_generaldata is None:
    print("The first XML is missing general data so I quit.")
    exit()

root.append(e_generaldata)
if favorites_Element is not None:
    root.append(favorites_Element)
if permamirror_Element is not None:
    root.append(permamirror_Element)
if e3_playlist_section is not None:
    root.append(e3_playlist_section)
if e3_goal_section is not None:
    root.append(e3_goal_section)
if e3_score_section is not None:
    root.append(e3_score_section)

print("Give an output filename or press enter to default.")
out = input()
if out == "" or out[-4:] != ".xml":
    out = "Etterna_Merged_defaulted.xml"

tree = xml.etree.ElementTree.ElementTree(root)
tree.write(out)