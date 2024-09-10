# funny 2d platformer writen in python

Dependencies And Requirements:

Python For Windows 3.x: [https://www.python.org/downloads/windows/]

Windows 10 or above

You could build from source to play on other platforms but idk anything about that.

## Building From Source
you need python (really now? i didn't figure that.)

basic knowledge of the funny bleep bloop computing mechanism.

On the Homepage on the repository, click on the green **"Code"** button, then click on **"Download ZIP"** next to the zipper thing, then extract it when it's finished downloading.

### Windows Guide:
You will need **'pyinstaller'** to build from source, if you haven't installed it already, read **"Installing pip"**, or skip ahead to **"Building"** if you have it already.

#### Installing "pip"
Pip usually comes with an installation of Python, to check if you have it installed, open up command prompt and type in **"pip"**.

If an error didn't show up, skip ahead to **"Installing pyinstaller"**, otherwise, copy and paste this into command prompt:
```bash
py -m ensurepip --upgrade
```

#### Installing "pyinstaller"
Copy and paste this into command prompt, wait for it to finish, then continue to **"Building"**
```bash
pip install pyinstaller
```

#### Building
First, locate the **"builder.spec"** file in the **Downloaded ZIP**, right-click it, and click **"Copy as path"**.

Then open up a terminal, and type in:
```bash
pyinstaller (Spec Path)
```
Replace "(Spec Path)" with the path you copied earlier, make sure to remove both **"** when pasting, otherwise you will get an error.

It will spit out two folders in the location of the .spec file, **"dist"**, and **"build"**.

Go ahead and delete the **"build"** folder, you don't need it.

Move the **"game"** folder out of the **"dist"** folder. (it's what i do normally.)

Next, which I know is a little annoying, but I couldn't find a workaround for this, go into the **"_internal"** folder, and locate the following:
+ res
+ map
+ snd

Move those out of the **"_internal"** folder, and into the same foler where the executables are.

Otherwise, launching the executables will cause them to take a tantrum about missing their favourite folders.

The tools folder ain't needed, you can just get ridda' that. (or install them tools, you should, actually.)

### Mac Guide:
¯\_(ツ)_/¯

**idk**
### Linux Guide:
¯\_(ツ)_/¯

**idk**

## Tips For Editing
.spec File Documentation: [https://pyinstaller.org/en/stable/spec-files.html]

Python 3 Documentation (nah really?): [https://docs.python.org/3/]

There's a **"tools"** folder: containing some applications, not made by me, but they're not just useful for this game.

add proper mpd module documentation here

(pygameplus docs i guess??? if you couldn't tell both libs made by me)

## other tips
You can save space by the deleting the **"tools"** folder, you don't need it, it just contains some useful tools for not just the game but for general use. (they are installers, not made by me.)
