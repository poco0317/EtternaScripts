import datetime
import codecs
import xml.etree.ElementTree
import math
import traceback

skillsetConstants = ["Overall", "Stream", "Jumpstream", "Handstream", "JackSpeed", "Chordjack", "Technical", "Stamina"]

print("Enter filename")
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
    
# charts are on list(e[5]) if file is full of data, otherwise we find it...
indexOfCharts = 0
found = False
for i in range(len(e)):
    if e[i].tag == "PlayerScores":
        indexOfCharts = i
        found = True

if not found:
    print("XML did not have scores...?")
    exit()

print("Turn off limits? Press enter to ignore. Otherwise, type 'a'")
limiter = input()
noLimits = False
if limiter == "a":
    noLimits = True

SkillsetsWithDates = []

charts = list(e[indexOfCharts])
failed = 0

import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import numpy as np

topssrs = {}

def aggregateSSRs(skillset, rating, res, iter):
    sum = 0
    while True:
        sum = 0
        rating += res
        for i in range(len(topssrs[skillset])):
            sum += max(0, 2 / math.erfc(0.1 * (topssrs[skillset][i][0] - rating)) - 2)
        if 2 ** (rating * 0.1) >= sum:
            break
    if iter == 11:
        return rating
    return aggregateSSRs(skillset, rating - res, res / 2, iter + 1)

def aggregateSSRsByDate(dates, ssrs, skillset, rating, res, iter):
    sum = 0
    while True:
        sum = 0
        rating += res
        for date in dates:
            for x in ssrs[skillset][date]:
                sum += max(0, 2 / math.erfc(0.1 * (x - rating)) - 2)
        if 2 ** (rating * 0.1) >= sum:
            break
    if iter == 11:
        return rating
    return aggregateSSRsByDate(dates, ssrs, skillset, rating - res, res / 2, iter + 1)

def calcRating():
    skillz = {}
    output = {}
    for ss in skillsetConstants[1:]:
        output[ss] = aggregateSSRs(ss, 0, 10.24, 1) * 1.04
        skillz[ss] = output[ss]
    skills = sorted(list(skillz.values()))[1:]
    return {"Overall": sum(skills) / 6,
        "Stream" : skillz["Stream"],
        "Jumpstream" : skillz["Jumpstream"],
        "Handstream" : skillz["Handstream"],
        "Stamina" : skillz["Stamina"],
        "JackSpeed" : skillz["JackSpeed"],
        "Chordjack" : skillz["Chordjack"],
        "Technical" : skillz["Technical"]
    }

def calcRatingByDate():
    '''
    TopSSRs should be sorted by now so this will go smoothly.
    '''
    listOfRatingsByDate = {}
    for ss in skillsetConstants:
        listOfRatingsByDate[ss] = {}

    for skillset, grades in topssrs.items():
        for grade in grades:
            date = grade[1].replace(hour = 0, minute = 0, second = 0)
            if date not in listOfRatingsByDate[skillset]:
                listOfRatingsByDate[skillset][date] = [grade[0]]
            else:
                listOfRatingsByDate[skillset][date].append(grade[0])
    listOfDates = list(listOfRatingsByDate["Overall"].keys())
    earliestDate = datetime.datetime(year=2017, month=5, day=1)

    if noLimits:
        earliestDate = datetime.datetime(year=2001, month=1, day=1)

    for i in range(len(listOfDates)):
        if listOfDates[i] > earliestDate:
            listOfDates = listOfDates[i:]
            break
    
    SSRsByDates = {}
    for i in range(len(listOfDates)):
        print("On Date", i+1, "out of", len(listOfDates))
        skillz = []
        output = {}
        skillsets = skillsetConstants[1:]
        for ss in skillsets:
            output[ss] = aggregateSSRsByDate(listOfDates[:i], listOfRatingsByDate, ss, 0, 10.24, 1) * 1.04
            skillz.append(output[ss])
        skills = sorted(skillz)[1:]
        
        dayResults = {}
        dayResults["Overall"] = sum(skills) / 6
        for j in range(len(skillsets)):
            dayResults[skillsets[j]] = skillz[j]
        SSRsByDates[listOfDates[i]] = dayResults
    return SSRsByDates




