import shutil
import os

path = '/home/test2/Reporting_FR'
for directories, subfolder, files in os.walk(path):
    if os.path.isdir(directories):
        if directories[::-1][:11][::-1] == '__pycache__':
                        shutil.rmtree(directories)
#__pycache__
#.pyc
#dump

