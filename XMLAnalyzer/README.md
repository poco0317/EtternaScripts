# XMLAnalyzer
Parse a given Etterna.xml file and return various bits of information in graph form.

## Execution
You need Python 3. Preferably 3.6+.

According to requirements.txt, you will need matplotlib and numpy. Numpy is also a requirement of matplotlib.

To ensure you have a good version of Python: `python --version` or `python3 --version` should indicate a Python version newer than 3.0.0.

To ensure you can install the required modules, check that `pip --version` or `pip3 --version` points to your Python install and is up to date.

Copy this repository folder to any directory you want. You must have `esketit.py` and `calc.py` within the same folder. The `requirements.txt` file is for the ultra-lazy Python users.

To install the required modules, either run `pip install -U matplotlib numpy` or `cd` to the directory with `requirements.txt` and run `pip install -r requirements.txt`. If you happen to be running on a system with multiple installs of Python, you may need to use `pip3` instead. The `-U` flag tells pip to upgrade the library if an old version is installed. The `-r` flag tells pip to use a requirements.txt file.

If for any reason your terminal complains that `pip` does not exist as a command yet you have Python installed with pip, you can also try `python -m pip install -U matplotlib numpy` or other variations similar to the above examples.

Once you have the modules, run `python esketit.py` or `python3 esketit.py`. The instructions in the terminal should be clear enough from this point. Simply indicate a specific filename for the Etterna.xml if it is in the same folder as the script, or give a complete path if it is located remotely. If it fails for any reason at this point or you enter no name, it attempts to find Etterna.xml in the same folder. If it still fails, you're out of luck and probably ran it incorrectly. Spaces in the path name should not make a difference.

Each process listed within should take a reasonable amount of time to run. They are near instant except for the Skillset Over Time Graph. This requires heavy calculation on all of your scores once for every single day's worth of scores. When run, it attempts to use 1 process for each CPU core to speed up the calculations. For an expected amount of time, I can say that this took about 45 seconds when parsing 500 days worth of 18000 scores on a R7 1700. Without the multiple processes, it can take much longer up to several minutes in the absolute extreme cases.


## Notes
If your XML contains very few scores, these graphs will not look interesting.

If the scores in your XML do not span more than a year, the axis formatting may break.


## Examples
These images were generated using default settings.

<img src="https://user-images.githubusercontent.com/2531164/60688638-10699900-9e7c-11e9-8687-00015fc0a9bd.png" width="720">
<img src="https://user-images.githubusercontent.com/2531164/60688647-1eb7b500-9e7c-11e9-87a8-79a364448300.png" width="720">
<img src="https://user-images.githubusercontent.com/2531164/60688651-211a0f00-9e7c-11e9-856d-63bed945282b.png" width="720">

