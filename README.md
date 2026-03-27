# Edge Heart Rate Monitor: PPG Signal Processing with ESP32 & FFT

A real-time heart rate monitoring system built on ESP32, featuring an end-to-end pipeline from hardware signal stabilization to on-chip frequency domain analysis.

## 🚀 Engineering Highlights
- **Hardware Optimization:** Custom 3D-printed stabilizer to mitigate motion artifacts.
- **Edge DSP:** Real-time 512-point FFT, DC removal, and Hamming Windowing implemented directly on ESP32.
- **Frequency Masking:** Bandpass filtering (0.8Hz - 2.2Hz) in the frequency domain to isolate physiological signals from noise.

## 📁 Repository Structure
- `firmware/`: C++ source code for ESP32.
- `notebooks/`: Offline Python analysis and algorithm validation.
- `scripts/`: Real-time data visualization and logging tool.
- `data/`: Sample datasets.
- `docs/`: Technical report and hardware photos.

## 📊 Performance
- **Sampling Rate:** 100Hz (Fixed via `micros()`).
- **Accuracy:** Stable heart rate extraction with ~0.066Hz resolution.
