# A Desktop Assistant App Made Especially for Marcus Lance

**Happy Birthday, Marcus Lance!**

> Current version: v0.4.1
> 
> Started on September 22, 2025

# Preview

Below is a preview of what you'd expect with the app (which is the latest release: v0.4.0):

![MikuMiku App v0.4.0 Preview GIF](https://github.com/user-attachments/assets/743c5e1e-82b9-4eb1-bb8c-a431f940287e)

# Wiki

I just made a Wiki for this project, you can access it here now: [DesktopAssistant Wiki](https://github.com/Meta-Dusk/DesktopAssistant/wiki)

> I'm thinking if I should just move everything to the Wiki instead of having most of the information here in the `README.md`... Should I?

# Feature List

Below are the current features implemented:

| Feature | Description |
| ----------- | ----------- |
| **Hatsune Miku** | She'll always be added :) |
| **Randomized Movement** | Miku can move randomly horizontally |
| **Randomized Messages** | Miku has a wide selection of monologues that she'll say |
| **Different Expressions** | Miku has at least 9 different expressions she can choose from |
| **Flips** | Yes, Miku has a small chance of doing two flips during a movement command |
| **Animations** | Various smooth animations |
| **A Menu** | So far, there's only one menu for now |

# Planned Features

The planned features below can be found in the `experimental branch` once development has begun.

| Feature | Description | Completion | Version Implemented |
| ----------- | ----------- | ----------- | ----------- |
| **SFX** | Sound effects for Miku | 0% | - |
| **Easter Eggs** | Some special interactions for Miku | 5% | 0.3.0 -> Current |
| **Extensive Menus** | Add more options and customizability to the menus | 5% | 0.4.1 (Current Pre-Release) |
| **Settings Menu** | For certain stuff | 0% | - |
| **Minigames** | Games that you can play with Miku | 0% | - |
| **Desktop Assistance** | Stuff that could actually assist you with your pc | 0% | - |

# Unintended Behaviors

- You can run multiple instances of Miku, by just simply running the executable again; the result is a shocker... **Mikus Galore!** (There's some visual bugs, such as `z-fighting`[^1], but it does work, and may or may not use a lot of your pc's resources).

Below is what this unintended behavior would look like:

![miku galore preview](https://github.com/user-attachments/assets/9375ed23-2b5c-48ad-a5e9-cedda88ff5a3)

[^1]: `z-fighting` refers to a rendering issue that occurs usually in games. It's a visual bug, that shows rapid fluctuation between two textures that are overlapping each other on the same layer. This issue can be fixed by simply spacing these layers a bit further from the z-axis, which is why they are referred to as `z-fighting`. As for this app, the *band-aid* solution I've implemented for when you want multiple Mikus in your desktop, is by simply having them only force a `always bring to front` state after movement commands, and for a specified duration (such as a second) only.

# Controls

> This section will be removed once the menu feature has been implemented.
> The controls being referred here are for interacting with Miku, or used directly on her.

| Button | Action | Additional Actions |
| ----------- | ----------- | ----------- |
| **Left Click** | Default interaction. | [1] Click twice to open/close the menu.<br> [2] Click and hold to drag Miku around. |
| **Right Click** | Clicking will open a prompt for exiting. | Click again to exit. <br> > (Doing *Right Click* twice will **exit** the app) |

# Known Issues and Fixes

Please do report any issues found that are not solvable with the fixes provided in the tables below:

## Known Issues List

| No. | Issue | Description | Any Fixes? | Is it Fixed? |
| ----------- | ----------- | ----------- | ----------- | ----------- |
| 1 | Miku, the window, or the speech bubble appears to be stretched, clipped, or stretched. | This issue could be because of how `Flet` handles transparent windows. | Try **Fix No. 3** first then **Fix No. 1** if it doesn't work. | Nope, only occurs sometimes. |
| 2 | A border around Miku appears during app launch. | This issue could also be because of how `Flet` handles transparent windows. | Try **Fix No. 1**. | Nope, only occurs sometimes. |
| 3 | Miku suddenly stops her idle animation. | This issue occurs when clicking her registers as a drag event, but is immediately canceled, resulting in the events not registering correctly. | Try **Fix No. 2**. | Only occurs during overlapping action registers. |
| 4 | After dragging Miku, her position doesn't update, and will return to her initial position pre-drag; happens occasionally, but nothing serious. | This issue is still under scrutiny. | Fixes itself. | Occurs rarely, and probably also during overlapping action registers. |
| 5 | Miku's randomized movement anchor is misplaced once dragged off-screen at the bottom; only happens if you intentionally drag her way below bounds of the monitor. | This issue is still under scrutiny. | Fixes itself if you just don't drag her way below the boundaries of your monitor. | Happens all the time based on my testing. |
| 6 | When launching the app, it sometimes just doesn't stop loading. | This issue is still under scrutiny. | Try **Fix No. 1**. | Probably only happens if your device has a lot of background apps. |
| 7 | ~When launching the app, it sometimes refuses to show itself, thus forcing the app to become a background process, which can only be exited by ending it in the task manager, which is very inconvenient.~ | I've implemented a hot fix for this, and the possible reason for this issue, is with how `flet` handles page visibility, when it has been initially set to `False`. | You can try **Fix No. 1** if it happens. | This issue **should be fixed** by now, as I've applied a hot fix for this. |

## Known Solutions List

| No. | Solution | Note |
| ----------- | ----------- | ----------- |
| 1 | Relaunch the app. | Refer to the [Controls](#controls) section. |
| 2 | Move Miku around your screen, then stop. | Refer to the [Controls](#controls) section. |
| 3 | Open any menu. | Refer to the [Controls](#controls) section. |
