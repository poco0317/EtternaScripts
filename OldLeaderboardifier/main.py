import codecs
import xml.etree.ElementTree

##
####
#######
##########
#######

print("Enter the path of the XML to read from. ./Etterna.xml is the default")
filename = input()

print("Enter the name of the player")
playername = input()

e = None
try:
    e = xml.etree.ElementTree.parse(filename).getroot()
except:
    try:
        with codecs.open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            contents = f.read()
        e = xml.etree.ElementTree.fromstring(contents, xml.etree.ElementTree.XMLParser(encoding='utf-8'))
    except:
        print("You didn't to enter a valid xml path. I'll try ./Etterna.xml")
        filename = "Etterna.xml"
        try:
            with codecs.open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                contents = f.read()
            e = xml.etree.ElementTree.fromstring(contents, xml.etree.ElementTree.XMLParser(encoding='utf-8'))
        except:
            print("It still failed.")
            exit()


def findSection(xml, sectionName):
    ''' Find a section of the XML by name. Return None if no section exists.'''
    for x in xml:
        if x.tag == sectionName:
            return x
    return None

all_scores = {} # by chartkey
e_score_section = findSection(e, "PlayerScores")

all_score_keys = set() # by scorekey
if e_score_section is not None:
    print("Score count", len(e_score_section))
    for chart in list(e_score_section):
        key = chart.attrib["Key"]
        if key not in all_scores:
            all_scores[key] = {}
            for scoresat in list(chart):
                all_scores[key][scoresat.attrib["Rate"]] = [scoresat, chart.attrib["Pack"], chart.attrib["Song"], chart.attrib["Steps"]]
                for score in list(scoresat):
                    all_score_keys.add(score.attrib["Key"])
        else:
            for scoresat in list(chart):
                rate = scoresat.attrib["Rate"]
                if rate in all_scores[key]:
                    for score in list(scoresat):
                        if score.attrib["Key"] in all_score_keys:
                            continue
                        all_score_keys.add(score.attrib["Key"])
                        ggg = xml.etree.ElementTree.SubElement(all_scores[key][rate][0], "Score", attrib={"Key": score.attrib["Key"]})
                        ggg.extend(score)
                else:
                    all_scores[key][scoresat.attrib["Rate"]] = [scoresat, chart.attrib["Pack"], chart.attrib["Song"], chart.attrib["Steps"]]
                    for score in list(scoresat):
                        all_score_keys.add(score.attrib["Key"])  

print("Give an output filename or press enter to default. The output will be in csv format to import to a spreadsheet.")
out = input()
if out == "" or out[-4:] != ".csv":
    out = "Etterna.csv"

def safeget(element, name):
    g = element.find(name)
    if g is not None:
        return g.text
    return ""

def safegetn(element, name):
    g = element.find(name)
    if g is not None:
        return float(g.text)
    return 0

def dumbgrade(grade):
    g = {
        "Tier01":"AAAAA",
        "Tier02":"AAAA",
        "Tier03":"AAAA",
        "Tier04":"AAAA",
        "Tier05":"AAA",
        "Tier06":"AAA",
        "Tier07":"AAA",
        "Tier08":"AA",
        "Tier09":"AA",
        "Tier10":"AA",
        "Tier11":"A",
        "Tier12":"A",
        "Tier13":"A",
        "Tier14":"B",
        "Tier15":"C",
        "Tier16":"D",
        "Failed":"F",
    }
    if g[grade] is not None:
        return g[grade]
    return ""

with codecs.open(out, "w", encoding='utf-8', errors='ignore') as f:
    f.write("Player,Score Key,Song Name,Rate,Wife,Grade,Marvelous,Perfect,Great,Good,Bad,Miss,Difficulty,Calc Version,Pack,Wife Version,Overall,Stream,Jumpstream,Handstream,Stamina,Jackspeed,Chordjack,Technical,Date,CC Off,Judge Scale\n")
    for chartkey, chart in all_scores.items():
        obj = [x for x in chart.values()][0]
        pack = obj[1].replace(",", " ")
        songname = obj[2].replace(","," ")
        diffname = obj[3]
        scoresat = obj[0]
        rate = scoresat.attrib["Rate"]
        for score in scoresat:
            wife = safegetn(score,"SSRNormPercent") * 100
            grade = dumbgrade(safeget(score,"Grade"))
            marv = safeget(score,"TapNoteScores/W1")
            perf = safeget(score,"TapNoteScores/W2")
            great = safeget(score,"TapNoteScores/W3")
            good = safeget(score,"TapNoteScores/W4")
            bad = safeget(score,"TapNoteScores/W5")
            miss = safeget(score,"TapNoteScores/Miss")
            calcversion = safeget(score,"SSRCalcVersion")
            wifeversion = safeget(score,"wv")
            overall = safeget(score,"SkillsetSSRs/Overall")
            stream = safeget(score,"SkillsetSSRs/Stream")
            js = safeget(score,"SkillsetSSRs/Jumpstream")
            hs = safeget(score,"SkillsetSSRs/Handstream")
            stam = safeget(score,"SkillsetSSRs/Stamina")
            jack = safeget(score,"SkillsetSSRs/JackSpeed")
            cj = safeget(score,"SkillsetSSRs/Chordjack")
            tech = safeget(score,"SkillsetSSRs/Technical")
            date = safeget(score,"DateTime")
            ccoff = safeget(score,"NoChordCohesion")
            judge = safeget(score,"JudgeScale")
            f.write(f"{playername},{chartkey},{songname},{rate},{wife},{grade},{marv},{perf},{great},{good},{bad},{miss},{diffname},{calcversion},{pack},{wifeversion},{overall},{stream},{js},{hs},{stam},{jack},{cj},{tech},{date},{ccoff},{judge}\n")

print("Done")