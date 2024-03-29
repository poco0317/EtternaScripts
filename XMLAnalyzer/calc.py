import os
import math
import time
import datetime
import traceback
from multiprocessing import Pool

skillset_consts = ["Overall", "Stream", "Jumpstream", "Handstream", "JackSpeed", "Chordjack", "Technical", "Stamina"]

def aggregateSSRs(skillset, rating, res, iter, topssrs):
    '''
    Calculate Skillset Rating for a selected Skillset given a list of Top SSR Values
    '''
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
    return aggregateSSRs(skillset, rating - res, res / 2, iter + 1, topssrs)

def aggregateSSRsByDate(dates, ssrs, skillset, rating, res, iter, dayIndex):
    '''
    Calculate Skillset Rating for a selected Skillset given a list of Top SSR Values
    However, this will only calculate for the dates in the given list.
    Those dates must correspond to existent SSR Values in the given SSR list
    '''
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
        return rating, skillset, dayIndex
    return aggregateSSRsByDate(dates, ssrs, skillset, rating - res, res / 2, iter + 1, dayIndex)

def calcRating(ssrs):
    '''
    Shortcut to grab a dict of all Skillset Ratings given a full list of SSRs
    '''
    skillz = {}
    output = {}
    for ss in skillset_consts[1:]:
        output[ss] = aggregateSSRs(ss, 0, 10.24, 1, ssrs) * 1.04
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

def calcRatingByDate(ssrs, no_limits = False):
    '''
    Given a list of SSRs to work with, calculate the Skillset Ratings for every day of those SSRs
    Return a dict mapping those dates to the Skillsets
    '''
    listOfRatingsByDate = {ss: {} for ss in skillset_consts}
    SSRsByDates = {}

    # gather a list of ratings by date and attach a readable datetime to them
    for skillset, grades in ssrs.items():
        for grade in grades:
            date = grade[1].replace(hour = 0, minute = 0, second = 0)
            if date not in listOfRatingsByDate[skillset]:
                listOfRatingsByDate[skillset][date] = [grade[0]]
            else:
                listOfRatingsByDate[skillset][date].append(grade[0])
    listOfDates = list(listOfRatingsByDate["Overall"].keys())
    earliestDate = datetime.datetime(year=2017, month=5, day=1)

    if no_limits:
        earliestDate = datetime.datetime(year=2001, month=1, day=1)

    # cut off any scores that happen to be in the list if they are too early
    for i in range(len(listOfDates)):
        if listOfDates[i] > earliestDate:
            listOfDates = listOfDates[i:]
            break
    
    pool = Pool()
    j1 = time.time()
    skillsets = skillset_consts[1:]
    total = len(listOfDates)
    each_day = {}

    def the_callback(x):
        '''
        Callback for process pool which fills out the info per day
        '''
        ss = x[1]
        result = x[0] * 1.04
        index = x[2]
        if index in each_day:
            each_day[index][ss] = result
            if len(each_day[index]) == 7:
                each_day[index]["Overall"] = sum(sorted([x for x in each_day[index].values()])[1:]) / 6
                SSRsByDates[listOfDates[index]] = each_day[index]
                print(f"\tFinished day {index+1} of {total}")
        else:
            each_day[index] = {ss: result}

    for i in range(total):
        for ss in skillsets:
            pool.apply_async(aggregateSSRsByDate, args=(listOfDates[:i], listOfRatingsByDate, ss, 0, 10.24, 1, i), callback=the_callback)
    
    print(f"Queued the process pool. There are {total} days to calculate. Up to {os.cpu_count()} processes may spawn.")
    pool.close() # stop the pool
    pool.join() # block until the pool finishes

    j2 = time.time()
    print(f"Full run took {j2-j1} seconds")
    return SSRsByDates

