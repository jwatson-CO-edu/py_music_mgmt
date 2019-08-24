# temp_player.py
# A music player for when both your Windows machine and your youtube are tied up

# https://linuxconfig.org/how-to-play-audio-with-vlc-in-python
import vlc , getpass , os , sys , time
from random import choice

SOURCEDIR = os.path.dirname( os.path.abspath( '__file__' ) ) # URL, dir containing source file: http://stackoverflow.com/a/7783326
PARENTDIR = os.path.dirname( SOURCEDIR )
# ~~ Path Utilities ~~
def prepend_dir_to_path( pathName ): sys.path.insert( 0 , pathName ) # Might need this to fetch a lib in a parent directory
prepend_dir_to_path( SOURCEDIR )
from marchhare.marchhare import get_EXT
print "Loaded Libs!"

MUSICDIR = os.path.join( "/media/" , getpass.getuser() , "MUSIC/Music" ) 
print "The music directory is" , MUSICDIR , "but is it valid?" , os.path.isdir( MUSICDIR )

tracklist = []

# https://www.pythoncentral.io/how-to-traverse-a-directory-tree-in-python-guide-to-os-walk/
for dirName , subdirList , fileList in os.walk( MUSICDIR ):
    for fName in fileList:
        if get_EXT( fName ) == "MP3":
            tracklist.append( os.path.join( dirName , fName ) )
            
print "Found" , len( tracklist ) , "playable files! For example" , choice( tracklist )

N_tracks = 20

for i in range( N_tracks ):
    track = choice( tracklist )
    print i+1 , "of" , N_tracks , ", Now playing" , track , 
    player = vlc.MediaPlayer( track )
    print ", Duration:" , player.get_length() / 1000.0 , 
    player.play()
    time.sleep( 0.5 )
    Ended = 6
    current_state = player.get_state()
    while current_state != Ended:
        print '.',
        sys.stdout.flush()
        time.sleep( 1.0 )
        current_state = player.get_state() 
    print
    
print "End!"