# picking_game
The game requires a working copy of relion any version 1.4+ should work.  It will look for the hardcoded path in line 8, change this to the correct path, if it doesn't find relion there it will ask for the location every time.
- after starting the game select the micrograph to work on
- pick the particles on the micrograph that appears, right click and save the star file
- hit enter on the window running this program to display the score and display the diagnostic
- enter you name and to get all the glory on the leader board

To add your own micrographs:
- put the micrograph in the micrographs folder
- use relion to pick particles to make the answer, save the star as `micrographs/<filename>_answers.star`
- edit the file 'micrographs_info.star' input the micrograph path, a nickname for it, the micrograph's sampling (in A/px), and the particle diameter (in Angstroms), in the appropriate columns

Scoring:
The program compares the results of the picking with the answer starfile.
- Any particle that doesn't have a picked particle within 1/3 of a particle diameter counts as a miss
- If a particle has two or more picks within 1/3 of a particle diameter all of the picks are considered false positives
- Any pick not with 1/3 of a particle diameter of a correct pick is considered a false positive
Score  = Correct picks - false positives - misses

leaderboard.py can be opened in a separate terminal window to display an independent leaderboard - useful for public engagement events and the like.  Hit enter to update it.

option c ('check you answers') displays the diagnostic screen for the last time a specific file was picked, very useful if the program has crashed before someone gost to see their score.

If you are Shaun Rawson and prefer to win by cheating type 'shaun'.