def setAllTopSSRs(requiredAcc = 0):
    '''
    Note: This is for PBs only, and all invalid scores are ignored. This means no CC On. No Client Invalidated.
    '''
    failed = 0
    for chart in charts:
        for scores_at_rate in list(chart):
            pbkey = scores_at_rate.get("PBKey")
            for score in [x for x in list(scores_at_rate) if x.get("Key") == pbkey]:
                try:
                    if not isValid(score):
                        continue
                    if not fitsAcc(score, float(requiredAcc)):
                        continue
                    datime = datetime.datetime.strptime([" ".join(x.itertext()) for x in score.findall("DateTime")][0], "%Y-%m-%d %H:%M:%S")
                    for attribute in score.findall("SkillsetSSRs")[0]:
                        if attribute.tag in topssrs:
                            topssrs[attribute.tag].append((float(" ".join(attribute.itertext())), datime))
                        else:
                            topssrs[attribute.tag] = [(float(" ".join(attribute.itertext())), datime)]
                except:
                    failed += 1
                    #traceback.print_exc()
    for k,v in topssrs.items():
        topssrs[k] = sorted(v, key = lambda x: x[1])
    #print("Failed pb topssr counts", failed)

def isValid(score):
    if noLimits:
        return True
    for x in score.findall("EtternaValid"):
        if " ".join(x.itertext()) == "0":
            return False
    for x in score.findall("NoChordCohesion"):
        if " ".join(x.itertext()) == "0":
            return False
    return True

def fitsAcc(score, requiredAcc):
    try:
        for x in score.findall("SSRNormPercent"):
            if float(" ".join(x.itertext())) * 100 >= requiredAcc:
                return True
        return False
    except:
        return False

class InfoHolder:
    def __init__(self, date, skillsetdict, percent):
        self.date = date
        self.skillsets = skillsetdict
        self.overall = skillsetdict["Overall"]
        self.stream = skillsetdict["Stream"]
        self.jumpstream = skillsetdict["Jumpstream"]
        self.handstream = skillsetdict["Handstream"]
        self.stamina = skillsetdict["Stamina"]
        self.jackspeed = skillsetdict["JackSpeed"]
        self.chordjack = skillsetdict["Chordjack"]
        self.technical = skillsetdict["Technical"]
        self.percent = percent
    def __repr__(self):
        return str(self.date) + f" {self.percent * 100:.4f}% worth " + str(self.overall)
    def __str__(self):
        return str(self.date) + f" {self.percent * 100:.4f}% worth " + str(self.overall)


def getPBs(skillset, advancedFilter):
    '''
    Given the skillset, get the pbs
    returns a tuple of (dates, values) , {grade : (dates, values) }
    '''
    pbmap = {}

    failed = 0
    AAAAkeys = set()
    AAAkeys = set()
    AAkeys = set()
    for chart in charts:
        stuff = list(chart)
        for scres_at_rate in list(stuff):
            pbkey = scres_at_rate.get("PBKey")
            for score in [x for x in list(scres_at_rate) if x.get("Key") == pbkey]:
                try:
                    if pbkey not in pbmap:
                        newData = {}
                        for attribute in score.findall("SkillsetSSRs")[0]:
                            
                            if pbkey not in pbmap:
                                tag = attribute.tag
                                value = float(" ".join(attribute.itertext()))
                                newData[tag] = value
                        pbmap[pbkey] = newData
                        for attribute in score.findall("DateTime"):
                            pbmap[pbkey]["DateTime"] = " ".join(attribute.itertext())
                        for attribute in score.findall("WifeScore"):
                            if pbkey in pbmap:
                                thenum = float(" ".join(attribute.itertext()))
                                if thenum >= 0.9997:
                                    AAAAkeys.add(pbkey)
                                elif thenum >= 0.9975:
                                    AAAkeys.add(pbkey)
                                elif thenum >= 0.93:
                                    AAkeys.add(pbkey)
                except:
                    failed += 1
    overallWithDates = [data for (pb,data) in pbmap.items()]
    yeetus = sorted(overallWithDates, key = lambda kv: datetime.datetime.strptime(kv["DateTime"], "%Y-%m-%d %H:%M:%S"))

    def skippable(score):
        biggestSSVal = 0
        biggestSS = skillset
        for ss, val in score.items():
            if ss != "Overall" and ss != "DateTime" and val > biggestSSVal:
                biggestSSVal = val
                biggestSS = ss
        if biggestSS != skillset:
            return True
        return False

    if advancedFilter:
        skipped = 0
        for score in yeetus.copy():
            if skippable(score):
                yeetus.remove(score)
                skipped += 1
        print(f"Skipped {skipped} scores due to advanced skillset filtering.")

    dates = matplotlib.dates.date2num([datetime.datetime.strptime(x["DateTime"], "%Y-%m-%d %H:%M:%S") for x in yeetus])
    values = [float(x[skillset]) for x in yeetus]

    # these are all lists of overallWithDates dictionaries
    AAAAs = []
    AAAs = []
    AAs = []
    others = []

    for pbk, data in pbmap.items():
        if advancedFilter:
            if skippable(data):
                continue
                    
        if pbk in AAAAkeys:
            AAAAs.append(data)
        elif pbk in AAAkeys:
            AAAs.append(data)
        elif pbk in AAkeys:
            AAs.append(data)
        else:
            others.append(data)

    sortedGradesByDate = {
        "AAAA" : sorted(AAAAs, key = lambda kv: datetime.datetime.strptime(kv["DateTime"], "%Y-%m-%d %H:%M:%S")),
        "AAA" : sorted(AAAs, key = lambda kv: datetime.datetime.strptime(kv["DateTime"], "%Y-%m-%d %H:%M:%S")),
        "AA" : sorted(AAs, key = lambda kv: datetime.datetime.strptime(kv["DateTime"], "%Y-%m-%d %H:%M:%S")),
        "others" : sorted(others, key = lambda kv: datetime.datetime.strptime(kv["DateTime"], "%Y-%m-%d %H:%M:%S"))
    }

    output = {}
    for g in ("AAAA", "AAA", "AA", "others"):
        output[g] = (matplotlib.dates.date2num([datetime.datetime.strptime(x["DateTime"], "%Y-%m-%d %H:%M:%S") for x in sortedGradesByDate[g]]), [float(x[skillset]) for x in sortedGradesByDate[g]])

    return (dates, values),output

