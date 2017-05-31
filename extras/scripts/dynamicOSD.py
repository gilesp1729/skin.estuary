import xbmc
import xbmcgui

white50 = 'special://skin/media/colors/white50.png'
grey50 = 'special://skin/media/colors/grey50.png'


class DynamicOSD(xbmcgui.WindowXMLDialog):
   def __init__(self, *args, **kwargs ):
      xbmcgui.WindowXMLDialog.__init__(self)

# This label is just for debugging things.
#      self.debugLabel = xbmcgui.ControlLabel(200, 400, 1500, 50, '')
#      self.addControl(self.debugLabel)
      
# Synthesise a progress bar out of buttons. 
# We do this because ControlProgress does not reliably appear, and we can't interact with controls in the XML.
# In any event we want finer grained control than the percentage gives us.

      self.barY = self.getHeight() - 120
      self.barWidth = self.getWidth()
      self.tsProgressBg = xbmcgui.ControlButton(0, self.barY, self.barWidth, 15, ' ', noFocusTexture=grey50)
      self.addControl(self.tsProgressBg)
      self.tsProgressBg.setEnabled(False)
      
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
      duration = self.translate_hhmm(xbmc.getInfoLabel('Player.Duration(hh:mm)'))

# Player.StartTime can be unreliable if starting chanel from bootup.
# Calculate it from FinishTime - Duration.
#      startTime = self.translate_hhmm(xbmc.getInfoLabel('Player.StartTime'))
      finish_time = self.translate_hhmm(xbmc.getInfoLabel('Player.FinishTime'))
      startTime = self.subtract_times(finish_time, duration)

      tsStart = self.translate_hhmm(xbmc.getInfoLabel('PVR.TimeshiftStart'))
      tsEnd = self.translate_hhmm(xbmc.getInfoLabel('PVR.TimeshiftEnd'))
      
# Take care of tsStart before the start of the current program
      tsDuration = min(self.subtract_times(tsEnd, tsStart), self.subtract_times(tsEnd, startTime))
      self.progWidth = (tsDuration * self.barWidth) / duration

# Watch out for 12/24 hours added to the difference if tsStart earlier than startTime
      tsStart = self.subtract_times(tsStart, startTime)
      if tsStart > tsEnd:
         tsStart = 0
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

# Try and send clicks and stuff through to the underlying window, to minimise out-of-sync unloading
# of OSD, SeekBar and TopBarOverlay (not altogether successful)

   def onClick(self):
      pass

# Translate hh:mm into a time in minutes. Ignore any AM/PM in the string.
   def translate_hhmm(self, hhmm):
      colon = hhmm.find(':')
      return int(hhmm[0:colon]) * 60 + int(hhmm[colon+1:colon+3])
      
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

# ------------------------------------------------------------------------------------
# Display the window. It will be taken down when the OSD unloads,

display = DynamicOSD('VideoOSDControls.xml', 'special://skin/xml')
display.doModal()
del display






#tsStart =  xbmc.getInfoLabel('PVR.TimeshiftStart')
#tsEnd =  xbmc.getInfoLabel('PVR.TimeshiftEnd')
#start =  xbmc.getInfoLabel('Player.StartTime')
#end =  xbmc.getInfoLabel('Player.FinishTime')

#win.setProperty('TsStartScaled', duration)
#win.setProperty('TsEndScaled', '50')
