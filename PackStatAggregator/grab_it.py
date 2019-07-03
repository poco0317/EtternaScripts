import re
import glob
import zipfile


files = glob.glob("*.zip")
dates_dict = {}

for f in files:
    try:
        with zipfile.ZipFile(f) as thisfile:
            g = thisfile.infolist()
            times = []
            for potential_match in g:
                #print(potential_match)
                try:
                    if re.search(r".+\.sm$", potential_match.filename) or re.search(r".+\.dwi$", potential_match.filename):
                        times.append(potential_match.date_time)
                except:
                    #filename was broken
                    pass
            last_time = times[0]
            for time in times:
                if time > last_time:
                    last_time = time
            #print(last_time)
            #print("\t "+thisfile.filename)
            dates_dict[thisfile.filename[:-4]] = last_time
    except:
        print("Zip isnt a zip apparently... "+f)
        dates_dict[f[:-4]] = (1980,1,1,0,0,0)

out = "packname,year,month,day,hour,min,sec\n"
for date in dates_dict:
    out = out + date + "," + ",".join([str(i) for i in dates_dict[date]]) + "\n"
final_file = open("output.csv", "w")
final_file.write(out)
final_file.close()

print("done")
#
#   CSV format:
#   pack_name,year,month,day,hour,min,sec
#   'd,yyyy,mm,dd,hh,mm,ss
#
#
#
#
#