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
from tkinter import Entry,Frame,Button, Label, filedialog, Checkbutton, StringVar, IntVar, Spinbox
from threading import Timer 
import json
import time

class EntryWithPlaceholder(Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey'):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()


vfiles = []
t = None

root = TkinterDnDTk()

scanpath = os.path.abspath('.')


varmp4 = IntVar(root)
varmp4.set(1)
varmov = IntVar(root)
varmov.set(1)
vargif = IntVar(root)
vargif.set(1)
varjpg = IntVar(root)
varjpg.set(1)
varpng = IntVar(root)
varpng.set(1)

def scanfiles():
  global vfiles
  for r,dl,fl in os.walk(scanpath):
    print(r)
    for f in fl:
      p = os.path.join(r,f)
      if p.upper().endswith('.MP4') and varmp4.get()==1 and p not in vfiles:
        vfiles.append(p)
      if p.upper().endswith('.MOV') and varmov.get()==1 and p not in vfiles:
        vfiles.append(p)
      if p.upper().endswith('.GIF') and vargif.get()==1 and p not in vfiles:
        vfiles.append(p)
      if (p.upper().endswith('.JPG') or p.upper().endswith('.JPEG')) and varjpg.get()==1 and p not in vfiles:
        vfiles.append(p)
      if p.upper().endswith('.PNG') and varpng.get()==1 and p not in vfiles:
        vfiles.append(p)
  open('filecache.bin','w').write(json.dumps(vfiles))
  random.shuffle(vfiles)
  files = vfiles[::]
  nextvid(1)


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
root.columnconfigure(1, weight=0)
root.columnconfigure(1, weight=0)
root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=0)
root.rowconfigure(2, weight=0)
root.rowconfigure(3, weight=0)
root.rowconfigure(4, weight=1)


root.geometry("800x600")

buttonscanPath = Button(root,text=f'Scan Path = \'{scanpath}\'')

frame = Frame(root,width=500,height=500,background='#3d3d3d')
frame.grid(column=0,row=4,columnspan=4,sticky='NESW')

player = mpv.MPV(wid=frame.winfo_id())

def resetfiles():
    global vfiles
    player.stop()
    vfiles.clear()
    open('filecache.bin','w').write(json.dumps(vfiles))

def setScanPath():
    global scanpath
    folder_selected = filedialog.askdirectory()
    if folder_selected is not None:
        folder_selected = os.path.normpath(folder_selected)
        if os.path.exists(folder_selected):
            scanpath= folder_selected
            buttonscanPath.configure(text=f'Scan Path = \'{scanpath}\'')

buttonscanPath.configure(command=setScanPath)
buttonscanPath.grid(column=0,row=0,sticky='NESW')

framefiletypes = Frame(root,background='red')
framefiletypes.columnconfigure(0, weight=1)
framefiletypes.columnconfigure(1, weight=1)
framefiletypes.columnconfigure(2, weight=1)
framefiletypes.columnconfigure(3, weight=1)
framefiletypes.columnconfigure(4, weight=1)

framefiletypes.grid(column=0,row=1,columnspan=4,sticky='NESW')

buttonmp4 = Checkbutton(framefiletypes,text='mp4',variable=varmp4)
buttonmp4.grid(column=0,row=0,sticky='NESW')
buttonmp4.select()

buttonmov = Checkbutton(framefiletypes,text='mov',variable=varmov)
buttonmov.grid(column=1,row=0,sticky='NESW')
buttonmov.select()


buttongif = Checkbutton(framefiletypes,text='gif',variable=vargif)
buttongif.grid(column=2,row=0,sticky='NESW')
buttongif.select()


buttonjpg = Checkbutton(framefiletypes,text='jpg',variable=varjpg)
buttonjpg.grid(column=3,row=0,sticky='NESW')
buttonjpg.select()


buttonpng = Checkbutton(framefiletypes,text='png',variable=varpng)
buttonpng.grid(column=4,row=0,sticky='NESW')
buttonpng.select()


frameoptions = Frame(root)

delayVar = StringVar(root)
delayVar.set('6')


labelDelay = Label(frameoptions,text='Post Delay')
labelDelay.grid(column=0,row=0,sticky='NESW')
spindelay =  Spinbox(frameoptions,text='Delay:',textvariable=delayVar,from_=0.1,to=60,increment=0.1)
spindelay.grid(column=1,row=0,sticky='NESW')



cooldownLabel = Label(frameoptions,text='Post Cooldown 0s')
cooldownLabel.grid(column=2,row=0,sticky='NESW')


frameoptions.columnconfigure(2, weight=1)


autovar = IntVar(root)

checkAutoPost = Checkbutton(frameoptions,text='Autopost',variable=autovar)
checkAutoPost.grid(column=5,row=0,sticky='NESW')

lastautopost = None

autotimer = None
def autopost():
    global autotimer
    global lastautopost

    sendfile()
    autotimer = Timer(float(delayVar.get()), autopost)
    autotimer.start()
    lastautopost= time.time()

def toggleautopost(*args):
    global autotimer
    global lastautopost
    autopostOn = autovar.get()==1
    if autotimer is not None:
        autotimer.cancel()
    if autopostOn:
        autotimer = Timer(float(delayVar.get()), autopost)
        autotimer.start()
        lastautopost = time.time()

