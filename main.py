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

def waveform_select():
    while True:

        try:
            waveform = int(input(
"""
-------------------------------------------------
Please select a waveform for the oscillator
-------------------------------------------------

1. Sine wave
2. Square wave
3. Sawtooth wave

-------------------------------------------------
Select 1/2/3
-------------------------------------------------

"""))

        # Validates user input is an integer  
        except ValueError:
            print("Please enter an integer between 1 and 3.")
            continue
        
        # Validates that input is within desired range
        if waveform > 3 or waveform < 1:
            pass
        else:
            break

    return waveform

def frequency_select():
    while True:

        try:
            osc_freq = int(input(
"""
-------------------------------------------------
Please input a frequency value in Hertz for the
oscillator between 10Hz and 22,000Hz.
-------------------------------------------------

"""))
            
        except ValueError:
            print("Please enter an integer between 10 and 22,000.")
            continue
        
        if osc_freq > 22000 or osc_freq < 10:
            pass
        else:
            break

    return osc_freq

def duration_select():
    osc_duration = width*height
    return osc_duration

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

def sine_gen(audio_rate, f, l):
    # Create time values
    t = np.linspace(0, l/audio_rate, l, dtype=np.float32)

    # Generate y values for signal
    y = np.sin(2 * np.pi * f * t)

    # Returns a sine waveform of the desired frequency and duration
    return y

def square_gen(audio_rate, f, l):
    # Create time values   
    t = np.linspace(0, l/audio_rate, l, dtype=np.float32)

    # Generate y values for signal
    y = signal.square(2 * np.pi * f * t)

    # Returns a square waveform of the desired frequency and duration
    return y

def saw_gen(audio_rate, f, l):
    # Create time values   
    t = np.linspace(0, l/audio_rate, l, dtype=np.float32)

    # Generate y values for signal
    y = signal.sawtooth(2 * np.pi * f * t)

    # Returns a sawtooth waveform of the desired frequency and duration
    return y


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

# Waveform selection
wf = waveform_select()

# Oscillator frequency selection
osc_f = frequency_select()

# Oscillator duration selection
osc_d = duration_select()

# Select the function to generate the chosen waveform
if wf == 1:
    osc_signal = sine_gen(sample_rate, osc_f, osc_d)
    wf_type = "Sine Wave"

elif wf == 2:
    osc_signal = square_gen(sample_rate, osc_f, osc_d)
    wf_type = "Square Wave"

else:
    osc_signal = saw_gen(sample_rate, osc_f, osc_d)
    wf_type = "Sawtooth Wave" 

fade_audio(osc_signal)
stream.write(osc_signal.astype(np.float32).tobytes())
my_plot(osc_signal, "Oscillator Waveform")
my_fft(osc_signal)



# Create a convolution of the image and oscillator signal
conv_signal = signal.convolve(osc_signal, image_data)

# Normalise it
conv_signal = normalise(conv_signal, 0.95)

# Apply fades
fade_audio(conv_signal)
# Audition the convolved audio 
stream.write(conv_signal.astype(np.float32).tobytes())
# Plot the waveform and FFT
my_plot(conv_signal, "Image/Oscillator Convolution Waveform")
my_fft(conv_signal)




# Exit condition for looping menu
quit = False