def getScores(skillset, advancedFilter):
    '''
    Given the skillset, get the scores
    Can filter.
    '''
    failed = 0
    skipped = 0
    for chart in charts:
        for scoresAtRate in list(chart):
            for score in scoresAtRate:
                try:
                    datime = datetime.datetime.strptime([" ".join(x.itertext()) for x in score.findall("DateTime")][0], "%Y-%m-%d %H:%M:%S")
                    inputinfo = {}
                    for attribute in score.findall("SkillsetSSRs")[0]:
                        tag = attribute.tag
                        value = float(" ".join(attribute.itertext()))
                        inputinfo[tag] = value

                    biggestSS = skillset
                    if advancedFilter:
                        biggestSSVal = 0
                        for ss,v in inputinfo.items():
                            if ss != "Overall" and v > biggestSSVal:
                                biggestSS = ss
                                biggestSSVal = v
                    if biggestSS == skillset:
                        percent = float([" ".join(x.itertext()) for x in score.findall("WifeScore")][0])
                        SkillsetsWithDates.append(InfoHolder( datime, inputinfo, percent))
                    else:
                        skipped += 1
                except:
                    #traceback.print_exc()
                    failed += 1                    

    SkillsetsWithDates.sort(key = lambda x: x.date)

    gradeNames = ("AAAA", "AAA", "AA", "A", "B", "C", "D", "F")
    def percentToName(num):
        if num >= .9997:
            return "AAAA"
        elif num >= .9975:
            return "AAA"
        elif num >= .93:
            return "AA"
        elif num >= .80:
            return "A"
        elif num >= .70:
            return "B"
        elif num >= .60:
            return "C"
        elif num >= 0:
            return "D"
        return "F"

    grades = {}
    for g in gradeNames:
        grades[g] = set()
    for thing in SkillsetsWithDates:
        grades[percentToName(thing.percent)].add(thing)

    for g in gradeNames[:-1]:
        print(f"{g} Scores", len(grades[g]))
    print("F Scores", failed)
    print(f"Disregarded {skipped} scores due to advanced filtering by highest skillset.")

    print("Earliest Score:", SkillsetsWithDates[0])
    print("Latest Score:", SkillsetsWithDates[-1])
    return grades

print("Show all scores or filter to PB only? Enter 'a' for PB only.")
option = input()

print("Skillset to measure?")
print("Valid input is: Overall, Stream, Jumpstream, Handstream, JackSpeed, Chordjack, Technical, Stamina")
valids = skillsetConstants
skillset = input()
if skillset not in valids:
    skillset = "Overall"
    print("Your skillset was not valid. Picked Overall.")

advancedFilter = False
if skillset != "Overall":
    print(f"Do you want advanced filtering? This removes all scores that don't have {skillset} as the highest skillset.\nEnter 'a' for no.")
    choice = input()
    if choice == 'a':
        advancedFilter = False
    else:
        advancedFilter = True