autovar.trace('w',toggleautopost)
delayVar.trace('w',toggleautopost)


frameoptions.grid(column=0,row=2,columnspan=4,sticky='NESW')

entry = EntryWithPlaceholder(root,placeholder='Filename filter')
entry.grid(column=0,row=3,columnspan=4,sticky='NESW')


buttonRescan = Button(root,text='Scan Path',command=scanfiles)
buttonRescan.grid(column=1,row=0,sticky='NESW')

buttonReset = Button(root,text='Reset Cache',command=resetfiles)
buttonReset.grid(column=2,row=0,sticky='NESW')

buttonLoop = Button(root,text='loop one',command= lambda:slideshow())
buttonLoop.grid(column=3,row=0,sticky='NESW')


instructionsLabel = Label(root,text='Click on this window, and hover the mouse over the discord window, then press the key shortcut controls.')
instructionsLabel.grid(column=0,row=5,columnspan=3,sticky='NESW')

controlsLabel = Label(root,text='Shortcuts: q=Quit d=Delete Video m=Mute, y=Send Drag/Drop, u=nextVid, i=prevVid')
controlsLabel.grid(column=0,row=6,columnspan=4,sticky='NESW')


cooldowndisplaytimer = None
lastSend = None

def updatecooldown():
    global cooldowndisplaytimer
    diff=0.0
    apdiff=0.0
    try:
        if lastSend is not None:
            delaysecs = float(delayVar.get())
            diff = delaysecs-abs(lastSend-time.time())
            diff = max(0,diff)
        if autovar.get()==1 and lastautopost is not None:
            delaysecs = float(delayVar.get())
            apdiff = delaysecs-abs(lastautopost-time.time())
            apdiff = max(0,apdiff)
    except:
        diff=0.0
        apdiff=0.0
    diff = max(diff,apdiff)
    try:
        cooldownLabel.configure(text=f'Post Cooldown {diff:.2f}s')
        if 2 > diff > 0:
            cooldownLabel.configure(background='orange',foreground='white')
        elif diff > 0:
            cooldownLabel.configure(background='red',foreground='white')
        else:
            cooldownLabel.configure(background='green',foreground='white')
    except Exception as e:
        print(e)

    root.after(100,updatecooldown)

updatecooldown()


doSlideshow=False

player.mute=True
currentFile = None
player.loop='inf'

frame.focus()

root.drag_source_register()

lastsearch=''

vidindex=0

def nextvid(e):
  global currentFile,files,vfiles,lastsearch,vidindex
  
  fil = entry.get().replace('Filename filter','')

  filetypes = []

  if varmp4.get()==1:
    filetypes.append('.MP4')
  if varmov.get()==1:
    filetypes.append('.MOV')
  if vargif.get()==1:
    filetypes.append('.GIF')
  if varjpg.get()==1:
    filetypes.append('.JPG')
    filetypes.append('.JPEG')
  if varpng.get()==1:
    filetypes.append('.PNG')

  lastsearch=fil

  searchset = set([x for x in fil.upper().split()])

  files = [x for x in vfiles if all(k in x.upper() for k in searchset) and (any(ft in x.upper() for ft in filetypes) or len(filetypes)==0)]
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
  global doSlideshow

  if doSlideshow:
    nextvid(1)

def slideshow():
  global doSlideshow
  doSlideshow = not doSlideshow

  if doSlideshow:
    buttonLoop.configure(text='loop all')
  else:
    buttonLoop.configure(text='loop one')

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


def sendfile():
    try:
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
      frame.focus()
      frame.focus_force()
      pyautogui.moveTo(currentMouseX, currentMouseY, 0.1)
    except Exception as e:
        print(e)

dt = None

def queuesendfile(e):
  global dt
  timeout = 0.1

  try:
    if autovar.get()==1:
        autovar.set(0)
  except:
    pass

  if dt is not None:
    try:    
      dt.cancel()
    except:
      pass

  delaysecs = float(delayVar.get())
  max(delaysecs,0.1)

  if lastSend is not None:
    diff = abs(lastSend-time.time())
    if diff<delaysecs:
      timeout=delaysecs-diff

  dt = Timer(timeout, sendfile)
  dt.start()

def quit(e):
    try:
        if autovar.get()==1:
            autovar.set(0)
    except:
        pass


    for tim in [autotimer,cooldowndisplaytimer,dt]:
        try:
            tim.cancel()
        except:
            pass

    try:
        root.update_idletasks()
        root.destroy()
    except:
        pass

    exit()
    
def toggleautopost(e):
    if autovar.get()==0:
        autovar.set(1)
    else:
        autovar.set(0)

frame.bind('<Double-Button-1>',nextvid)
frame.bind('<MouseWheel>',nextvid)
frame.bind('<Control-a>', toggleautopost)
frame.bind('<q>', quit)
frame.bind('<d>', delvid)
frame.bind('<m>', toggleMute)
frame.bind('<Button-1>',lambda x:frame.focus())
frame.bind('<Enter>',lambda x:root.focus_force() and root.after(0.1,frame.focus))
frame.bind('<y>',queuesendfile)
frame.bind('<Y>',queuesendfile)
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

try:
    nextvid(None)
except Exception as e:
    print(e)

root.mainloop()
quit(1)