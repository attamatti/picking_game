#!/usr/bin/python
import os
import sys
import time
import grep
global vers
global relionpath
relionpath = '/fbs/emsoftware2/LINUX/relion-1.4-beta-1/bin/'

vers = '0.2'

# --- function find relion ---
def find_relion():
    global relionpath
    if os.path.isfile('{0}relion_display'.format(relionpath)) == False:
        print "Can't find Relion! :("
        relionpath = raw_input("path to relion's bin directory: ")
        find_relion()
    else:
        return()

#--------- check the scores and make the leaderboard
def check_scores():  
    print "** **** ****** Particle Picking Leaderboard ****** **** **"
    print '      NAME                                    SCORE'
    scoresdata = open('email_scores.txt','r').readlines()
    
    scores = {}
    for i in scoresdata:
        splitdata = i.split(',')
        if len(splitdata) >= 1:
            if int(splitdata[-2])-int(splitdata[-1]) in scores:
                    scores[int(splitdata[-2])-int(splitdata[-1])].append(splitdata[0])
            else:
                  scores[int(splitdata[-2])-int(splitdata[-1])] = [splitdata[0]] 
    keys = scores.keys()
    keys.sort(reverse=True)
    n = 1
    curr = keys[0]
    if len(keys) < 10:
        listlength = len(keys)
    else:
        listlength = 10
    for i in keys[0:listlength]:
        if i < curr:
            n +=1
        m=0
        for j in scores[i]:
            print '{0:>2}) {1:<40} {2:>3}'.format(n,scores[i][m],i) 
            m+=1
        curr = i
    print "** **** *****                             ****** **** **"
    return()
#------------------

