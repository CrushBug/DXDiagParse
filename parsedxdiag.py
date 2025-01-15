#/usr/bin/python3
#parsedxdiag.py
# parse through a DXDiag report file and pull out the useful information
# by Derek French
# v1.13
#- 1.13 - added checking for valid report file encoding format
#- 1.12 - added User DPI
#- 1.11 - switching to def main(), print() formatting

#imports
from dxdiagfile import DXDiagFile
import os
import sys

#constants
FILENAME_POS = 1
VERSION = '1.12'

#functions
def ParseFile(fileName):
  dxDiag = DXDiagFile(fileName)
  if dxDiag.valid is False:
    print(f"Failed to read report file {fileName}; check report file encoding.")
    sys.exit()
  sysInfo = dxDiag.systemInformation
  print(f"DxDiag Report Parser {VERSION}")
  print('--------------------------')
  print(f"Report time:      {sysInfo['reportTime']}")
  print(f"Computer Name:    {sysInfo['machineName']}")
  print(f"OS:               {sysInfo['osName']}")
  print(f"Language:         {sysInfo['language']}")
  print(f"System:           {sysInfo['systemDetails']}")
  print(f"CPU:              {sysInfo['cpuName']}")
  memoryString = ''
  memoryInMeg = sysInfo['memoryInMB']
  if memoryInMeg > 1023:
    memoryString = str(sysInfo['memoryInGB']) + ' GB'
  else:
    memoryString = str(sysInfo['memoryInMB']) + ' MB'
  print(f"RAM:              {memoryString}")
  print(f"Page File:        {sysInfo['pageFile']}")
  print(f"DirectX:          {sysInfo['directXVersion']}")
  print(f"User DPI:         {sysInfo['userDPI']}")
  print()
  #video displays
  displayNumber = 1
  for cards in dxDiag.videoDisplays:
    print(f"Video display {displayNumber}")
    print(f"Video card:       {cards['cardName']}")
    print(f"Driver version:   {cards['driverVersion']}")
    #convert to GB as needed
    vRAM = cards['VRAM']
    vRAMLine = 'VRAM:             ' + str(vRAM) + ' MB'
    if vRAM > 1023:
      valueInGig = vRAM / 1024
      vRAM = round(valueInGig)
      vRAMLine = 'VRAM:             ' + str(vRAM) + ' GB'
    print(vRAMLine)
    print(f"Display mode:     {cards['displayMode']}")
    #clean up monitor names into 1 line
    monitorName = cards['monitorName']
    monitorModel = cards['monitorModel']
    monitorLine = monitorName
    if not monitorModel == 'unknown':
      #model isn't unknown, but let's only show it if it isn't a repeat of the Name
      modelLen = len(monitorModel)
      if not monitorName[:modelLen] == monitorModel: monitorLine += ' (' + monitorModel  + ')'
    print(f"Monitor name:     {monitorLine}")
    print()
    displayNumber += 1
  #audio devices
  audioPrefix = 'Sound devices:    '
  for audio in dxDiag.soundDevices:
    print(audioPrefix + audio)
    audioPrefix = '                  '
  print()
  #drives
  driveLetters = ''
  driveInfo = ''
  driveInfoPrefix = ''
  for drives in dxDiag.drives:
    driveLetters += drives['driveLetter'] + ' '
    driveInfo += driveInfoPrefix + drives['driveLetter'] + ': '
    if not drives['freeSpace'] == '':
      driveInfo += '(free ' + drives['freeSpace'] + '/' + drives['totalSpace'] + ') ' + drives['fileSystem'] + ' - '
    driveInfo += drives['model']
    driveInfoPrefix = '\n                  '
  print(f"Drives:           {driveLetters}")
  print(f"Drive info:       {driveInfo}")
  #any DXDiag errors
  if dxDiag.dxErrorCount > 0:
    print()
    print('DXDIAG DETECTED AN ERROR:')
    print(f"Error count: {dxDiag.dxErrorCount}")
    for errors in dxDiag.dxErrorNotes :
      print(f"- {errors}")
    print()
    print('Check the DxDiag report section "DxDiag Notes"')
#end ParseFile()

def PrintHelp():
  print(f"ParseDxDiag {VERSION} - parses a DxDiag report file")
  print()
  print('parsedxdiag.py [DxDiag.txt]')
  print('DxDiag.txt   - name of the DxDiag file, defaults to DxDiag.txt')
#end PrintHelp()

#mainline
def main():
  fileName = ''
  argCount = len(sys.argv)
  #argCount 1 is no parameters, 2 is 1, etc.
  if argCount == 1:
    #no args passed, assume DxDiag.txt file
    fileName = 'DxDiag.txt'
  elif argCount == 2:
    #single arg passed
    fileName = sys.argv[FILENAME_POS]
    if fileName == '-h' or fileName == '--help':
      fileName = ''
  else:
    #more than 2 arguments, print help
    fileName = ''
  if fileName == '':
    #print help
    PrintHelp()
  else:
    #check if the file exists
    if os.path.exists(fileName):
      #parse the file
      ParseFile(fileName)
    else:
      #print help
      print('ERROR: Specified file not found.')
      print()
      PrintHelp()
#end main()

if __name__ == "__main__":
  main()
