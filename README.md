Okular_Plugin
===========

Plugin to preview files using Okular inside kate.

Installation
=================================================
  First build support library Part.so by running 
 
    make

  This library makes setWatchFileModeEnabled() available to the plugin.

  Move or symlink this directory into either of

    /usr/share/apps/kate/pate/
    ~/.kde/share/apps/kate/pate/

  Move or symlink katepate_okular_plugin.desktop into

    /usr/share/kde4/services/
    ~/.kde4/share/kde4/services

Default Shortcuts
=================================================

- Ctrl+Alt+Shift+O   Preview file
- Ctrl+Alt+Shift+G   Goto page
