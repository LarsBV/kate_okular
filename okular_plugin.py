'''Okular plugin '''

# Author: Lars Banner-Voigt
# License see readme.txt

# Reference docs
#    actions_in_okular_part.txt
#    http://api.kde.org/4.11-api/applications-apidocs/kate/kate/interfaces/kate/html/index.html
#    http://patches.fedorapeople.org/pate-docs/_modules/kate/__init__.html#action

from PyKDE4.kdecore import *
from PyKDE4.kdeui import *
from PyKDE4.kio import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import kate

import sip
from .Okular.Part import *

class mouseEventFilter(QObject):
    def __init__(self, parent):
        super(mouseEventFilter, self).__init__()
        self.selecting = False
        self.parent = parent
      
    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseMove:
            if self.selecting:
                print("mousemove!")
                print( self.parent.part.getSourceReference(event.pos()) )
        elif event.type() == QEvent.MouseButtonPress:
            self.selecting = True
            print("mouse button press!")
            print( self.parent.part.getSourceReference(event.pos()) )
        elif event.type() == QEvent.MouseButtonRelease:
            print("mouse button release!")
            self.selecting = False
            print( self.parent.part.getSourceReference(event.pos()) )
            
        return False
      
class OkularPlugin(QObject):
  def __init__(self):
    QObject.__init__(self)
      
    ## Create Kate window
    self.kate_window    = kate.mainInterfaceWindow()
    self.tool_view      = self.kate_window.createToolView("preview", self.kate_window.Right, SmallIcon("okular"), "Okular")
    self.win            = QWidget(self.tool_view)
    
    ## Load okular part
    factory             = KPluginLoader("okularpart").factory()
    self.part           = factory.create(self, "OkularPart", ["ViewerWidgetout",])
    self.part           = sip.cast(self.part, Okular.Part)
    
    
    self.okular_actions = self.part.actionCollection()
    print("Okular actions: ", self.okular_actions)
      #print("Action: %s: %s, context: %s" % (
      #                         action.objectName(),
      #                         action.iconText(),
      #                         action.shortcutContext()))
    
    
    kate.configuration.root.clear()
    
    #Actions
    
    ''' Adds a shortcut using its stored, or its default shortcut. Takes a name-string as icon. '''
    def addAction(self, objectName, icon, text, shortcut = "", slot = None):
        act = KAction(KIcon(icon), text, self.win)
        act.setObjectName(objectName)
        
        if not act.objectName() in kate.configuration:
            kate.configuration[act.objectName()] = shortcut

        act.setShortcut(kate.configuration[act.objectName()])
        act.changed.connect( self.onActionChange )
        if slot != None:
            act.triggered.connect( slot )
        self.kate_window.window().actionCollection().addAction(act.objectName(), act)
        act.setEnabled(False)
        return act
        
        
    self.act_preview_file = addAction(self, 'preview-file',  'document-open', 'preview file', 'Ctrl+Alt+Shift+O', self.open )
    self.act_go_jump      = addAction(self, 'goto-shortcut', 'go-jump', 'Goto page', 'Ctrl+Alt+G', self.okular_actions.action('go_goto_page').trigger )
    
    self.act_preview_file.setEnabled(True)
    
    ## Build a toolbar 
    self.toolBar        = QToolBar(self.win)
    toolButtonAction    = QWidgetAction(self.win)
    toolButton          = QToolButton()
    self.toolMenu       = QMenu(toolButton)
        
    
    toolButton.setMenu(self.toolMenu)
    toolButton.setPopupMode(QToolButton.InstantPopup)
    toolButtonAction.setDefaultWidget(toolButton)

    # Update the buttons icon / main action when an action gets selected
    self.toolMenu.triggered.connect(toolButton.setDefaultAction)
    
    # toolButton provides a menu with actions
    for item in ['mouse_drag', 'mouse_zoom', 'mouse_select', 'mouse_textselect', 'mouse_tableselect']:
        act = self.okular_actions.action(item)
        if act:
            act = addAction(self, item, act.icon(), act.text(), act.shortcut().toString(), act.trigger)
            act.setEnabled(True)
            self.toolMenu.addAction(act)
            if item == 'mouse_drag':
                act.trigger()
    
    ## Arrange toolbar
    # self.toolBar.addAction(self.act_show_panel)
    self.toolBar.addAction(self.act_preview_file)
    self.toolBar.addAction(toolButtonAction)
    self.toolBar.addAction(self.act_go_jump)

    

    ## Disable okular's actions shortcut's, after we have used their default's as our own
    for action in self.okular_actions.actions():
      action.setShortcut(QKeySequence())


    ## Fit okular and toolbar together
    layout = QVBoxLayout()
    layout.addWidget(self.part.widget())
    layout.addWidget(self.toolBar)    
    self.win.setLayout(layout)
            
    ## Don't let us take focus, TODO check if this actually works and subwidgets can't grab the focus.
    self.win.setFocusPolicy(Qt.NoFocus)
    
    ## Test
    #for (name, value) in inspect.getmembers(self.part):
    #    print("Name: %s\nValue: %s\n" % (name,value))
    
    #print(self.part.staticMetaObject.superClass().superClass().superClass().className())
        
    # Connect to new document and document deleted. When opening a session etc. new documents
    # are created before the plugin, so the open preview function handles these.
    kate.documentManager.documentCreated.connect(self.new_document)
    kate.documentManager.documentDeleted.connect(self.close_document)        

  def onSourceReferenceActivated(self, file, line, col):
      handled = True
      print("Open ", file, line, col)
      print(self.part.getSourceReference(QPoint(100,100)))

      
  def onActionChange(self):
      print("Action change: %s shortcut %s" % ( self.sender().objectName(), self.sender().shortcut().toString() ))
      print("Set: '%s'" % (self.sender().objectName()), self.sender().shortcut().toString())
      kate.configuration[self.sender().objectName()] = self.sender().shortcut().toString()
      
        
      kate.configuration.save()
    

  def new_document(self, doc):
      print("New Document, compare %s == %s" % (doc.url(), self.part.url()))
      doc.documentUrlChanged.connect(self.check_watcher)
      
  def check_watcher(self, doc):
      if doc.url() == self.part.url():  
        doc.documentSavedOrUploaded.disconnect()
        doc.reloaded.disconnect()
        doc.documentSavedOrUploaded.connect(self.reload)
        doc.reloaded.connect(self.reload)
        self.part.setWatchFileModeEnabled(False)
        print("Disable file watcher")
        
  def close_document(self, doc):
      print("Close document")
      if kate.documentManager.findUrl(self.part.url()) == None:
          self.part.setWatchFileModeEnabled(True)
          print("Enable File Watcher")
    
  def reload(self):
      self.part.reload()
      print("Reload!")

      
  def open(self):
    document = kate.activeDocument().url()
    fileName = KFileDialog.getOpenUrl(document)
    
    if fileName != "":
      if self.part.openUrl(fileName): # Invalid page number so we get the correct function, not the slot function wich doesn't return a bool
        # Disable okular's file watcher, if file open, due to KDE Bug 329101
        if kate.activeDocument() != None:
            if kate.documentManager.findUrl(self.part.url()) == None:
                self.part.setWatchFileModeEnabled(True)
            else:  
                self.check_watcher(kate.activeDocument())
            
        self.kate_window.showToolView(self.tool_view)
        
        self.act_preview_file.setEnabled(True)
        self.act_go_jump.setEnabled(True)
        #self.act_show_panel.setEnabled(True)
        
        print(self.part.currentDocument())
        #self.part.openSourceReference.disconnect()
        self.part.openSourceReference.connect(self.onSourceReferenceActivated)


        #print("¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤")
        #print("Widget: ", self.part.pageView().viewport())
        #self.part.pageView().setObjectName("Testooo")
        #self.filter = mouseEventFilter(self)
        #self.part.pageView().viewport().installEventFilter(self.filter)                
      
        self.part.enableTOC(True)
        return True
      
    return False
