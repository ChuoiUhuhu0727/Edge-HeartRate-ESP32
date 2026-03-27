#include <Arduino.h>
#include <Wire.h>
#include "MAX30105.h"
#include "arduinoFFT.h"

// --- 1. CONFIGURATION (Phải đặt ở trên cùng) ---
#define I2C_SDA 11
#define I2C_SCL 12
const uint16_t SAMPLES = 512;          // Định nghĩa SAMPLES trước
const double SAMPLING_FREQUENCY = 100; // Tần số lấy mẫu 100Hz

// --- 2. GLOBAL VARIABLES (Khai báo mảng dựa trên SAMPLES) ---
MAX30105 sensor;
ArduinoFFT<double> FFT = ArduinoFFT<double>();

double vReal[SAMPLES];
double vImag[SAMPLES];
uint16_t sampleIndex = 0;
unsigned long microseconds;

// --- 3. HÀM XỬ LÝ (HR_EXTRACT) ---
double HR_EXTRACT() {
  // Step 1: Remove DC (Subtract the mean)
  double mean = 0;
  for (int i = 0; i < SAMPLES; i++) mean += vReal[i];
  mean /= SAMPLES;
  for (int i = 0; i < SAMPLES; i++) {
    vReal[i] -= mean;
    vImag[i] = 0; // Reset phần ảo về 0
  }

  // Step 2: Windowing
  FFT.windowing(vReal, SAMPLES, FFT_WIN_TYP_HAMMING, FFT_FORWARD);

  // Step 3: Compute FFT
  FFT.compute(vReal, vImag, SAMPLES, FFT_FORWARD);
  FFT.complexToMagnitude(vReal, vImag, SAMPLES);

  // Step 4: Frequency Masking (Chỉ giữ vùng 0.8Hz - 2.2Hz)
  for (int i = 0; i < (SAMPLES / 2); i++) {
    double freq = (i * SAMPLING_FREQUENCY) / SAMPLES;
    if (freq < 0.8 || freq > 2.2) { 
      vReal[i] = 0; 
    }
  }

  // Step 5: Find Peak
  double peakFreq = FFT.majorPeak(vReal, SAMPLES, SAMPLING_FREQUENCY);
  return peakFreq * 60.0;
}

void setup() {
  Serial.begin(115200);
  Wire.begin(I2C_SDA, I2C_SCL);
  if (!sensor.begin(Wire, I2C_SPEED_STANDARD)) {
    Serial.println("MAX30102 not found!");
    while (1);
  }
  sensor.setup();
  sensor.setPulseAmplitudeRed(0x0A);
  sensor.setPulseAmplitudeIR(0x1F);
  microseconds = micros();
}

void loop() {
  if (sampleIndex < SAMPLES) {
    // Đảm bảo lấy mẫu đúng 100Hz dùng micros()
    if (micros() - microseconds >= 10000) {
      microseconds = micros();
      
      long irValue = sensor.getIR();
      if (irValue > 50000) { // Finger detected
        vReal[sampleIndex] = (double)irValue;
        vImag[sampleIndex] = 0;
        sampleIndex++;
      } else {
        sampleIndex = 0; // Nhấc tay thì reset buffer
      }
    }
  } else {
    // Khi đã đủ 512 mẫu, tiến hành tính toán
    double bpm = HR_EXTRACT();
    
    if (bpm > 40 && bpm < 150) {
      Serial.print("Stable Heart Rate: ");
      Serial.print(bpm);
      Serial.println(" BPM");
    }

    sampleIndex = 0; // Reset để lấy mẻ dữ liệu tiếp theo
  }
}