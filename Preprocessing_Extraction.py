import numpy as np

# Specify the file name
filename = "HackRF-20230718_193740-2_4GHz-20MSps-20MHz.complex16s"

# Read the complex numbers from the file as float64 values: 32bit + 32 bit = 64 bit
complex_data = np.fromfile(filename, dtype=np.complex64)


# Extract the real and imaginary parts as float32 arrays
real_part = complex_data.real.astype(np.float32)
imaginary_part = complex_data.imag.astype(np.float32)

# ignore the nan value; prevent it result in calculation error
mask = np.isnan(real_part)
real_part_without_nan = real_part[~mask]
maks = np.isnan(imaginary_part)
imaginary_part_without_nan = imaginary_part[~mask]

# floats in scientific notation: only save the real number part
real_numbers = np.asarray([float(f"{val:e}".split('e')[0]) for val in real_part_without_nan])

# rms normalization
rms = np.sqrt(np.mean(real_numbers**2))
real_numbers = real_numbers / rms

