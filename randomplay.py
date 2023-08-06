import os
import pyautogui

scriptPath = os.path.dirname(os.path.abspath(__file__))
basescriptPath = os.path.split(scriptPath)[0]
os.environ["PATH"] = scriptPath + os.pathsep + os.environ["PATH"]

import random
import mpv
import time 
from tkinterdnd2 import Tk as TkinterDnDTk
from tkinterdnd2 import DND_FILES,DND_TEXT,CF_UNICODETEXT,CF_TEXT,COPY,MOVE,LINK,CF_HDROP,FileGroupDescriptor
from tkinter import Entry,Frame,Button, Label, filedialog
from threading import Timer 
import json
import time

vfiles = []
t = None

root = TkinterDnDTk()


scanpath = os.path.abspath('.')

def scanfiles():
  global vfiles
  for r,dl,fl in os.walk(scanpath):
    print(r)
    for f in fl:
      p = os.path.join(r,f)
      if p.endswith('.mp4') and p not in vfiles:
        vfiles.append(p)
  open('filecache.bin','w').write(json.dumps(vfiles))
  random.shuffle(vfiles)
  files = vfiles[::]


def rescan():
  global t
  if t is None:
    t = 1
    root.after(1000,scanfiles)
  return True

try:
  vfiles = json.loads(open('filecache.bin','r').read())
except Exception as e:
  print(e)

random.shuffle(vfiles)
files = vfiles[::]

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=0)
root.rowconfigure(2, weight=1)

root.geometry("800x600")

entry = Entry(root,text='')
entry.grid(column=0,row=1,sticky='NESW')

buttonscanPath = Button(root,text=f'Scan Path = \'{scanpath}\'')


frame = Frame(root,width=500,height=500,background='#3d3d3d')
frame.grid(column=0,row=2,columnspan=4,sticky='NESW')

def resetfiles():
    global vfiles
    vfiles.clear()

def setScanPath():
    global scanpath
    folder_selected = filedialog.askdirectory()
    if folder_selected is not None:
        folder_selected = os.path.normpath(folder_selected)
        if os.path.exists(folder_selected):
            scanpath= folder_selected
            buttonscanPath.configure(text=f'Video Path = \'{scanpath}\'')

buttonscanPath.configure(command=setScanPath)

buttonscanPath.grid(column=0,row=0,columnspan=4,sticky='NESW')

buttonRescan = Button(root,text='Scan Path',command=scanfiles)
buttonRescan.grid(column=1,row=1,sticky='NESW')

buttonRescan = Button(root,text='Reset Cache',command=resetfiles)
buttonRescan.grid(column=2,row=1,sticky='NESW')

buttonRescan = Button(root,text='Slideshow',command= lambda:slideshow())
buttonRescan.grid(column=3,row=1,sticky='NESW')


instructionsLabel = Label(root,text='Click on this window, and hover the mouse over the discord window, then press the key shortcut controls.')
instructionsLabel.grid(column=0,row=4,columnspan=3,sticky='NESW')


controlsLabel = Label(root,text='Shortcuts: q=Quit d=Delete Video m=Mute, y=Send Drag/Drop, u=nextVid, i=prevVid')
controlsLabel.grid(column=0,row=5,columnspan=4,sticky='NESW')


doSlideshow=False

player = mpv.MPV(wid=frame.winfo_id())
player.mute=True
currentFile = None
player.loop='inf'


frame.focus()

root.drag_source_register()

lastsearch=''

vidindex=0

def nextvid(e):
  global currentFile,files,vfiles,lastsearch,vidindex
  
  fil = entry.get()
  lastsearch=fil

  searchset = set([x for x in fil.upper().split()])

  files = [x for x in vfiles if all(k in x.upper() for k in searchset)]
  if len(files) == 0:
    player.stop()
    root.title('0/0 NO MATCHES')
    return

  increment=1

  try:
    if e.delta > 0:
      increment = -1
  except:
    pass

  if type(e) == int:
    increment = e    
    
  vidindex+=increment

  ind = vidindex%len(files)
  
  currentFile = files[ind]

  root.title('{}/{} {}'.format(ind,len(files),currentFile))
  player.play(currentFile)

@player.event_callback('seek')
def endfileeventhandler(e):
  print(e)
  global doSlideshow
  print(e)
  if doSlideshow:
    nextvid(1)

def slideshow():

  global doSlideshow
  doSlideshow = not doSlideshow
  print('slideshow',doSlideshow)

def delvid(e):
  global currentFile
  lastFile = currentFile
  nextvid(1)
  os.remove(lastFile)
  if lastFile in files:
    files.remove(lastFile)
  if lastFile in vfiles:
    vfiles.remove(lastFile)
  

def toggleMute(e):
  player.mute = not player.mute

lastSend = None

def sendfile():
  print('send')
  global lastSend

  root.attributes('-topmost', 1)
  root.attributes('-topmost', 0)

  currentMouseX, currentMouseY = pyautogui.position()

  winx,winy,winw,winh = root.winfo_x(), root.winfo_y(), root.winfo_width(), root.winfo_height()

  winx += winw//2
  winy += winh//2

  pyautogui.moveTo(winx, winy, 0.2)
  pyautogui.keyDown('shift')
  pyautogui.mouseDown()
  pyautogui.moveTo(currentMouseX, currentMouseY, 0.4)
  pyautogui.mouseUp()
  pyautogui.keyUp('shift')
  lastSend=time.time()

  root.attributes('-topmost', 1)
  root.attributes('-topmost', 0)

  pyautogui.moveTo(winx, winy, 0.1)
  pyautogui.click()
  pyautogui.moveTo(currentMouseX, currentMouseY, 0.1)

dt = None


def queuesendfile(e):
  global dt
  timeout = 0.1

  if dt is not None:
    try:
      dt.cancel()
    except:
      pass

  if lastSend is not None:
    diff = abs(lastSend-time.time())
    if diff<6:
      timeout=6-diff



  dt = Timer(timeout, sendfile)
  dt.start()


root.bind('<Double-Button-1>',nextvid)
root.bind('<MouseWheel>',nextvid)
frame.bind('<q>', lambda x:exit())
frame.bind('<d>', delvid)
frame.bind('<m>', toggleMute)
frame.bind('<Button-1>',lambda x:frame.focus())
frame.bind('<Enter>',lambda x:root.focus_force() and root.after(1,frame.focus))
frame.bind('<y>',queuesendfile)
frame.bind('<U>',queuesendfile)
frame.bind('<u>',lambda x:nextvid(1))
frame.bind('<U>',lambda x:nextvid(1))
frame.bind('<i>',lambda x:nextvid(-1))
frame.bind('<I>',lambda x:nextvid(-1))
entry.bind('<Return>',nextvid)




def dragInit(e):
  fbin = '{{{}}}'.format(os.path.abspath(currentFile))
  nextvid(e)
  return (COPY,DND_FILES, fbin)

frame.drag_source_register("*")
frame.dnd_bind('<<DragInitCmd>>',dragInit)

root.mainloop()