while quit == False:
    while True:
        # Menu allows user to: view details about the image and the oscillator,
        # modify them, audition the audio they have synthesised, save the 
        # audio they have created to file, or quit the program.
        try:
            select = int(input(
f"""
-------------------------------------------------
Modify IMG/OSC parameters, audition the convolved
audio, export audio, or quit.
-------------------------------------------------

1. Modify IMG/OSC parameters
2. Audition convolved audio
3. Export audio
4. Quit

-------------------------------------------------
Select 1/2/3/4
-------------------------------------------------
Current IMG/OSC Parameters
-------------------------------------------------

IMG   Name      : {Path(img.filename).stem}
      Format    : {img.format}
      Dimensions: {width}x{height}
      Pixels    : {osc_d}
      Duration  : {round(osc_d/sample_rate, 2)} seconds (2 d.p.)

OSC   Waveform  : {wf_type}
      Frequency : {osc_f} Hz
      Samples   : {osc_d}
      Duration  : {round(osc_d/sample_rate, 2)} seconds (2 d.p.)

-------------------------------------------------

"""))

        # Validates user input is an integer  
        except ValueError:
            print("Please enter an integer between 1 and 4.")
            continue
        
        # Validates that input is within desired range
        if select > 4 or select < 1:
            pass
        else:
            break
    
    # Parameter modify menu
    if select == 1:
        while True:

            try:
                param_select = int(input(
f"""
-------------------------------------------------
Please select a parameter to modify
-------------------------------------------------

1. Select new image
2. Select oscillator waveform
3. Select oscillator frequency

-------------------------------------------------
Select 1/2/3
-------------------------------------------------
Current IMG/OSC Parameters
-------------------------------------------------

IMG   Name      : {Path(img.filename).stem}
      Format    : {img.format}
      Dimensions: {width}x{height}
      Pixels    : {osc_d}
      Duration  : {round(osc_d/sample_rate, 2)} seconds (2 d.p.)

OSC   Waveform  : {wf_type}
      Frequency : {osc_f} Hz
      Samples   : {osc_d}
      Duration  : {round(osc_d/sample_rate, 2)} seconds (2 d.p.)

-------------------------------------------------

"""))

            # Validates user input is an integer  
            except ValueError:
                print("Please enter an integer between 1 and 3.")
                continue
            
            # Validates that input is within desired range
            if param_select > 3 or param_select < 1:
                pass
            else:
                break
        
        # Select new image
        if param_select == 1:
            while True:

                try: img_select = input("""
Please place the image you want to sonify in the same directory as main.py
Type the full name of the image, i.e 'gradient.png': """)

                except FileNotFoundError:
                    print("File not found.")
                
                if os.path.isfile(f'{dir_path}/Greyscale Images/{img_select}'):
                    print('File found.')
                    break

                else:
                    print("File not found. Please make sure the correct file name is entered.")

            img = Image.open(f'{dir_path}/Greyscale Images/{img_select}')
            img.show()
            width, height = img.size
            osc_d = duration_select()
            bi_select = bidirectional_select()
            pixel_values = raster_scan(img, bi_select)   
            image_data = normalise(pixel_values, 0.95)
            fade_audio(image_data)
            stream.write(image_data.astype(np.float32).tobytes())
            my_plot(image_data, "Sonified Image Waveform")
            my_fft(image_data)


        else:
            # Select waveform
            if param_select == 2:
                wf = waveform_select()

            # Select oscillator frequency
            else:
                osc_f = frequency_select()

            if wf == 1:
                osc_signal = sine_gen(sample_rate, osc_f, osc_d)
                wf_type = "Sine_Wave"

            elif wf == 2:
                osc_signal = square_gen(sample_rate, osc_f, osc_d)
                wf_type = "Square_Wave"

            else:
                osc_signal = saw_gen(sample_rate, osc_f, osc_d)
                wf_type = "Sawtooth_Wave" 

            fade_audio(osc_signal)
            stream.write(osc_signal.astype(np.float32).tobytes())
            my_plot(osc_signal, "Oscillator Waveform")
            my_fft(osc_signal)

        # Create a new convolution of the image and oscillator signal
        conv_signal = signal.convolve(osc_signal, image_data)
        conv_signal = normalise(conv_signal, 0.95)
        fade_audio(conv_signal)

    # Audition convolved audio
    elif select == 2:
        stream.write(conv_signal.astype(np.float32).tobytes())
        my_plot(conv_signal, "Image/Oscillator Convolution Waveform")
        my_fft(conv_signal)  

    # Save convolved audio to file
    elif select == 3:
        write(f"{dir_path}/WAV Exports/{Path(img.filename).stem}_{wf_type}_{osc_f}Hz_{round(osc_d/sample_rate*2,2)}s.wav", sample_rate, conv_signal.astype(np.float32))
        print(f"File saved as {Path(img.filename).stem}_{wf_type}_{osc_f}Hz_{round(osc_d/sample_rate*2,2)}s.wav")

    # Quit
    else:
        quit = True
        print("Shutting down...")

# Close the stream and PyAudio object
stream.stop_stream()
stream.close()
p.terminate()