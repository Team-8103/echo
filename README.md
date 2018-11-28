# GEORGIA TECH HEATING VENTILATION AIR CONDITIONING ALEXA SKILL

This Alexa Dot Skill was created to handle basic smart home commands in association with GTHousing. The intent_schema gives an example of what phrases activate which intents, while main.py goes through and handles those intents. The backend is handled by outside sources such as GT and JC, our application handles the front of end of word parsing and assigning the intent of each command. The Lambda Handler looks at the incoming request and assigns it to its respective intent, and each intent tells Alexa how to react/handle it.

## Install Guide
### Installing the Alexa Skill
You can “Ask GT Housing” questions with the Georgia Tech Housing  Skill. Once you’ve downloaded the Amazon Alexa app on your phone, you can enable the Georgia Tech skill in 3 steps...
1. Set Up Your Echo Dot
    In the Alexa app, select “Set Up A New Device” in Settings and follow the steps. When prompted to select your Wi-Fi network, choose GTother and use the password found at auth.lawn.gatech.edu/key. This Echo Dot has been pre-registered so you will only have to enter this information once during initial setup.
2. Enable the Skill
    In the Alexa app, select “Skills” and search for Georgia Tech Housing. Select “Enable”. Accept “Terms and Conditions”.
3. Link Your GT Account
    In the Alexa app, open the menu and go to “Skills”. Then select “Your Skills” in the upper right corner. Open the Georgia Tech Housing skill and tap “Settings” to enter your GT Account username and password and log in. Now, use the app by saying something like, “Alexa, ask GT Housing to turn the temperature to 74 degrees.”

For troubleshooting tips, visit the [Amazon Help Desk](https://www.amazon.com/gp/help/customer/display.html) or [Alexa skills and games](https://www.amazon.com/gp/help/customer/display.html/ref=hp_bc_nav?ie=UTF8&nodeId=202013760).

### Downloading the Code
Clone the public repository

```commandline
git clone https://github.com/Team-8103/echo.git
```

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies
```commandline
pip install -r requirements.txt
```

Need the passcodes to make the code run? Email malte.weiland@housing.gatech.edu

Passcodes needed:
* BuzzAPI -> Used to find user's GT Residence Hall and Room Number
* AWS Account Public and Secret Key -> Used to send data to the DynamoDB

### Testing your Code
You can find example Alexa Intents to test the code in the [Amazon Developer Docs](https://developer.amazon.com/docs/custom-skills/request-and-response-json-reference.html).

It is best to run this code in an AWS Lambda Function.
There are two Lambda Functions that make this skill work:

Function  | Function Handler | Trigger
------------- | ------------- | -------------
[main.py](main.py)  | main.handler | Alexa Skills Kit
[auth.py](auth.py)  | auth.handler | API Gateway

## Using the Alexa Skill
Here are a sample list of commands you can use with the Alexa Skill. For an exhaustive list, checkout [intent_schema.json](intent_schema.json)

* Change the Temperature
    * Alexa, ask GT Housing to change the temperature to seventy degrees
    * Alexa, ask GT Housing to turn it up to eighty-four degrees
    * Alexa, ask GT Housing to set the temperature to sixty

* Change the Lights
    * Alexa, ask GT Housing to turn the lights off
    * Alexa, ask GT Housing to turn the lights on

* State the Temperature
    * Alexa, ask GT Housing what the temperature is
    * Alexa, ask GT Housing what temperature it is

## Release Notes
 - [x] Build backbone of Alexa Skill
 - [x] Intent Schema with utterances [link](intent_schema.json)
 - [x] Find room/building number through GT Buzz API [link](main.py#L92)
 - [x] Authenticate Georgia Tech users through GT CAS
    - [ ] Currently in contact with [Stephen Garrett](mailto:stephen.garrett@itg.gatech.edu) of OIT's ITG to get GT CAS to work with this Alexa Skill.
 - [ ] Connect to the Johnson Controls Metasys Database
 - [ ] Have different situations allowed if the user is in a room with a thermostat versus a room with a fan
 - [ ] Check if a user is living in a Georgia Tech Dorm before trying to change the temperature - If BuzzAPI fails to find the field gtCurrentDormResidence of a user, then they are not a Georgia Tech Housing resident.

[Known Bugs](https://github.com/Team-8103/echo/issues)


## Authors
* Aadarsh Padiyath
* L Samuel Cook
* Jack Lafiandra
* Philip Carpenter
* Vijay Upadhya

## Client
* [Malte Weiland](mailto:malte.weiland@housing.gatech.edu)
