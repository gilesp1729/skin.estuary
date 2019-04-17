import xbmc
import xbmcgui

ACTION_MOUSE_RIGHT_CLICK = 101
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK = 92

white50 = 'special://skin/media/colors/white50.png'
grey50 = 'special://skin/media/colors/grey50.png'


debug = 0


class DynamicOSD(xbmcgui.WindowXMLDialog):
   def __init__(self, *args, **kwargs ):
      xbmcgui.WindowXMLDialog.__init__(self)

# These labels are just for debugging things.
      self.debugLabel = [None for i in range(10)]
      self.createDebugLabel(0)
      self.createDebugLabel(1)
      self.createDebugLabel(2)
      self.createDebugLabel(3)
      self.createDebugLabel(4)
      self.createDebugLabel(5)
      
# These do not change - let Kodi do the scaling. 
      screen_width = 1920
      screen_height = (1920 * self.getHeight()) / self.getWidth()

# Synthesise a progress bar out of buttons. 
# We do this because ControlProgress does not reliably appear, and we can't interact with controls in the XML.
# In any event we want finer grained control than the percentage gives us.

      self.barY = screen_height - 120
      self.barWidth = screen_width
      self.tsProgressBg = xbmcgui.ControlButton(0, self.barY, self.barWidth, 15, ' ', noFocusTexture=grey50)
      self.addControl(self.tsProgressBg)
      self.tsProgressBg.setEnabled(False)
      
# Let player settle before asking it for duration, etc for the first time.
      xbmc.sleep(100)
      self.calcProgress()
      self.tsProgress = xbmcgui.ControlButton(self.progX, self.barY, self.progWidth, 15, ' ', noFocusTexture=white50)
      self.addControl(self.tsProgress)
      self.tsProgress.setEnabled(False)
      if self.progWidth == 0:
         self.tsProgress.setVisible(False)
         
# Calculate the scaled positions of PVR.TimeshiftStart and End on the progress bar.
# Position = (TimeshiftStart - StartTime) / Duration
# Width = (TimeshiftEnd - TimeshiftStart) / Duration
# (clamped and scaled appropriately into pixels)
#
   def calcProgress(self):
      self.debugRawData()

      tsStart = self.translate_hhmm(xbmc.getInfoLabel('PVR.TimeshiftStart'))
      tsEnd = self.translate_hhmm(xbmc.getInfoLabel('PVR.TimeshiftEnd'))

# v18 get duration and finish time from the right infolabels      
      if xbmc.getCondVisibility('VideoPlayer.HasEpg'):
         duration = self.translate_hhmm(xbmc.getInfoLabel('PVR.EpgEventDuration(hh:mm)'))
         finish_time = self.translate_hhmm(xbmc.getInfoLabel('Videoplayer.EndTime'))
      else:
         duration = self.translate_hhmm(xbmc.getInfoLabel('Player.Duration(hh:mm)'))
         finish_time = self.translate_hhmm(xbmc.getInfoLabel('Player.FinishTime'))
         
# Player.StartTime can be unreliable if starting channel from bootup.
# Calculate it from FinishTime - Duration.
      startTime = self.subtract_times(finish_time, duration)
      
# Take care of tsStart before the start of the current program
# Protect division by zero (some DVD lead-in tracks come up with zero duration)
      tsDuration = min(self.subtract_times(tsEnd, tsStart), self.subtract_times(tsEnd, startTime))
      self.progWidth = 0
      if duration > 0:
         self.progWidth = (tsDuration * self.barWidth) / duration
      self.setLabel(3, str(startTime) + " for " + str(duration))
      self.setLabel(4, "TS: " + str(tsStart) + " to " + str(tsEnd) + " for " + str(tsDuration))

# Take care of TVH bug where tsEnd is cut off when buffer runs out
# (rather than correctly advancing tsStart)
# Do this by using the current time for tsEnd and subtracting tsDuration to get tsStart
      tsEnd = self.translate_hhmm(xbmc.getInfoLabel('System.Time'))
      tsStart = self.subtract_times(tsEnd, tsDuration)