if option == "a":
    scores = getPBs(skillset, advancedFilter)
    colors = {
        "AAAA" : 'c',
        "AAA" : 'y',
        "AA" : 'b',
        "others" : 'r'
    }

    dates = {}
    values = {}
    for g in ("AAAA", "AAA", "AA", "others"):
        dates[g] = scores[1][g][0]
        values[g] = scores[1][g][1]

    fg, ax = plt.subplots()

    for v in ("others", "AA", "AAA", "AAAA"):
        ax.plot_date(dates[v], values[v], color=colors[v], markersize=1)
        print(v, len(values[v]))

    #plt.plot_date(dates, values, markersize=1)
    plt.yticks(np.arange(5, min(max(scores[0][1]), 38), 1.0))
    plt.ylim([8,min(max(scores[0][1]), 38)])
    plt.gcf().autofmt_xdate()
    plt.title(f"All PBs by {skillset} from {filename[:-4]}{' (Filtered)' if advancedFilter else ''}")
    fg.savefig(f"pbgraph_{filename[:-4]}.png", dpi=500)
    print("Done.")

else:
    scores = getScores(skillset, advancedFilter)

    fg, ax = plt.subplots()

    colors = {
        "AAAA" : 'c',
        "AAA" : 'y',
        "AA" : 'b',
        "A" : 'r',
        "B" : 'r',
        "C" : 'r',
        "D" : 'r',
        "F" : 'r'
    }

    biggestOverall = 0
    for g in ("F", "D", "C", "B", "A", "AA", "AAA", "AAAA"):
        k = g
        v = scores[g]
        dates = []
        values = []
        for x in v:
            dates.append(x.date)
            values.append(x.skillsets[skillset])
            if x.overall > biggestOverall:
                biggestOverall = x.overall
        ax.plot_date(dates, values, color = colors[k], markersize=1)

    print("Highest overall score:", biggestOverall)

    plt.yticks(np.arange(5, min(biggestOverall, 38), 1.0))
    plt.ylim([8,min(biggestOverall, 38)])
    plt.gcf().autofmt_xdate()
    plt.title(f"All Scores by {skillset} from {filename[:-4]}{' (Filtered)' if advancedFilter else ''}")
    fg.savefig(f"allscoresgraph_{filename[:-4]}.png", dpi=500)
    print("Done.")

print("Pick a minimum required accuracy level to filter scores")
print("Enter nothing to pick 0%")
amount = input()
print("Final Rating by skillset:")
try:
    float(amount)
except:
    amount = 0
setAllTopSSRs(amount)
for ss,val in calcRating().items():
    print(f"\t{ss}", f"{val:.2f}")

print("Do you want to calculate the rating per day?")
print("Input 'y' for yes")
check = input()
if check == "y":
    print("Calculating rating per day....")
    plt.clf()
    SSRS = calcRatingByDate()
    x = list(SSRS.keys())
    y = {ss : [] for ss in skillsetConstants}
    colors = { "Overall" : "b",
            "Stream" : "g",
            "Jumpstream" : "r",
            "Handstream" : "c",
            "Stamina" : "y",
            "JackSpeed": "k",
            "Chordjack" : "m",
            "Technical" : "#ff8800"
        }
    for date,ratings in SSRS.items():
        for ss in skillsetConstants:
            y[ss].append(ratings[ss])
    for ss in skillsetConstants:
        plt.plot(x, y[ss], color=colors[ss])
    plt.legend(skillsetConstants, loc="upper center", fancybox=True, ncol=4, bbox_to_anchor=(0.5,-0.3))

    biggestSSR = 0
    for ss in skillsetConstants:
        if y[ss][-1] > biggestSSR:
            biggestSSR = y[ss][-1]
    lowerLimit = (sum(y["Overall"][:len(y["Overall"])//3]) / len(y["Overall"])//3 + y["Overall"][-1]) / 2
    if noLimits:
        lowerLimit = 5

    plt.ylim([lowerLimit,min(38, int(biggestSSR) + 1)])
    plt.gcf().autofmt_xdate()
    g = plt.gcf()
    print("Enter a width value (default is 5.0)")
    w = input()
    try:
        float(w)
    except:
        w = 5
    print("Enter a height value (default is 5.0)")
    h = input()
    try:
        float(h)
    except:
        h = 5
    g.set_size_inches(w,h)
    plt.draw()
    plt.title(f"Skillsets over time from {filename[:-4]}")
    plt.tight_layout(pad=2)

    plt.savefig(f"plotovertime_{filename[:-4]}.png", dpi=500)