def setAllTopSSRs(charts, ssrnorm, requiredAcc = 0, no_limits = False):
    '''
    Get all valid PB SSRs for the profile. Must be CC Off.
    Returns a dict mapping skillsets to big lists of SSR values
    Each list of SSR values is sorted
    '''
    failed = 0
    topssrs = {}
    for chart in charts:
        for scores_at_rate in list(chart):
            pbkey = scores_at_rate.get("PBKey")
            for score in [x for x in list(scores_at_rate) if x.get("Key") == pbkey]:
                try:
                    if not isValid(score, no_limits):
                        continue
                    if not fitsAcc(score, float(requiredAcc), ssrnorm):
                        continue
                    datime = datetime.datetime.strptime([" ".join(x.itertext()) for x in score.findall("DateTime")][0], "%Y-%m-%d %H:%M:%S")
                    for attribute in score.findall("SkillsetSSRs")[0]:
                        if attribute.tag in topssrs:
                            topssrs[attribute.tag].append((float(" ".join(attribute.itertext())), datime))
                        else:
                            topssrs[attribute.tag] = [(float(" ".join(attribute.itertext())), datime)]
                except:
                    failed += 1
                    #traceback.print_exc() # usually complains about the ssr section missing
    for k,v in topssrs.items():
        topssrs[k] = sorted(v, key = lambda x: x[1])
    return topssrs
    #print("Failed score count", failed)

def isValid(score, no_limits = False):
    if no_limits:
        return True
    for x in score.findall("EtternaValid"):
        if " ".join(x.itertext()) == "0":
            return False
    for x in score.findall("NoChordCohesion"):
        if " ".join(x.itertext()) == "0":
            return False
    return True

def fitsAcc(score, requiredAcc, ssrnorm):
    try:
        if ssrnorm:
            for x in score.findall("SSRNormPercent"):
                if float(" ".join(x.itertext())) * 100 >= requiredAcc:
                    return True
        else:
            for x in score.findall("WifeScore"):
                if float(" ".join(x.itertext())) * 100 >= requiredAcc:
                    return True
        return False
    except:
        return False

class InfoHolder:
    def __init__(self, date, skillsetdict, percent, name="", grade=""):
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
        self.name = name
        self.grade = grade
    def __repr__(self):
        return str(self.date) + f" {self.percent * 100:.4f}% worth " + str(self.overall)
    def __str__(self):
        return str(self.date) + f" {self.percent * 100:.4f}% worth " + str(self.overall)

def get_scores(charts, skillset, advanced_filter = False, ssrnorm = False, requiredAcc = 0, no_limits = False):
    '''
    Get the full list of scores according to the given Skillset and set of charts
    '''
    failed = 0
    skipped = 0
    SkillsetsWithDates = []
    for chart in charts:
        for scoresAtRate in list(chart):
            for score in scoresAtRate:
                try:
                    if not fitsAcc(score, requiredAcc, ssrnorm):
                        continue
                    datime = datetime.datetime.strptime([" ".join(x.itertext()) for x in score.findall("DateTime")][0], "%Y-%m-%d %H:%M:%S")
                    inputinfo = {}
                    for attribute in score.findall("SkillsetSSRs")[0]:
                        tag = attribute.tag
                        value = float(" ".join(attribute.itertext()))
                        inputinfo[tag] = value
                    grade = ""
                    try:
                        grade = ["".join(x.itertext()) for x in score.findall("Grade")][0]
                    except:
                        pass

                    biggestSS = skillset
                    if advanced_filter:
                        biggestSSVal = 0
                        for ss,v in inputinfo.items():
                            if ss != "Overall" and v > biggestSSVal:
                                biggestSS = ss
                                biggestSSVal = v
                    if biggestSS == skillset:
                        if not ssrnorm:
                            percent = float([" ".join(x.itertext()) for x in score.findall("WifeScore")][0])
                        else:
                            percent = float([" ".join(x.itertext()) for x in score.findall("SSRNormPercent")][0])
                        SkillsetsWithDates.append(InfoHolder( datime, inputinfo, percent, chart.get("Song"), grade))
                    else:
                        skipped += 1
                except:
                    #traceback.print_exc()
                    failed += 1                    

    SkillsetsWithDates.sort(key = lambda x: x.date)

    gradeNames = ("AAAAA", "AAAA", "AAA", "AA", "A", "B", "C", "D", "F")
    def percentToName(num):
        if num >= .99996:
            return "AAAAA"
        elif num >= .99955:
            return "AAAA"
        elif num >= .997:
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
    if advanced_filter:
        print(f"Disregarded {skipped} scores due to advanced filtering by highest skillset.")

    print("Earliest Score:", SkillsetsWithDates[0])
    print("Latest Score:", SkillsetsWithDates[-1])
    #print(len(SkillsetsWithDates))
    return grades

