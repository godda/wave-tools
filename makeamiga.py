# Makeamiga
# For Python 3
# By Zoe Blade

# Converts mono .wav files into mono 8-bit 8363Hz .pcm files

import math # For floor
import struct # For converting the (two's complement?) binary data to integers
import sys # For command line arguments
import wave # For .wav input and output

# Set sensible defaults
inputFilenames = []

for argument in sys.argv:
	if (argument[-4:].lower() == '.wav'):
		inputFilenames.append(argument)

if (len(inputFilenames) == 0):
	print("Please specify which .wav files you would like to convert.")
	exit()

# Cycle through files
for inputFilename in inputFilenames:
	outputFilename = inputFilename[:-4] + '.pcm'

	try:
		inputFile = wave.open(inputFilename, 'r')
	except:
		print(inputFilename, "doesn't look like a valid .wav file.  Skipping.")
		continue

	if (inputFile.getnchannels() != 1):
		print(inputFilename, "isn't mono.  Skipping.")
		continue

	sampleResolution = inputFile.getsampwidth()

	if (sampleResolution != 1 and sampleResolution != 2 and sampleResolution != 3):
		print(inputFilename, "is neither 8-bit, 16-bit nor 24-bit.  Skipping.")
		continue

	try:
		outputFile = open(outputFilename, 'wb')
	except:
		print("I couldn't write to", outputFilename, "Skipping.")
		continue

	sampleFrequency = inputFile.getframerate()

	# Make lookup table
	whenToTakeASample = []
	lastAmigaQualitySample = -1

	for originalQualitySample in range(sampleFrequency):
		currentAmigaQualitySample = math.floor(originalQualitySample / sampleFrequency * 8363)

		if (currentAmigaQualitySample > lastAmigaQualitySample):
			whenToTakeASample.append(1)
			lastAmigaQualitySample = currentAmigaQualitySample
		else:
			whenToTakeASample.append(0)

	inputSamples = 0
	outputSamples = 0

	for iteration in range (0, inputFile.getnframes()):
		datumAsBinary = inputFile.readframes(1)
		inputSamples = inputSamples + 1

		if (inputSamples == sampleFrequency):
			inputSamples = 0

		if (whenToTakeASample[inputSamples] == 0):
			continue

		outputSamples = outputSamples + 1

		if (outputSamples > 64000):
			# Scream Tracker has a maximum sample size of 64000
			continue

		if (sampleResolution == 3):
			datumAsInteger = struct.unpack('<3b', datumAsBinary)
			datumAsInteger = int(datumAsInteger[2]) # Ignore all but the most significant byte
		elif (sampleResolution == 2):
			datumAsInteger = struct.unpack('<2b', datumAsBinary)
			datumAsInteger = int(datumAsInteger[1]) # Ignore all but the most significant byte
		else:
			datumAsInteger = struct.unpack('<b', datumAsBinary)
			datumAsInteger = int(datumAsInteger[0])

		datumAsBinary = struct.pack('<B', datumAsInteger + 128)
		outputFile.write(datumAsBinary)

	inputFile.close()
	outputFile.close()
	print(inputFilename, "converted to", outputFilename)
