from __future__ import print_function


def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "ChangeIntent":
        return changeIntent(intent, session)
    elif intent_name == "StateIntent":
        return stateIntent(intent, session)
    elif intent_name == "LightsIntent":
        return lightsIntent(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response(intent, session)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response(intent, session):
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = getAttributes(intent, session)
    card_title = "Welcome"
    speech_output = "Welcome to Georgia Tech Housing's Alexa Skill. " \
                    "Please tell me what temperature you want this room to be " \
                    "by saying, change the temperature to 67 " \
                    "or something similar."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me what temperature you want this room to be " \
                    "by saying, change the temperature to 67 " \
                    "or something similar."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def changeIntent(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = getAttributes(intent, session)
    should_end_session = False

    if 'temperature' in intent['slots']:
        temperature = intent['slots']['temperature']['value']
        if int(temperature) < 90:
            if int(temperature) > 50:
                session_attributes["temperature"] = temperature
                speech_output = "I will now change the temperature to " + \
                                temperature + " degrees."
                reprompt_text = speech_output
            else:
                temperature = "50"
                session_attributes["temperature"] = temperature
                speech_output = "The minimum temperature allowed is" \
                " 50 degrees. I will now change the temperature to " + \
                            temperature + " degrees."
                reprompt_text = speech_output
        else:
            temperature = "90"
            session_attributes["temperature"] = temperature
            speech_output = "The maximum temperature allowed is"\
            " 90 degrees. I will now change the temperature to " + \
                        temperature + " degrees."
            reprompt_text = speech_output
    else:
        speech_output = "I'm not sure what you are asking. " \
                        "Please try again."
        reprompt_text = "I'm not sure what you are asking. " \
                        "Please try again."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def lightsIntent(intent, session):
    """ Sets the light in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = getAttributes(intent, session)
    should_end_session = False

    if 'power' in intent['slots']:
        power = intent['slots']['power']['value']
        session_attributes["power"] = power
        speech_output = "I am now turning the lights " + \
                        power + "."
        reprompt_text = speech_output
    else:
        speech_output = "I'm not sure what you are asking. " \
                        "Please try again."
        reprompt_text = "I'm not sure what you are asking. " \
                        "Please try again."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def create_temperature_attribute(temperature):
    return {"temperature": temperature}
    
def create_power_attribute(power):
    return {"power": power}

def getAttributes(intent, session):
    sessionAttributes = {}
    if "temperature" in session.get('attributes', {}):
        temperature = session['attributes']['temperature']
        sessionAttributes["temperature"] = temperature
    if "power" in session.get('attributes', {}):
        power = session['attributes']['power']
        sessionAttributes["power"] = power
    return sessionAttributes
        
def stateIntent(intent, session):
    session_attributes = getAttributes(intent, session)
    reprompt_text = None

    if "temperature" in session.get('attributes', {}):
        temperature = session['attributes']['temperature']
        speech_output = "Your current temperature is " + temperature + \
                        " degrees."
        should_end_session = True
    else:
        speech_output = "I'm not sure what your current temperature is. " \
                        "You can ask g t housing to turn it to 67."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'GT Housing',
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }