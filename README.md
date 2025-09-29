# A Desktop Assistant App made especially for Marcus Lance

> Current version: v0.4.0

**Happy Birthday, Marcus Lance!**

> Started on September 22, 2025

## Controls

> This section will be removed once the menu feature has been implemented.
> The controls being referred here are for interacting with Miku, or used directly on her.

### Left-click

Default interaction. Click twice for a menu. Clicking then holding is a placeholder for now.

### Right-click

Click twice to exit.

### Left-click + drag

Will move Miku around.

## Known Issues and Fixes

Please do report any issues found that are not solvable with the fixes provided below:

### Fix 1

Relaunch the app. Refer to the [Controls](#controls) section.

### Fix 2

Move Miku around your screen, then stop. Refer to the [Controls](#controls) section.

### Fix 3

Open a menu. Refer to the [Controls](#controls) section.

### The Known Issues

1. Miku, the window, or the speech bubble appears to be stretched, clipped, or stretched; try [Fix 3](#fix-3) first then [Fix 1](#fix-1) if it doesn't work. *This issue could be because of how `Flet` handles transparent windows.*
2. A border around Miku appears during app launch; try [Fix 1](#fix-1). *This issue could also be because of how `Flet` handles transparent windows.*
3. Miku suddenly stops her idle animation; try [Fix 2](#fix-2). *This issue occurs when clicking her registers as a drag event, but is immediately canceled, resulting in the events not registering correctly.*
4. After dragging Miku, her position doesn't update, and will return to her initial position pre-drag; happens occasionally, but nothing serious. *This issue is still under scrutiny.*
5. Miku's randomized movement anchor is misplaced once dragged off-screen at the bottom; only happens if you intentionally drag her way below bounds of the monitor. *This issue is still under scrutiny.*
6. When launching the app, it sometimes just doesn't stop loading; try [Fix 1](#fix-1). *This issue is still under scrutiny.*
7. When launching the app, it sometiems refuses to show itself, thus forcing the app to become a background process, which can only be exited by ending it in the task maanger, which is very inconvenient. You can try [Fix 1](#fix-1) but I sure hope this doesn't happen **at all**. I've implemented a hot fix for this, and the possible reason for this issue, is with how `flet` handles page visibility, when it has been initially set to `False`.

## Features

1. Hatsune Miku
2. Randomized Movement
3. Randomized Messages
4. Different Expressions
5. Flips
6. Animations
7. A Menu

## Planned Features

1. SFX
2. More Easter Eggs
3. Extensive Menus **< (In Development in Experimental)**
4. Settings Menu **< (In Development in Experimental)**
5. Minigames
6. Make her an actual "Desktop Assistant" and not just a pet

## Unintended Behaviors

- You can run multiple instances of Miku, by just simply running the executable again; the result is a shocker... **Mikus Galore!** (This is a bit buggy, but works, and may or may not use a lot of your pc's resources)
