#!/usr/bin/python

#
# This tool is a very simple re-engineered version of the Panasonic LUMIX Map Tool.
#
# It may be used for copying detailed geographic data to the camera's SD card from
# the CD-ROM / DVD supplied with your DMC-TZ30 Series or DMC-TZ40 Series digital camera.
#
#
# Usage:
#
#  python maptool.py
#
#
# Authors: Roland Kluge          http://blog.roland-kluge.de/?p=250
#          Andrew Freemantle     http://www.fatlemon.co.uk/lumix-map-tool
#


import os
import re
import sys
import shutil

# defaults
MAP_LIST_FILENAME = 'MapList.dat'
LUMIX_MODELS = [
  ['DSC-TZ3x Series', 'PRIVATE/MAP_DATA/'],
  ['DSC-TZ4x Series', 'PRIVATE/PANA_GRP/PAVC/LUMIX/MAP_DATA/']
]
REGIONS = [
  [1, 'Japan'],
  [2, 'South Asia, Southeast Asia'],
  [3, 'Oceania'],
  [4, 'North America, Central America'],
  [5, 'South America'],
  [6, 'Northern Europe'],
  [7, 'Eastern Europe'],
  [8, 'Western Europe'],
  [9, 'West Asia, Africa'],
  [10, 'Russia, North Asia'],
]


def main():

  printWelcomeMessage()

  lumixModel = getLumixModel()

  mapDataLocation = getMapDataLocation()

  sdCardLocation = getSDCardLocation(lumixModel)

  printRegionList()

  regionToCopy = '0'
  while regionToCopy != '':
    regionToCopy = raw_input('Which maps do you want? (number, \'a[ll]\', \'?\' for list, or [enter] to quit): ')

    # is the region valid?
    try:
      regionToCopy = int(regionToCopy)

      if regionToCopy in range(1,11):
        copyMapData(regionToCopy, mapDataLocation, sdCardLocation)
    except ValueError:
      if regionToCopy in ('a', 'al', 'all'):
        for region in range(1,11):
          copyMapData(region, mapDataLocation, sdCardLocation)
      elif regionToCopy in ('q', 'quit'):
        # allow 'q' to quit as well
        regionToCopy = ''
      elif regionToCopy != '':
        printRegionList()

  print('Done, thank you  :o)')



def printWelcomeMessage():
  print('\nLUMIX Map Tool - Open Source edition  :o)\n')
  print('This tool will copy the Map Data from the CD-ROM / DVD that')
  print('accompanied your Panasonic LUMIX TZ30 / TZ40 Series digital camera')
  print('to your SD Card.\n')
  print('For more information please visit: http://www.fatlemon.co.uk/lumix-map-tool\n')



def getLumixModel():
  choices = ''
  for i, model in enumerate(LUMIX_MODELS):
    print(str(i) + ': ' + model[0])
    if len(choices) > 0:
      choices += ', '
    choices += str(i)

  lumixModel = 0
  lumixModelInput = 'invalid'
  while lumixModelInput == 'invalid':
    lumixModelInput = raw_input('Which LUMIX camera do you have? (' + choices + '): ')

    try:
      lumixModel = int(lumixModelInput)

      if lumixModel not in range(0, len(LUMIX_MODELS)):
        # input is invalid, ask the user again
        lumixModelInput = 'invalid'

    except ValueError:
      lumixModelInput = 'invalid'

  return LUMIX_MODELS[lumixModel]



def getMapDataLocation():
  isLocationOK = False
  mapDataLocation = ''
  while not isLocationOK:
    mapDataLocation = raw_input('Where\'s the Map Data? (e.g. \'/media/dvd/MAP_DATA\'): ')

    # check the path exists
    if not os.path.exists(mapDataLocation):
      print('Hmm.. that location doesn\'t exist, please try again..')
    elif not os.path.isfile(os.path.join(mapDataLocation, MAP_LIST_FILENAME)):
      print('Hmm.. couldn\'t find \'' + MAP_LIST_FILENAME + '\' in that location, please try again')
    else:
      isLocationOK = True

  return mapDataLocation



def getSDCardLocation(lumixModel):
  isLocationOK = False
  sdCardLocation = ''
  while not isLocationOK:
    sdCardLocation = raw_input('And where\'s your SD Card? (e.g. \'/media/sdcard\'): ')

    # check the path exists
    if not os.path.exists(sdCardLocation):
      print('Hmm.. that SD Card doesn\'t exist, please try again..')
    else:
      isLocationOK = True

  # append the sub-directory location based on the LUMIX Model
  sdCardLocation = os.path.join(sdCardLocation, lumixModel[1])

  # is there any Map Data already on the card?
  try:
    if os.listdir(sdCardLocation):
      # Map Data exists, ask if it should be removed..
      emptyExistingLocation = raw_input('Got it, but the map data folder isn\'t empty, clear it? (y,n - default): ')
      if emptyExistingLocation.startswith('y') | emptyExistingLocation.startswith('Y'):
        shutil.rmtree(sdCardLocation)
        print(' > cleared: ' + sdCardLocation)
  except OSError:
    pass    # directory doesn't exist, which is fine so nothing to do here

  # ensure the destination directory exists before we return
  try:
    os.makedirs(sdCardLocation)
  except OSError:
    pass    # directory exists, which is fine so nothing to do here   

  return sdCardLocation



def printRegionList():
  for region in REGIONS:
    print(str(region[0]).ljust(2) + ': ' + region[1])



def copyMapData(regionToCopy, mapDataLocation, sdCardLocation):
  # read the MapData.dat file
  mapListLines = open(os.path.join(mapDataLocation, MAP_LIST_FILENAME), 'r').readlines()

  mapData = []
  currentRegion = -1

  # load the information from the MapList.dat file into an
  #  easily searchable list by Region
  for line in mapListLines:
    line = line.strip()
    if re.match('^\d\d$', line):
      # i.e. line looks like "01" then we have a new Region
      currentRegion = int(line)
    elif re.match('^[^{}]', line):
      # i.e. line is not a curly bracket "{" or "}"
      # which means it's a file needed for the current Region
      mapData.append([currentRegion, line])
    # else ignored
  
  # pull out just the files needed for the region we want to copy
  matches = (l for l in mapData if l[0] == regionToCopy)
  sys.stdout.write(' > copying ')
  count = 0
  copyErrors = False
  for match in matches:
    # make sure the destination sub directory exists
    subdir, filename = match[1].split("/")
    destination = os.path.join(sdCardLocation, subdir)

    if not os.path.exists(destination):
      try:
        os.mkdir(destination)
      except:
        pass  # ignore any error and try to copy the file anyway

    # copy the file..
    try:
      shutil.copy(os.path.join(mapDataLocation, match[1]), destination)
      sys.stdout.write('.')
    except (OSError, IOError):
      sys.stdout.write('X')
      copyErrors = True
    sys.stdout.flush()
    count += 1

  if copyErrors:
    print(' ERROR: Sorry, there was a problem copying files')
  else:
    print(' done (' + str(count) + ' files)')



main()

