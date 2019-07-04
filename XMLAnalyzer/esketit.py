import math
import codecs
import datetime
import traceback
import xml.etree.ElementTree as ET
from calc import *

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
matplotlib.use("agg")

def yes_or_no(question):
    print(question)
    out = input()
    if out == "y":
        return True
    else:
        return False

def get_number(default = 0):
    out = input()
    try:
        return float(out)
    except:
        return default

def get_no_limits():
    return yes_or_no("Turn off limits? Invalid scores will show up and the graph will not be limited by anything.\nEnter 'y' to confirm.")

def get_ssrnorm():
    return yes_or_no("Do you want to use the SSRNorm Percent for filtering? In other words, convert all scores to Wife J4. Enter 'y' for yes.")

def get_xml(filename):
    e = None
    try:
        e = ET.parse(filename).getroot()
    except:
        try:
            with codecs.open(filename, "r", encoding='utf-8', errors='ignore') as f:
                contents = f.read()
            e = ET.fromstring(contents, ET.XMLParser(encoding='utf-8'))
        except:
            if filename != "Etterna.xml":
                print("You failed to enter a valid choice. I'll try Etterna.xml")
                return get_xml("Etterna.xml")
            else:
                print("It still failed.")
                exit()
    return e

def get_section(xml, section_name):
    for section in xml:
        if section.tag == section_name:
            return section
    return None

def get_displayname(xml):
    section = get_section(xml, "GeneralData")
    if section is None:
        print("fdsa")
        return "NoName"
    try:
        for attribute in section.findall("DisplayName"):
            return "".join(attribute.itertext())
        return "NoName"
    except:
        print(1)
        return "NoName"

def set_w_h_values(fig):
    print("Enter a width value (default is 6.4)")
    w = get_number(default=6.4)
    print("Enter a height value (default is 4.8)")
    h = get_number(default=4.8)
    fig.set_size_inches(w,h)

def run_rating_calc(xml):
    charts = get_section(xml, "PlayerScores")
    if charts is None:
        print("XML did not have scores.")
        return 1
    
    print("Pick a minimum required accuracy to filter scores")
    print("Enter nothing to pick 0%")
    threshold = get_number()

    ssrnorm = False
    if threshold > 0:
        ssrnorm = get_ssrnorm()

    print("Final rating by skillset:")
    ssrs = setAllTopSSRs(charts, ssrnorm, requiredAcc=threshold)

    for ss, val in calcRating(ssrs).items():
        print(f"\t{ss}", f"{val:.2f}")
    print("Done\n")
    return 0

