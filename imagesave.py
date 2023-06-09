### Package import ###

import numpy as np
from scipy import signal, fft
from scipy.io.wavfile import write
import pyaudio
from PIL import Image
import matplotlib.pyplot as plt
import os 
from pathlib import Path


### Defining functions ###

def my_fft(data):
    # Create an FFT of the image data
    data_fft = fft.rfft(data)

    # Create a list of positions
    positions = np.linspace(10, 22050, 22040)

    # Create the plot (x,y)
    plt.semilogx(positions, np.absolute(data_fft[10:22050]))

    # Add axis labels and title
    plt.xlabel('Frequency')
    plt.ylabel('Amplitude')
    plt.title('FFT')

    # Show the plot
    plt.show()

def raster_scan(image, bi_sel):
    # Get the dimensions of the image
    width, height = image.size

    # Create an array to store the pixel values
    pixel_values = []

    # Iterates through every horizontal pixel position, top to bottom
    for y in range(height):

        # If row is at an even index, traverse from left to right
        if (y+2) % 2 == 0 or ((y+2) % 2 == 1 and bi_sel == 2):
            
            # Iterates through each pixel in the row
            for x in range(width):
                pixel_value = image.getpixel((x, y))

                # Add the pixel 
                pixel_values.append(pixel_value) 

        # If odd index AND bidirectional = 1 (True), traverse right to left
        # This 'snaking' through the pixel rows is raster scanning
        else:
            for x in range(width):
                pixel_value = image.getpixel(((width-x-1), y))
                pixel_values.append(pixel_value)
    
    return pixel_values

def bidirectional_select():
    while True:

        try:
            bidir = int(input(
"""
-------------------------------------------------
Please select bidirectional (L->R then R->L)
or unidirectional (just L->R) raster scanning
-------------------------------------------------

1. Bidirectional
2. Unidirectional

-------------------------------------------------
Select 1/2
-------------------------------------------------

"""))

        # Validates user input is an integer  
        except ValueError:
            print("Please enter either 1 or 2.")
            continue
        
        # Validates that input is within desired range
        if bidir > 1 or bidir < 3:
            break
        else:
            pass

    return bidir

def normalise(data, max_min):
    # Find max and min values of all pixel colour data
    min_value = np.min(data)
    max_value = np.max(data)

    # Normalise pixel values between 0.95 and -0.95
    normalised_data = ((2 * (data - min_value) / (max_value - min_value)) - 1)*max_min

    # Validate the edge values to ensure no clipping will occur
    print(f"""MaxValue: {np.max(normalised_data)}
MinValue: {np.min(normalised_data)}""")

    return normalised_data

def fade_audio(unfaded_data):
    # Variable fade_length, 2400, is number of samples for fade in (50ms at 48kHz)
    fade_length = 2400

    # Create lists that go from 0 to 1 (fade in) or 1 to 0 (fade out)
    fade_multiplier = np.linspace(0, 1, fade_length)

    # Apply the fades to the audio data
    for i in range(0, fade_length, 1):

        # Image data
        unfaded_data[i] *= fade_multiplier[i]
        unfaded_data[-1-i] *= fade_multiplier[i] 

def my_plot(data, plot_name):
    # Create a list of positions
    positions = list(range(len(data)))

    # Create the plot (x,y)
    plt.plot(positions, data)

    # Add axis labels and title
    plt.xlabel('Sample No.')
    plt.ylabel('Amplitude')
    plt.title(f'{plot_name}')

    # Show the plot
    plt.show()



### Declaring parameters ###

dir_path = os.path.dirname(os.path.realpath(__file__))
sample_rate = 48000
channels = 1
format = pyaudio.paFloat32


### Image intake ###

# Open the image
img = Image.open(f'{dir_path}/Greyscale Images/rgb.png')
width, height = img.size

# Display information about the image
print(img.format)
print(img.mode)
print(img.size)

# Show the image
img.show()


### Image raster scanning ###

bi_select = bidirectional_select()
pixel_values = raster_scan(img, bi_select)   

# Using the normalise() function to scale the pixel data values appropriately
image_data = normalise(pixel_values, 0.95)

# Use the fade_audio() function to apply short fades
# at the start and the end to avoid any audible distortion
fade_audio(image_data)

### Sound synthesis ###

# Create a PyAudio object
p = pyaudio.PyAudio()

# Initialise the audio stream
stream = p.open(format=format,
                channels=channels,
                rate=sample_rate,
                output=True)

# Audition the image audio waveform
stream.write(image_data.astype(np.float32).tobytes())

# Plot the image waveform and FFT
my_plot(image_data, "Sonified Image Waveform")
my_fft(image_data)

write(f"{dir_path}/WAV Exports/{Path(img.filename).stem}.wav", sample_rate, image_data.astype(np.float32))
print(f"File saved as {Path(img.filename).stem}.wav")

# Close the stream and PyAudio object
stream.stop_stream()
stream.close()
p.terminate()