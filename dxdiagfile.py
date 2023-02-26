#/usr/bin/python3
#dxdiagfile.py
# DXDiag.txt report file class
# by Derek French
# v0.12
#- (0.12) added sanity check in AMD and NVIDIA decodes for when "Driver File Version: Unknown (Unknown)"
#- (0.11) fixing up file handling and comments

#imports
import os

#constants
FILE_DRIVERSAMD = 'driverDecodeAMD.csv'

#functions
def DecodeAMDDriverVersion(driverString, driverVersions):
  """
  turn a DXDiag AMD driver string from "30.00.15002.1004 (English)" to "Adrenalin 22.5.1 (WHQL)"
  driverVersions - a dictionary of "31.00.14000.61002": "22.12.2 (WHQL)",... entries
  """
  #NEW sanity check for when "Driver File Version: Unknown (Unknown)"
  if driverString.startswith('Unknown'): return "Unknown"
  #check to make sure the driverVersions dictionary has entries
  if len(driverVersions) == 0: return driverString
  spaceSplit = driverString.split(' ') # "30.00.15002.1004", "(English)"
  numbers = spaceSplit[0]              # "30.00.15002.1004"
  numberSplit = numbers.split('.')     # "30", "00", "15002", "1004"
  majorVersion = int(numberSplit[0])   # 30
  if numbers in driverVersions:
    decodedAMDString = "Adrenalin " + driverVersions[numbers]
  else:
    if majorVersion < 30:
      decodedAMDString = driverString + " - unknown Adrenalin version, OLDER than September 2021"
    else:
      decodedAMDString = driverString + " - unknown Adrenalin version"
  return decodedAMDString

def DecodeNVIDIADriverVersion(driverString):
  """
  turn a DXDiag NVIDIA driver string from "30.00.0015.1179 (English)" OR "30.0.15.1179" to "511.79"
  """
  #NEW sanity check for when "Driver File Version: Unknown (Unknown)"
  if driverString.startswith('Unknown'): return "Unknown"
  spaceSplit = driverString.split(' ')    # "30.00.0015.1179", "(English)"
  numbers = spaceSplit[0]                 # "30.00.0015.1179"
  numberSplit = numbers.split('.')        # "30", "00", "0015", "1179"
  #only index 2 and 3 matter
  index2 = numberSplit[2]                 # "0015"
  index2 = str(int(index2))               # "0015" -> 15 -> "15"
  index3 = numberSplit[3]                 # "1179"
  majorVersion = index2[1:] + index3[:2]  #511
  minorVersion = index3[2:]               #79
  decodedNVIDIAString = majorVersion + '.' + minorVersion
  if int(majorVersion) < 500: decodedNVIDIAString += " - OLDER than January 2022"
  return decodedNVIDIAString

