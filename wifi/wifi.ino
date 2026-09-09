#include <WiFi.h>
#include <WiFiUdp.h>

// ---------- تنظیمات وای‌فای ----------
const char* ssid = "TP-Link";
const char* password = "ESP32 WiFi Server";

// ---------- آی‌پی ثابت (Static IP) ----------
// این‌ها را با تنظیمات شبکه خودتان تطبیق دهید (بر اساس رنج 192.168.1.x)
IPAddress local_IP(192, 168, 1, 150);   // آی‌پی ثابتی که همیشه همین می‌ماند
IPAddress gateway(192, 168, 1, 1);      // آی‌پی روتر شما (معمولاً همین است)
IPAddress subnet(255, 255, 255, 0);

WiFiUDP udp;
unsigned int localPort = 4210;
char incomingPacket[64];

// ---------- پین‌های درایور L298N ----------
#define IN1 13
#define IN2 12
#define IN3 14
#define IN4 27

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  stopMotors();

  // تنظیم آی‌پی ثابت قبل از اتصال
  if (!WiFi.config(local_IP, gateway, subnet)) {
    Serial.println("خطا در تنظیم IP ثابت");
  }

  WiFi.begin(ssid, password);
  WiFi.setSleep(false);
  Serial.print("در حال اتصال به وای‌فای");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print(">>> متصل شد! آی‌پی ثابت: ");
  Serial.println(WiFi.localIP());

  udp.begin(localPort);
  Serial.printf(">>> در حال گوش دادن روی پورت %d\n", localPort);
}

void loop() {
  // اگر وای‌فای قطع شد، دوباره وصل شو
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println(">>> اتصال قطع شد! تلاش مجدد...");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    Serial.println(">>> دوباره متصل شد!");
  }

  int packetSize = udp.parsePacket();
  if (packetSize > 0) {
    int len = udp.read(incomingPacket, sizeof(incomingPacket) - 1);
    if (len > 0) incomingPacket[len] = 0;

    int code = atoi(incomingPacket);
    Serial.print("کد دریافتی: ");
    Serial.println(code);

    handleCommand(code);
  }
}

void handleCommand(int code) {
  if (code == 10 || code == 9 || code == 11) {
    moveForward();
  }
  else if (code == 15 || code == 16 ) {
    moveBackward();
  }
  else if (code == 6) {
    stopMotors();
  }
  else if (code == 0 || code == 1 || code == 2 || code == 3) {
    moveLeft();
  }
  else if (code == 12 || code == 13 || code == 14) {
    moveRight();
  }
}

void moveForward() {
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
}

void moveBackward() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
}

void moveLeft() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
}

void moveRight() {
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
}

void stopMotors() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
}