def getPBs(charts, skillset, advanced_filter = False, ssrnorm = False, requiredAcc = 0, no_limits = False):
    '''
    Given the skillset, get the pbs
    returns a tuple of (dates, values) , {grade : (dates, values) }
    '''
    import matplotlib
    pbmap = {}

    failed = 0
    AAAAAkeys = set()
    AAAAkeys = set()
    AAAkeys = set()
    AAkeys = set()
    for chart in charts:
        stuff = list(chart)
        for scres_at_rate in list(stuff):
            pbkey = scres_at_rate.get("PBKey")
            for score in [x for x in list(scres_at_rate) if x.get("Key") == pbkey]:
                try:
                    if not fitsAcc(score, requiredAcc, ssrnorm):
                        continue
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
                        if not ssrnorm:
                            for attribute in score.findall("WifeScore"):
                                if pbkey in pbmap:
                                    thenum = float(" ".join(attribute.itertext()))
                                    if thenum >= 0.99996:
                                        AAAAAkeys.add(pbkey)
                                    elif thenum >= 0.99955:
                                        AAAAkeys.add(pbkey)
                                    elif thenum >= 0.997:
                                        AAAkeys.add(pbkey)
                                    elif thenum >= 0.93:
                                        AAkeys.add(pbkey)
                        else:
                            for attribute in score.findall("SSRNormPercent"):
                                if pbkey in pbmap:
                                    thenum = float(" ".join(attribute.itertext()))
                                    if thenum >= 0.99996:
                                        AAAAAkeys.add(pbkey)
                                    elif thenum >= 0.99955:
                                        AAAAkeys.add(pbkey)
                                    elif thenum >= 0.997:
                                        AAAkeys.add(pbkey)
                                    elif thenum >= 0.93:
                                        AAkeys.add(pbkey)
                except:
                    failed += 1
                    #traceback.print_exc()
    overallWithDates = [data for (pb,data) in pbmap.items()]
    yeetus = sorted(overallWithDates, key = lambda kv: datetime.datetime.strptime(kv["DateTime"], "%Y-%m-%d %H:%M:%S"))
    #print("all charts", len(charts))
    #print("missing", failed)
    #print("found", len(yeetus))

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

    if advanced_filter:
        skipped = 0
        for score in yeetus.copy():
            if skippable(score):
                yeetus.remove(score)
                skipped += 1
        print(f"Skipped {skipped} scores due to advanced skillset filtering.")

    dates = matplotlib.dates.date2num([datetime.datetime.strptime(x["DateTime"], "%Y-%m-%d %H:%M:%S") for x in yeetus])
    values = [float(x[skillset]) for x in yeetus]
    #print(len(values))

    # these are all lists of overallWithDates dictionaries
    AAAAAs = []
    AAAAs = []
    AAAs = []
    AAs = []
    others = []

    for pbk, data in pbmap.items():
        if advanced_filter:
            if skippable(data):
                continue

        if pbk in AAAAAkeys:
            AAAAAs.append(data)
        elif pbk in AAAAkeys:
            AAAAs.append(data)
        elif pbk in AAAkeys:
            AAAs.append(data)
        elif pbk in AAkeys:
            AAs.append(data)
        else:
            others.append(data)

    sortedGradesByDate = {
        "AAAAA" : sorted(AAAAAs, key = lambda kv: datetime.datetime.strptime(kv["DateTime"], "%Y-%m-%d %H:%M:%S")),
        "AAAA" : sorted(AAAAs, key = lambda kv: datetime.datetime.strptime(kv["DateTime"], "%Y-%m-%d %H:%M:%S")),
        "AAA" : sorted(AAAs, key = lambda kv: datetime.datetime.strptime(kv["DateTime"], "%Y-%m-%d %H:%M:%S")),
        "AA" : sorted(AAs, key = lambda kv: datetime.datetime.strptime(kv["DateTime"], "%Y-%m-%d %H:%M:%S")),
        "others" : sorted(others, key = lambda kv: datetime.datetime.strptime(kv["DateTime"], "%Y-%m-%d %H:%M:%S"))
    }

    output = {}
    for g in ("AAAAA", "AAAA", "AAA", "AA", "others"):
        output[g] = (matplotlib.dates.date2num([datetime.datetime.strptime(x["DateTime"], "%Y-%m-%d %H:%M:%S") for x in sortedGradesByDate[g]]), [float(x[skillset]) for x in sortedGradesByDate[g]])

    return (dates, values),output