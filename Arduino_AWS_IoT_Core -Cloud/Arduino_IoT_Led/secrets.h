
#include <pgmspace.h>
 
#define SECRET
#define THINGNAME "ESP32-#"                         //change this
 
const char WIFI_SSID[] = "androidSebPro";               //change this
const char WIFI_PASSWORD[] = "123456789";           //change this
const char AWS_IOT_ENDPOINT[] = "a2hb1w86de6tcr-ats.iot.ap-southeast-2.amazonaws.com";

//clientID: device-#
//port:8883     

//topics
//"ESP32bootcamp_com"
//"ESP32bootcamp_control"
 
// Amazon Root CA 1
static const char AWS_CERT_CA[] PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----

-----END CERTIFICATE-----
)EOF";
 
// Device Certificate                                               //change this
static const char AWS_CERT_CRT[] PROGMEM = R"KEY(
-----BEGIN CERTIFICATE-----

-----END CERTIFICATE-----
)KEY";
 
// Device Private Key                                               //change this
static const char AWS_CERT_PRIVATE[] PROGMEM = R"KEY(
-----BEGIN RSA PRIVATE KEY-----

-----END RSA PRIVATE KEY-----
 
)KEY";