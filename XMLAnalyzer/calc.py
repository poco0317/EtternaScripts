import math
import datetime
import traceback



skillset_consts = ["Overall", "Stream", "Jumpstream", "Handstream", "JackSpeed", "Chordjack", "Technical", "Stamina"]

def aggregateSSRs(skillset, rating, res, iter, topssrs):
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

def calcRating(ssrs):
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
    TopSSRs should be sorted by now so this will go smoothly.
    '''
    listOfRatingsByDate = {}
    for ss in skillset_consts:
        listOfRatingsByDate[ss] = {}

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

    for i in range(len(listOfDates)):
        if listOfDates[i] > earliestDate:
            listOfDates = listOfDates[i:]
            break
    
    SSRsByDates = {}
    for i in range(len(listOfDates)):
        print("On Date", i+1, "out of", len(listOfDates))
        skillz = []
        output = {}
        skillsets = skillset_consts[1:]
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

def setAllTopSSRs(charts, ssrnorm, requiredAcc = 0, no_limits = False):
    '''
    Note: This is for PBs only, and all invalid scores are ignored. This means no CC On. No Client Invalidated.
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
                    #traceback.print_exc() # usually complaints about the ssrs missing
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

def get_scores(charts, skillset, advanced_filter = False, ssrnorm = False, requiredAcc = 0, no_limits = False):
    '''
    Given the skillset, get the scores
    Can filter.
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
    if advanced_filter:
        print(f"Disregarded {skipped} scores due to advanced filtering by highest skillset.")

    print("Earliest Score:", SkillsetsWithDates[0])
    print("Latest Score:", SkillsetsWithDates[-1])
    return grades

def getPBs(charts, skillset, advanced_filter = False, ssrnorm = False, requiredAcc = 0, no_limits = False):
    '''
    Given the skillset, get the pbs
    returns a tuple of (dates, values) , {grade : (dates, values) }
    '''
    import matplotlib
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
                                    if thenum >= 0.9997:
                                        AAAAkeys.add(pbkey)
                                    elif thenum >= 0.9975:
                                        AAAkeys.add(pbkey)
                                    elif thenum >= 0.93:
                                        AAkeys.add(pbkey)
                        else:
                            for attribute in score.findall("SSRNormPercent"):
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
                    #traceback.print_exc()
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

    if advanced_filter:
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
        if advanced_filter:
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