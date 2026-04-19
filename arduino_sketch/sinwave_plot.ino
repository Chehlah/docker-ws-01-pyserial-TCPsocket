// Arduino Uno - Sine Wave Generator
// Amplitude: ±10, Loop delay: 200ms

#include <math.h>

float angle = 0.0;
const float AMPLITUDE = 10.0;
const float STEP = 0.2;  // radians per step (~11.5 degrees)
const int DELAY_MS = 200;

void setup() {
  Serial.begin(9600);
  Serial.println("Sine Wave Output (Amplitude: ±10)");
  Serial.println("angle_rad,value");
}

void loop() {
  float value = AMPLITUDE * sin(angle);

  // ส่งค่าออก Serial (CSV format สำหรับ Serial Plotter)
  //Serial.print(angle, 3);
  //Serial.print(",");
  Serial.println(value, 2);

  angle += STEP;

  // รีเซ็ต angle เมื่อครบ 1 รอบ (2π) เพื่อป้องกัน float overflow
  if (angle >= TWO_PI) {
    angle -= TWO_PI;
  }

  delay(DELAY_MS);
}