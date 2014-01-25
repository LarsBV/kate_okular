Okular_Plugin
===========

Plugin to preview files using Okular inside kate.

Installation
=================================================
  First build support library Part.so by running 
 
    make

  This library makes setWatchFileModeEnabled() available to the plugin.

  Symlink this directory, and the .desktop, into the right places

    ln -s $(pwd) ~/.kde/share/apps/kate/pate/okular_plugin
    ln -s $(pwd)/katepate_okular_plugin.desktop ~/.kde4/share/kde4/services/

Default Shortcuts
=================================================

- Ctrl+Alt+Shift+O   Preview file
- Ctrl+Alt+Shift+G   Goto page
