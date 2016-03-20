# mp3Scraper.py
# James Watson, 2013 October
# Find ALL THE MP3s and copy them all to one spot

import os, shutil, time


def find_drives():
    env = os.name
    L = []
    if(env == 'nt'): # if windows
        for i in range(ord('a'), ord('z')+1):
            drive = chr(i)
            if(os.path.exists(drive +":\\")):
                L.append(drive + ":/")

        return L
    elif(environnement == 'UNIX'): # FIXME: write code for UNIX
        return L

allDrives = find_drives()
print allDrives # printed ['c:/', 'd:/', 'e:/', 'h:/', 'i:/']
musicPathString = "D:/AllMusic"
foundMusicPath = os.path.exists(musicPathString) # true
print foundMusicPath
if foundMusicPath:
    musicPath = os.path.abspath(musicPathString)
desiredTypes = ['.mp3','.mp4', '.aac','.wav','.flac','.ogg']
processed = 0
processTime = time.clock()

def gather_all_songs(arg, dirname, names):
    global musicPath, desiredTypes, processed, processTime
    if dirname != musicPath:
        for i in names:
            if os.path.splitext(i)[1] in desiredTypes:
                try:
                    shutil.move(os.path.join(dirname, i),os.path.join(musicPath, i))
                    break
                except IOError:
                    print "Unable to copy " + str(os.path.join(dirname, i))
            processed += 1
            if processed % 5000 == 0:
                print "Processed " + str(processed) + " files. Last 5k in " + str(time.clock() - processTime)
                processTime = time.clock()

if foundMusicPath:
    for drive in allDrives:
        os.path.walk(drive, gather_all_songs, False)
        print "DRIVE " + str(drive) + " COMPLETE!"
else:
    print "Path '" + str(musicPathString) + "' not found!"

##testPath = os.path.abspath("D:/testdir")
##totalTXTCount = 0
##def count_txt(arg, dirname, names):
##    global totalTXTCount, musicPath
##    for i in names:
##        print dirname == musicPath
##        print os.path.join(dirname, i)
##        if os.path.splitext(i)[1] == '.txt':
##            #shutil.copy2(os.path.join(dirname, i),os.path.join(testPath, i))
##            shutil.move(os.path.join(dirname, i),os.path.join(testPath, i))
##            totalTXTCount += 1
##    
##os.path.walk(musicPath, count_txt, False)
##print totalTXTCount
##print os.walk('c:/').next()[1]