# Watch out for 12/24 hours added to the difference if tsStart earlier than startTime
      tsStart = self.subtract_times(tsStart, startTime)
      if tsStart > tsEnd:
         tsStart = 0
         
# Protect division by zero (some DVD lead-in tracks come up with zero duration)
      self.progX = 0
      if duration > 0:
         self.progX = (tsStart * self.barWidth) / duration
      
# Update the width and position of the progress bar. Setting a button to a zero width seems
# to produce strange results, so in this case just hide the thing.

   def updateProgress(self):
      self.calcProgress()
      self.tsProgress.setPosition(self.progX, self.barY)
      if self.progWidth == 0:
         self.tsProgress.setVisible(False)
      else:
         self.tsProgress.setWidth(self.progWidth)
         
# Translate hh:mm into a time in minutes since the previous midnight. 
# hh:mm may be 24-hour or 12-hour with AM/PM.
   def translate_hhmm(self, hhmm):
      colon = hhmm.find(':')
      minutes = int(hhmm[0:colon]) * 60 + int(hhmm[colon+1:colon+3])
      pm = hhmm.find('PM')
      if pm > 0:
         minutes = minutes + 12 * 60
      return minutes
      
# Subtract two times. If the result is negative, add 12 or 24 depending on what
# clock format we appear to be using. This relies on the fact that TV programs 
# are usually only a couple of hours, so the larger time is something like
# 12:xx or 23:xx. There appears to be no way to independently determine the
# clock format.

   def subtract_times(self, end, start):
      diff = end - start
      if diff < 0:
         if start > 12 * 60 + 59:
            diff = diff + 24 * 60
         else:
            diff = diff + 12 * 60
      return diff

# Create a debug label.
   def createDebugLabel(self, i):
      if debug:
         self.debugLabel[i] = xbmcgui.ControlLabel(100, 200 + 50 * i, 1500, 50, '')
         self.addControl(self.debugLabel[i])
      
   def setLabel(self, i, text):
      if debug:
         self.debugLabel[i].setLabel(text)

   def debugRawData(self):
      if debug:
         self.setLabel(0, xbmc.getInfoLabel('Player.Title'))
         if xbmc.getCondVisibility('VideoPlayer.HasEpg'):
            self.setLabel(1, "EPG: ending " + xbmc.getInfoLabel('PVR.EpgEventFinishTime(hh:mm:ss xx)') + " for " + xbmc.getInfoLabel('PVR.EpgEventDuration(hh:mm:ss)'))
         else:
            self.setLabel(1, "Player: " + xbmc.getInfoLabel('Player.StartTime(hh:mm:ss xx)') + " to " + xbmc.getInfoLabel('Player.FinishTime(hh:mm:ss xx)') + " for " + xbmc.getInfoLabel('Player.Duration(hh:mm:ss)'))
         self.setLabel(2, "TS: " + xbmc.getInfoLabel('PVR.TimeshiftStart(hh:mm:ss xx)') + " to " + xbmc.getInfoLabel('PVR.TimeshiftEnd(hh:mm:ss xx)') + " cur: " + xbmc.getInfoLabel('PVR.TimeshiftCur(hh:mm:ss xx)') + " system: " + xbmc.getInfoLabel('System.Time(hh:mm:ss xx)'))

# Action handler for right click, since we can't do it in a keymap.
# Prevent it from leaving the OSD up while the script goes away...
   def onAction(self, act):
      self.setLabel(3, str(act.getId()))
      if act.getId() == ACTION_MOUSE_RIGHT_CLICK:
         xbmc.executebuiltin("Dialog.Close(VideoOSD)")
      elif act.getId() == ACTION_PREVIOUS_MENU:
         self.close()
      elif act.getId() == ACTION_NAV_BACK:
         self.close()
         
# ------------------------------------------------------------------------------------
# Display the window. It will be taken down when the OSD unloads,

display = DynamicOSD('VideoOSDControls.xml', 'special://skin/xml')
display.doModal()
del display
