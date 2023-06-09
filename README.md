# image-sonification-synthesis
**BSc Sound Engineering Final Project**
This algorithm will take a digital image input, extract a signal from it and map it into the audio domain.
This signal can be used for sound synthesis purposes.
Currently, the idea is to apply this algorithm creatively by using a fingerprint scan as the digital image input. This provides unique input for any user and allows the user to create their **'own sound'**.

This repository will be continually updated as I progress with the code design and implementation.



9th June 2023

The research project has concluded and the result is two Python implementations:
main.py (1) takes in image input, raster scans its pixel data and converts this data into a format analogous to digital audio, and convolves it with a typical audio waveform (sine/square/sawtooth) to synthesise sound;
imagesave.py (2) does the same as main.py, but does not convolve with other audio. It simply saves the synthesised audio of an image to a WAV file in the 'WAV Exports' folder. imagesave.py was used in combination with GIMP to explore the effects on resultant audio when the original image was tiled 3x3 and transformed. The transformations used were reflection, rotation, and translation.

In the end, this research project quickly moved away from scanning a fingerprint to allow the user to generate an image to be sonified. By purely focusing on the software, this research project was allowed to flourish and develop past the original scope set out.
