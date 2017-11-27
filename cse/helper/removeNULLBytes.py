import os
from os import remove
from shutil import move

"""
Helper file for removing lines with NULL-byte in data file
"""

def removeNULLBytes(filepath):
    count = 0
    with open(filepath, 'r', newline='', encoding="utf-8") as readFile:
        with open(filepath + ".tmp", 'w', newline='', encoding="utf-8") as writeFile:
            for line in readFile:
                if '\0' not in line:
                    writeFile.write(line)
                else:
                    count += 1

    print("found", count, "lines containing NULL bytes")
    remove(filepath)
    move(filepath + ".tmp", filepath)
    print("removed NULL bytes")



if __name__ == '__main__':
    removeNULLBytes(os.path.join("data", "comments.data"))