#------- the meat of the game ---------------
def thegame(file):
    # --- function calculate the distance bewteen two points ---
    def calc_points_dist(coords1,coords2):
        xdif = abs(float(coords1[0]) - float(coords2[0]))
        ydif = abs(float(coords1[1]) - float(coords2[1]))
        return xdif+ydif
    #-----------------------------------------------------------
    
    # ---- function: get coords from a star file
    def getcoords(file):
        coords = []
        data = open(file,'r').readlines()
        for line in data:
                if '_' not in line and line != '\n':
                    if len(line.split()) >1:
                        coords.append(line.split())
        return coords
    #-----------------------------------------------
    
    #----- function: run relion to do the picking:
    def do_picking(file):
        print """
    How to pick particles:
    
    * Left click on virus particles
    * Be sure not to select particles that are touching each other, the carbon support, or the edge of the micrograph
    * When finished right click and select 'save STAR with coordinates'
    """
        go = raw_input('Press enter to begin')
    
        print '... please wait for the micrograph to load\n'
        command = '{2}relion_display --pick  --i {0}  --coords {1}_manualpick.star --scale 0.3 --black 0 --white 0 --sigma_contrast 3 --particle_radius 125 --lowpass 10 --angpix 1 &'.format(file,file.split('.')[0],relionpath)
        os.system(command)
        time.sleep(10)
        go = raw_input('\nClick on this window and hit enter when finished')
    #---------------------------------------------
    
    
    #-- Function compare autopick and manual pick files generate starfiles for pretty visuals ---
    def diffstar(apf,mpf,fileroot):
        maxbetween = 200
        colorcode = open('{0}_colors.star'.format(fileroot),'w')
        autopick = getcoords(apf)
        manualpick = getcoords(mpf)
        # find the hits
        hits = {}
        manpi = 0
        for i in manualpick:
            id = i[0]+','+i[1]
            hits[id] = 0
            manpi +=1
            for j in autopick:
                dist = calc_points_dist(i,j)
                if dist <= 0.5*maxbetween:
                    hits[id]+=1
        # find the false positives (by working backwards, finding which autos also have manual hits):
        poshits = {}
        for i in autopick:
            id = i[0]+','+i[1]
            poshits[id] = 0
            for j in manualpick:
                dist = calc_points_dist(i,j)
                if dist <= 0.5*maxbetween:
                    poshits[id] +=1
        goodhits = 0
        misses  = 0
        falsepositives = 0
        doublehits = 0
        
        colorcode.write('''data_
    
    loop_ 
    _rlnCoordinateX #1 
    _rlnCoordinateY #2
    _rlnClassNumber #3
    ''')
        
        
        for i in hits:
            if hits[i] == 0:
                x = i.split(',')[0]
                y = i.split(',')[1]
                colorcode.write('{0}\t{1}\t2\n'.format(x,y))
                misses +=1
            if hits[i] == 1:
                x = i.split(',')[0]
                y = i.split(',')[1]
                colorcode.write('{0}\t{1}\t1\n'.format(x,y))
                goodhits +=1
            if hits[i] > 1:
                x = i.split(',')[0]
                y = i.split(',')[1]
                colorcode.write('{0}\t{1}\t2\n'.format(x,y))
                misses += 1
        for i in poshits:
            if poshits[i] == 0:
                x = i.split(',')[0]
                y = i.split(',')[1]
                colorcode.write('{0}\t{1}\t0\n'.format(x,y))
                falsepositives +=1
        return goodhits,manpi,misses,doublehits,falsepositives
    #-----------------------------------------------------
    
    
    #--- function prepare the image and show it-----------
    def prepare_image(file):
        filename = file.split('.')[0]
        name1 = '{0}_manualpick.star'.format(filename)
        name2 = '{0}_answers.star'.format(filename)
        goodhits,manpi,misses,doublehits,falsepositives = diffstar(name1,name2,filename)
        command = '{2}relion_display --pick  --i {0}  --coords {1}_colors.star --scale 0.2 --black 0 --white 0 --sigma_contrast 3 --particle_radius 150 --lowpass 10 --angpix 1 --color_label rlnClassNumber --blue 0 --red 2 &'.format(file,filename,relionpath)
        os.system(command)
        return goodhits,manpi,misses,doublehits,falsepositives
    #--------------------------------------------------------
    
    do_picking(file)
    goodhits,manpi,misses,doublehits,falsepositives = prepare_image(file)
    emailsfile = open('email_scores.txt','a')
    
    print ''
    print "**************************************************"
    print "You picked {0}/{1} good particles with {2} errors!".format(goodhits,manpi,falsepositives)
    print 'purple = hits'
    print 'red = misses'
    print 'blue = false positives'
    print '**************************************************'
    print 'Final Score: {0}                                  '.format(int(goodhits)-int(falsepositives))
    print '**************************************************'
    
    name = raw_input('Enter your name to record your score: ')
    if len(name) >= 1: 
        email = raw_input('Enter your Email address to enter the contest: ')
        emailsfile.write('{0},{1},{2},{3}\n'.format(name,email,goodhits,falsepositives))
    return()

#-------- run the game ----------------------
def run_game():
    global vers


    os.system('clear')
    check_scores()
    print '\n\nParticle picking demo | for astbury conversation | vers {0}'.format(vers)

    micrographs = grep('micrographs/*.mrc')
    micrographsdic = {"1":"micrographs/micrograph00007.mrc","2":"micrographs/micrograph00007.mrc"}
    n=3
    for i in micrographs:
        if i not in("micrographs/micrograph00007.mrc","micrographs/micrograph00002.mrc"):
            micrographskdic[n] = i
            n+=1
    keys = micrographsdic.keys()
    keys.sort
    print '''
    1) Beginner
    2) Advanced
    '''
    for i in keys:
        print'{0}/t{1}'.format(i,micrograpshdic[i])
    diff = raw_input('Choose difficulty level:')
    if diff == 's':
        sys.exit('\n**SHAUN MODE! -- you just won by cheating**\n')
    file = micrographsd[diff]
    thegame(file)
    #os.system('python picking-demo.py {0}'.format(file))
    os.system('rm micrographs/*_manualpick.star')
    reset = raw_input('\n Thanks for playing!')
    os.system('pkill relion')
    run_game()
# -----------------------------


find_relion()
run_game()