def run_skillset_graph(xml):
    charts = get_section(xml, "PlayerScores")
    if charts is None:
        print("XML did not have scores.")
        return 1

    plt.clf()
    print("Pick a minimum required accuracy to filter scores")
    print("Enter nothing to pick 0%")
    threshold = get_number()

    no_limits = get_no_limits()

    ssrnorm = get_ssrnorm()

    topssrs = setAllTopSSRs(charts, ssrnorm, requiredAcc=threshold, no_limits=no_limits)
    ssrs = calcRatingByDate(topssrs, no_limits)

    x = list(ssrs.keys())
    y = {ss: [] for ss in skillset_consts}
    colors = { "Overall" : "b",
            "Stream" : "g",
            "Jumpstream" : "r",
            "Handstream" : "c",
            "Stamina" : "y",
            "JackSpeed": "k",
            "Chordjack" : "m",
            "Technical" : "#ff8800"
        }
    for date, ratings in ssrs.items():
        for ss in skillset_consts:
            y[ss].append(ratings[ss])
    for ss in skillset_consts:
        plt.plot(x, y[ss], color=colors[ss])
    plt.legend(skillset_consts, loc="upper center", fancybox=True, ncol=4, bbox_to_anchor=(0.5,-0.3))

    biggestSSR = 0
    for ss in skillset_consts:
        if y[ss][-1] > biggestSSR:
            biggestSSR = y[ss][-1]
    # basically a number meant to be closer to the upper 2 thirds of ratings per day
    # so that the graph appears zoomed in in most situations
    lowerLimit = (sum(y["Overall"][:len(y["Overall"])//3]) / len(y["Overall"])//3 + y["Overall"][-1]) / 2
    if no_limits:
        lowerLimit = 5

    plt.ylim([lowerLimit, min(38, int(biggestSSR) + 1)]) # restrict the upper limit to 38 because nobody goes that high
    plt.gcf().autofmt_xdate()
    set_w_h_values(plt.gcf())
    
    plt.draw()
    name = get_displayname(xml)
    plt.title(f"Skillsets over time from {name}")
    plt.tight_layout(pad=2)
    plt.savefig(f"overtime_{name}.png", dpi=500)
    print("Done\n")

    return 0

def run_all_plot(xml):
    charts = get_section(xml, "PlayerScores")
    if charts is None:
        print("XML did not have scores.")
        return 1

    print("Skillset to measure?")
    print("Valid input is: Overall, Stream, Jumpstream, Handstream, JackSpeed, Chordjack, Technical, Stamina")
    skillset = input()
    if skillset not in skillset_consts:
        skillset = "Overall"
        print("Your skillset was not valid. Picked Overall.")

    advanced_filter = False
    if skillset != "Overall":
        advanced_filter = yes_or_no(f"Do you want advanced filtering? This removes all scores that don't have {skillset} as the highest skillset.\nEnter 'y' for yes.")

    print("Pick a minimum required accuracy to filter scores")
    print("Enter nothing to pick 0%")
    threshold = get_number()

    no_limits = get_no_limits()

    ssrnorm = get_ssrnorm()

    scores = get_scores(charts, skillset, advanced_filter, ssrnorm, requiredAcc=threshold, no_limits=no_limits)

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

    if not no_limits:
        plt.yticks(np.arange(5, min(biggestOverall, 38), 1.0))
        plt.ylim([8,min(biggestOverall, 38)])
    else:
        plt.yticks(np.arange(5, biggestOverall, 1.0))
        plt.ylim([5, biggestOverall])
    plt.gcf().autofmt_xdate()
    set_w_h_values(plt.gcf())
    name = get_displayname(xml)
    plt.title(f"All Scores by {skillset} from {name}{' (Filtered)' if advanced_filter else ''}")
    fg.savefig(f"allscoresgraph_{name}.png", dpi=500)
    print("Done\n")

def run_pb_plot(xml):
    charts = get_section(xml, "PlayerScores")
    if charts is None:
        print("XML did not have scores.")
        return 1

    print("Skillset to measure?")
    print("Valid input is: Overall, Stream, Jumpstream, Handstream, JackSpeed, Chordjack, Technical, Stamina")
    skillset = input()
    if skillset not in skillset_consts:
        skillset = "Overall"
        print("Your skillset was not valid. Picked Overall.")

    advanced_filter = False
    if skillset != "Overall":
        advanced_filter = yes_or_no(f"Do you want advanced filtering? This removes all scores that don't have {skillset} as the highest skillset.\nEnter 'y' for yes.")

    print("Pick a minimum required accuracy to filter scores")
    print("Enter nothing to pick 0%")
    threshold = get_number()

    no_limits = get_no_limits()

    ssrnorm = get_ssrnorm()

    scores = getPBs(charts, skillset, advanced_filter, ssrnorm, requiredAcc=threshold, no_limits=no_limits)
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

    plt.yticks(np.arange(5, min(max(scores[0][1]), 38), 1.0))
    if not no_limits:
        plt.ylim([8,min(max(scores[0][1]), 38)])
    else:
        plt.ylim([5,max(scores[0][1])])
    plt.gcf().autofmt_xdate()
    set_w_h_values(plt.gcf())
    name = get_displayname(xml)
    plt.title(f"All PBs by {skillset} from {name}{' (Filtered)' if advanced_filter else ''}")
    fg.savefig(f"pbgraph_{name}.png", dpi=500)
    print("Done\n")


def main():
    ''' contains basic main program execution '''
    print("This is an Etterna.xml analyzer. It will parse your scores and do whatever you want I guess")

    print("Enter the filename.")
    filename = input()
    xml = get_xml(filename)

    while True:
        print("Enter a number to pick an option. Enter 'e' to quit.")

        print("1: Calculate Skillsets")
        print("2: Generate Skillset Over Time Graph")
        print("3: Generate PB Dot Plot")
        print("4: Generate All Score Dot Plot")

        decision = input()
        try:
            if decision == "1":
                run_rating_calc(xml)
            elif decision == "2":
                run_skillset_graph(xml)
            elif decision == "3":
                run_pb_plot(xml)
            elif decision == "4":
                run_all_plot(xml)
            elif decision == "e":
                return 69
        except:
            traceback.print_exc()

if __name__ == "__main__":
    main()