class DXDiagFile:
  #shared dictionary of AMD driver versions
  __driverVersionsAMD = {}

  def __init__(self, reportFileName):
    self.__filename = reportFileName
    self.__filecontents = []
    self.__found = False
    #initialize all the details
    #System info results
    self.__systemInformation = {
      'reportTime': '',
      'machineName': '',
      'osName': '',
      'language': '',
      'systemDetails': 'n/a',
      'cpuName': '',
      'memoryString': '',
      'memoryInMB': 0,
      'memoryInGB': 0,
      'pageFile': '',
      'directXVersion': ''
    }
    #DxDiag Notes
    self.__dxErrorNotes = []
    #Display Devices
    self.__videoDisplays = []
    #private lists to be assembled into self.__videoDisplays
    self.__videoCardNames = []
    self.__videoCardManufacturers = []
    self.__videoDriverVersions = []
    self.__videoCardRAM = []
    self.__videoDisplayModes = []
    self.__monitorNames = []
    self.__monitorModels = []
    #Sound Devices
    self.__soundDevices = []
    #Drives
    self.__drives = []
    #load up the AMD driver decode data
    self.__LoadAMDDriverVersions()
    #read the entire file for easier processing
    if os.path.exists(self.__filename):
      with open(self.__filename, "r") as fh:
        self.__filecontents = fh.readlines()
      self.__found = True
      self.__ParseFile()
  #end __init__()

  def __LoadAMDDriverVersions(self):
    """
    Load the driverDecodeAMD.csv file into the __driverVersionsAMD dictionary
    """
    #TODO check if a new version, download, and use that
    if os.path.exists(FILE_DRIVERSAMD):
      with open(FILE_DRIVERSAMD, "r") as fhAMD:
        for driverLine in fhAMD:
          entry = driverLine.strip().split(',')
          self.__driverVersionsAMD[entry[0]] = entry[1]
  #end __LoadAMDDriverVersions()

  def __ParseFile(self):
    """
    Parse the file sections for information
    """
    self.__ParseSystemInformation()
    self.__ParseDxDiagNotes()
    self.__ParseDisplayDevices()
    #video info is scattered in several lists; pull them all together
    self.__AssembleVideoInfo()
    self.__ParseSoundDevices('Sound Devices')
    self.__ParseSoundDevices('Sound Capture Devices')
    self.__ParseDrives()
  #end __ParseFile()

  def __ParseSystemInformation(self):
    """
    Parse the System Information section of the file
    """
    #------------------
    #System Information
    #------------------
    #parse the filecontents for the System Information section
    foundStart = False
    foundEnd = False
    skipNextLine = False
    for fileLine in self.__filecontents:
      if skipNextLine:
        skipNextLine = False
        continue
      line = fileLine.strip()
      if line == "System Information": 
        foundStart = True
        skipNextLine = True
      if foundStart:
        #the next line after "System Information" is "------------------", so skip it
        if skipNextLine: continue
        if line.startswith('Time of this report:'): self.__systemInformation['reportTime'] = line[21:]
        if line.startswith('Machine name:'): self.__systemInformation['machineName'] = line[14:]
        if line.startswith('Operating System:'): self.__systemInformation['osName'] = line[18:]
        if line.startswith('Language:'): self.__systemInformation['language'] = line[10:]
        if line.startswith('System Manufacturer:'):
          systemManufacturer = line[21:]
          if systemManufacturer != 'System manufacturer':
            self.__systemInformation['systemDetails'] = systemManufacturer
        if line.startswith('System Model:'):
          systemModel = line[14:]
          if systemModel != 'System Product Name':
            self.__systemInformation['systemDetails'] += ' ' + systemModel
        if line.startswith('Processor:'):
          #clean up (R) and (TM) and extra spaces in the CPU name
          cpuName = line[11:]
          cpuName = cpuName.replace('(R)', '')
          cpuName = cpuName.replace('(TM)', '')
          cpuName = " ".join(cpuName.split())
          self.__systemInformation['cpuName'] = cpuName
        #break memory down into memoryString, memoryInMB (int), memoryInGB (int)
        if line.startswith('Memory:'):
          memoryString = line[8:]
          self.__systemInformation['memoryString'] = memoryString
          memoryInMB = int(memoryString[:-6])
          self.__systemInformation['memoryInMB'] = memoryInMB
          memoryInGB = round(memoryInMB / 1024)
          self.__systemInformation['memoryInGB'] = memoryInGB
        if line.startswith('Page File:'): self.__systemInformation['pageFile'] = line[11:]
        if line.startswith('DirectX Version:'): self.__systemInformation['directXVersion'] = line[17:]
        #stop when we hit the next "--------"... line
        if line.startswith('--------'): foundEnd = True
        if foundEnd: break
      #end if foundStart
    #end for fileLine in self.__filecontents
  #end ParseSystemInformation()

  def __ParseDxDiagNotes(self):
    """
    Parse the DxDiag Notes section of the file
    """
    #------------
    #DxDiag Notes
    #------------
    foundStart = False
    foundEnd = False
    skipNextLine = False
    for fileLine in self.__filecontents:
      if skipNextLine:
        skipNextLine = False
        continue
      line = fileLine.strip()
      if line == "DxDiag Notes": 
        foundStart = True
        skipNextLine = True
      if foundStart:
        #the next line after "DxDiag Notes" is "------------", so skip it
        if skipNextLine: continue
        colonPos = line.find(":")
        if colonPos > -1:
          noteLine = line.split(':')
          if noteLine[1].startswith(' There is a problem'): self.__dxErrorNotes.append(noteLine[1].strip())
        #stop when we hit the next "--------"... line
        if line.startswith('--------'): foundEnd = True
        if foundEnd: break
      #end if foundStart
    #end for fileLine in self.__filecontents
  #end ParseDxDiagNotes()
  
  def __ParseDisplayDevices(self):
    """
    Parse the Display Devices section of the file
    """
    #---------------
    #Display Devices
    #---------------
    foundStart = False
    foundEnd = False
    skipNextLine = False
    monitorNameFound = False
    monitorModelFound = False
    for fileLine in self.__filecontents:
      if skipNextLine:
        skipNextLine = False
        continue
      line = fileLine.strip()
      if line == "Display Devices": 
        foundStart = True
        skipNextLine = True
      if foundStart:
        #the next line after "Display Devices" is "------------", so skip it
        if skipNextLine: continue
        #need to deal with the situation where the Monitor Name and/or Monitor Model are missing
        if line.startswith('Card name:'):               #Card name: NVIDIA GeForce RTX 3080
          videoCardName = line[11:]
          self.__videoCardNames.append(videoCardName)
          #this also indicates the start of a new Video section, so reset the Name and Model found flags
          monitorNameFound = False
          monitorModelFound = False
        if line.startswith('Manufacturer:'):            #Manufacturer: NVIDIA
          videoCardManufacturerName = line[14:]
          self.__videoCardManufacturers.append(videoCardManufacturerName)
        if line.startswith('Dedicated Memory:'):        #Dedicated Memory: 10067 MB
          videoRAM = line[18:]
          end = videoRAM.find(" MB")
          if end > -1:
            self.__videoCardRAM.append(int(videoRAM[:end]))
          elif videoRAM == 'n/a':
            self.__videoCardRAM.append(0)
        if line.startswith('Current Mode:'):            #Current Mode: 2560 x 1440 (32 bit) (144Hz)
          displayMode = line[14:]
          self.__videoDisplayModes.append(displayMode)
        if line.startswith('Monitor Name:'):            #Monitor Name: Dell S2716DG(DisplayPort)
          monitorNameFound = True
          monitorName = line[14:]
          self.__monitorNames.append(monitorName)
        if line.startswith('Monitor Model:'):           #Monitor Model: Dell S2716DG
          monitorModelFound = True
          monitorModel = line[15:]
          self.__monitorModels.append(monitorModel)
        if line.startswith('Driver File Version:'):     #Driver File Version: 31.00.0015.2661 (English)
          videoDriverVersion = line[21:]
          self.__videoDriverVersions.append(videoDriverVersion)
        #'PanelFitter Stretch' is usually one of the last lines in a Video section.
        #if we have made it here and no Name or Model found, then just add 'unknown'
        if line.startswith('PanelFitter Stretch:'):
          if not monitorNameFound: self.__monitorNames.append('unknown')
          if not monitorModelFound: self.__monitorModels.append('unknown')
        #stop when we hit the next "--------"... line
        if line.startswith('--------'): foundEnd = True
        if foundEnd: break
      #end if foundStart
    #end for fileLine in self.__filecontents
  #end ParseDisplayDevices(self)

  def __AssembleVideoInfo(self):
    """
    video info is scattered in several lists; pull them all together to 1 list of dictionaries
    """
    for i in range(len(self.__videoCardNames)):
      #based on videoCardManufacturers, decode videoDriverVersions into common driver versions/names
      driverVersion = self.__videoDriverVersions[i]
      #Intel Corporation
      #(Standardgrafikkartentypen)
      #NVIDIA
      if self.__videoCardManufacturers[i].startswith('NVIDIA'): driverVersion = DecodeNVIDIADriverVersion(driverVersion)
      #Advanced Micro Devices, Inc.
      if self.__videoCardManufacturers[i].startswith('Advanced Micro'): driverVersion = DecodeAMDDriverVersion(driverVersion, self.__driverVersionsAMD)
      cardData = {
        'cardName': self.__videoCardNames[i],
        'cardManufacturer': self.__videoCardManufacturers[i],
        'VRAM': self.__videoCardRAM[i],
        'displayMode': self.__videoDisplayModes[i],
        'monitorName': self.__monitorNames[i],
        'monitorModel': self.__monitorModels[i],
        'driverVersion': driverVersion,
        'driverVersionRaw': self.__videoDriverVersions[i]
      }
      self.__videoDisplays.append(cardData)
  #end __AssembleVideoInfo()

  def __ParseSoundDevices(self, sectionName):
    """
    Parse the Sound Devices/Capture Devices section of the file
    """
    #-------------
    #Sound Devices -AND- Sound Capture Devices
    #-------------
    #parse the filecontents for the sectionName section
    foundStart = False
    foundEnd = False
    skipNextLine = False
    for fileLine in self.__filecontents:
      if skipNextLine:
        skipNextLine = False
        continue
      line = fileLine.strip()
      if line == sectionName: 
        foundStart = True
        skipNextLine = True
      if foundStart:
        #the next line after sectionName is "------------", so skip it
        if skipNextLine: continue
        if line.startswith('Description:'): self.__soundDevices.append(line[13:])
        #stop when we hit the next "--------"... line
        if line.startswith('--------'): foundEnd = True
        if foundEnd: break
      #end if foundStart
    #end for fileLine in self.__filecontents
  #end ParseSoundDevices(self)

  def __ParseDrives(self):
    """
    Parse the Disk & DVD/CD-ROM Drives section of the file
    """
    #------------------------
    #Disk & DVD/CD-ROM Drives
    #------------------------
    tempLines = []
    foundStart = False
    foundEnd = False
    skipNextLine = False
    for fileLine in self.__filecontents:
      if skipNextLine:
        skipNextLine = False
        continue
      line = fileLine.strip()
      if line == "Disk & DVD/CD-ROM Drives": 
        foundStart = True
        skipNextLine = True
      if foundStart:
        #the next line after "Disk & DVD/CD-ROM Drives" is "------------", so skip it
        if skipNextLine: continue
        #make a copy of the disk section to reparse
        if not line == '': tempLines.append(line)
        #stop when we hit the next "--------"... line
        if line.startswith('--------'): foundEnd = True
        if foundEnd: break
      #end if foundStart
    #end for fileLine in self.__filecontents
    #parse the tempLines list for the details
    #print(tempLines)
    driveDetails = {
      'driveLetter': '',
      'freeSpace': '',
      'totalSpace': '',
      'fileSystem': '',
      'model': ''
    }
    for i in range(len(tempLines)):
      if tempLines[i].startswith('Drive:'):
        driveDetails['driveLetter'] = tempLines[i][7]
        #determine if next line is "Free Space:"
        if tempLines[i+1].startswith('Free Space:'):
          driveDetails['freeSpace'] = tempLines[i+1][12:]
          driveDetails['totalSpace'] = tempLines[i+2][13:]
          driveDetails['fileSystem'] = tempLines[i+3][13:]
          driveDetails['model'] = tempLines[i+4][7:]
        else:
          #empty removable drive
          driveDetails['freeSpace'] = ''
          driveDetails['totalSpace'] = ''
          driveDetails['fileSystem'] = ''
          driveDetails['model'] = tempLines[i+1][7:]
        #MUST use .copy() in order to get the data, otherwise it is just a list of references to the single driveDetails dict
        self.__drives.append(driveDetails.copy())
      #end if tempLines[i].startswith('Drive:')
    #end for i in range(len(tempLines))
  #end ParseDrives()

  @property
  def drives(self):
    """
    Return a list of drive info dictionaries
    """
    return self.__drives

  @property
  def dxErrorCount(self):
    """
    Return an integer of the number of DXDiag errors
    """
    return len(self.__dxErrorNotes)

  @property
  def dxErrorNotes(self):
    """
    Return a list of strings of DXDiag errors
    """
    return self.__dxErrorNotes

  @property
  def filename(self):
    """
    Return a string listing the specified filename
    """
    return self.__filename

  @property
  def found(self):
    """
    Return a boolean if the specified file was found and loaded
    """
    return self.__found

  @property
  def soundDevices(self):
    """
    Return a list of strings of detected sound devices
    """
    return self.__soundDevices

  @property
  def systemInformation(self):
    """
    Return a dictionary of system information
    """
    return self.__systemInformation

  @property
  def videoDisplays(self):
    """
    Return a list of dictionaries of detected video devices
    """
    return self.__videoDisplays
