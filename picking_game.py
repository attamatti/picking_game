#!/usr/bin/python
import os
import sys
import time
import glob
global vers
global relionpath
########### enter the path to relion here###################
relionpath = '/fbs/emsoftware2/LINUX/relion-1.4-beta-1/bin/'
############################################################


#--- no touchy touchy anything below here ---------------------

vers = '0.2 - BETA test'

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
    for i in keys:
        if i < curr:
            n +=1
        m=0
        for j in scores[i]:
            print '{0:>2}) {1:<40} {2:>3}'.format(n,scores[i][m],i) 
            m+=1
        curr = i
    print "** **** *****                             ****** **** **"
    print 'press <enter> to go back'
    return()
#------------------

#----- Get the micrographs ---------------
def get_micrographs():
    micsdata = {}
    micrographs = open('micrographs_info.star','r').readlines()
    for i in micrographs:
        if len(i.split()) > 3:
            micsdata[i.split()[0]] = i.split()[1:]
    return micsdata
#--------------------------------------------

#------- the meat of the game ---------------
def thegame(file,partdiameter,scale,apix):
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
    
    * Left click on the particles
    * Be sure not to select particles that are touching each other, the carbon support, or the edge of the micrograph
    * When finished right click and select 'save STAR with coordinates'
    """
        go = raw_input('Press <enter> to begin')
    
        print '... please wait for the micrograph to load\n'
        command = '{2}relion_display --pick  --i {0}  --coords {1}_manualpick.star --scale {4} --black 0 --white 0 --sigma_contrast 3 --particle_radius {3} --lowpass 10 --angpix {5} &'.format(file,file.split('.')[0],relionpath,0.75*partdiameter,scale,apix)
        os.system(command)
        time.sleep(10)
        go = raw_input('\nClick on this window and hit <enter> when finished')
    #---------------------------------------------
    
    
    #-- Function compare autopick and manual pick files generate starfiles for pretty visuals ---
    def diffstar(apf,mpf,fileroot):
        maxbetween = 0.3*partdiameter
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
        command = '{2}relion_display --pick  --i {0}  --coords {1}_colors.star --scale 0.2 --black 0 --white 0 --sigma_contrast 3 --particle_radius {3} --lowpass 10 --angpix 1 --color_label rlnClassNumber --blue 0 --red 2 &'.format(file,filename,relionpath,0.75*partdiameter)
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
def run_game(micsdata):
    global scale
    os.system('clear')
    print '\n** Particle picking trainer vers {0} **'.format(vers)
    print 'micrographs scale: {0}\n'.format(scale)
    n = 1
    backdic = {}
    for i in micsdata:
        print '{0}) {1}'.format(n,micsdata[i][0]) 
        backdic[str(n)] = i
        n+=1
    print '\ns) set scale\tc) check your answers\th) view high scores\tq) quit'
    diff = raw_input("Select the micrograph to pick: ")
    if diff == 'shaun':
        sys.exit('\n**SHAUN MODE! -- you just won by cheating**\n')
    if diff == 'q':
        sys.exit('Goodbye')
    if diff == 's':
        scale = raw_input('Set micrograph scale (0.3 recommended): ') or '0.3'
        run_game(micsdata)
    if diff == 'h':
        os.system('clear')
        check_scores()
        exit = raw_input(' ')
        run_game(micsdata)
    if diff == 'c':
        check_results()
    file = backdic[diff]
    apix = micsdata[file][1]
    partdiameter = micsdata[file][2]
    print '{0}_answers.star'.format(file.split('.')[0])
    if os.path.isfile('{0}_answers.star'.format(file.split('.')[0])) == False:
        sys.exit('The answer file for this micrograph is missing\nmake it with relion and save as micrographs/<filename>_answers.star')
    thegame(file,float(partdiameter),float(scale),float(apix))
    os.system('rm micrographs/*_manualpick.star')
    reset = raw_input('\n Thanks for playing!')
    os.system('pkill relion')
    run_game(micrographs)
# -----------------------------

#----- check the results on a micrograph ------
def check_results():
    os.system('clear')
    print '** check your picking on previous micrographs **'
    mics = glob.glob('micrographs/*.mrc')
    colorfiles = glob.glob('micrographs/*_colors.star')
    micsanswers = {}
    n = 1
    for i in mics:
        fileroot = i.split('/')[1]
        fileroot = fileroot.split('.')[0]
        if "micrographs/{0}_colors.star".format(fileroot) in colorfiles:
            micsanswers[n] = 'micrographs/{0}'.format(fileroot)
            print '{0}) {1}'.format(n,format(micrographs['{0}.mrc'.format(micsanswers[n])][0]))
            n+=1
    print '\nq) go back'
    selection = raw_input('pick a micrograph to display: ')
    if selection == 'q':
        os.system('pkill relion')
        run_game(micrographs)
    print '... please wait for the micrograph to load'
    selval = '{0}.mrc'.format(micsanswers[int(selection)])
    partdiameter = float(micrographs['{0}.mrc'.format(micsanswers[int(selection)])][2])
    command = '{2}relion_display --pick  --i {0}  --coords {1}_colors.star --scale 0.2 --black 0 --white 0 --sigma_contrast 3 --particle_radius {3} --lowpass 10 --angpix 1 --color_label rlnClassNumber --blue 0 --red 2 &'.format(selval,micsanswers[int(selection)],relionpath,0.75*partdiameter)
    time.sleep(15)
    os.system(command)
    check_results()
#-----------------------------------        
find_relion()
print '** Particle picking trainer vers {0} **'.format(vers)
scale = raw_input('Set the scale for the micrographs (0.3 recommended): ') or '0.3'
micrographs = get_micrographs()
run_game(micrographs)
