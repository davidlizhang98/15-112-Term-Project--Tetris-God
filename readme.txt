
Hi all! The following project is David Zhang's term project, a modified version of Tetris. 


To run the project, simply open the pygame tetris.py file and run it. 
Note that the project was created using pygame so pygame must be an imported module for the file to work properly. 
My term project takes pieces from the basic pygame framework provided by Lukas Peraza and builds upon the basic Tetris game that I created (which I modified from tkinter to pygame) in Week 6 of 15-112.

To import pygame (the way I did it):
	go to: https://repo.continuum.io/archive/index.html
	look for Anaconda3-2.3.0-Windowsx86.exe
	Install it for all users
	
	then, go to: http://www.lfd.uci.edu/~gohlke/pythonlibs/#gensim
	search for: pygame-1.9.2b1-cp34-cp34m-win32.whl
	download and copy this file to C->Anaconda3->Scripts
	go to command prompt and type: cd C:\Anaconda3\Scripts
	type: pip install pygame-1.9.2b1-cp34m-win32.whl


Major features of my term project include:
	a thoroughly optimized Tetris Artificial Intelligence developed using a Genetic Algorithm (capable of clearing more than 40,000 rows/lines)
	Tetris AIs of varying speeds and "intelligence" (a.k.a. can adjust difficulty of the AI)
	the capability to play Tetris solo, spectate an AI play Tetris, watch two Tetris AIs play against each other, play against a Tetris AI, and play against another player
	made a high scores feature, which writes to a text file, keeping track of information from past games and displays the high scores and best AIs defeated.
