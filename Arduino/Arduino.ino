
#include <Servo.h>
#include <Wire.h>
#include <LCD.h>
#include <LiquidCrystal_I2C.h>

#define I2C_ADDR    0x3F // <<----- Add your address here.  Find it from I2C Scanner
#define BACKLIGHT_PIN     3
#define En_pin  2
#define Rw_pin  1
#define Rs_pin  0
#define D4_pin  4
#define D5_pin  5
#define D6_pin  6
#define D7_pin  7
LiquidCrystal_I2C  lcd(I2C_ADDR, En_pin, Rw_pin, Rs_pin, D4_pin, D5_pin, D6_pin, D7_pin);

Servo servo;

String numberplate = "";

void setup()
{
  Serial.begin(9600);
  servo.attach(9);
  servo.write(0);

  lcd.begin (16, 2);
  // Switch on the backlight
  lcd.setBacklightPin(BACKLIGHT_PIN, POSITIVE);
  lcd.setBacklight(HIGH);
}

void loop()
{
  if (Serial.available() > 0) {
    numberplate = Serial.readStringUntil('\n');

    lcd.clear();
    lcd.home ();
    lcd.print("Nummerplade:");
    lcd.setCursor(0, 1);
    lcd.print(numberplate);
    servo.write(90);
    delay(10000);
    servo.write(0);
    lcd.clear();
  }
  else {
    lcd.home ();
    lcd.print("Velkommen :D");
    lcd.setCursor(0, 1);
    lcd.print("Parkering.tk");
 
  }
}
