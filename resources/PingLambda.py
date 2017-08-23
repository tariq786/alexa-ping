import random
import urllib2


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    '''
    :param title:
    :param output:
    :param reprompt_text:
    :param should_end_session:
    :return: returns Response according to Alexa api
    '''
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
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
    '''
    :param session_attributes:
    :param speechlet_response:
    :return: returns Response with wrapper
    '''
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def get_help_text():
    """
    :return: returns help text
    """
    host_list = ['google.com', 'youtube.com', 'facebook.com', 'wikipedia.com', 'reddit.com', 'runescape.com', 'twitter',
                 'http://www.fake.news/']
    input_text = ['ping {host}', 'is {host} up', 'is {host} down', 'is {host} working', 'is {host} not working']
    host = random.choice(host_list)
    input = random.choice(input_text)
    reprompt_text = "To check if {host} is up or down, say " + input
    return reprompt_text.replace('{host}', host)


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    reprompt_text = get_help_text()
    speech_output = "Welcome to Ping. Please tell me which host to ping. " + reprompt_text
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.


    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using ping"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def convert(url):
    url = url.replace("dot", ".")
    url = url.replace(" ", "")
    if url.startswith('http://www.'):
        url = 'http://' + url[len('http://www.'):]
    elif url.startswith('www.'):
        url = 'http://' + url[len('www.'):]
    elif not url.startswith('http://'):
        url = 'http://' + url

    if url.find(".") == -1:
        url = url + ".com"
    return url


def ping_host(host):
    url = convert(host)
    try:
        urllib2.urlopen(url, timeout=2)
        return url + ' is up!'
    except:
        print('FAIL: UTTER=' + host + " URL =" + url)
        return url + ' is not reachable!'


def on_ping(intent, session):
    """
    Gets host status
    """

    card_title = 'Here is what Ping It found'
    session_attributes = {}
    should_end_session = False

    if 'host' in intent['slots']:

        speech_output = ping_host(intent['slots']['host']['value'])
        reprompt_text = get_help_text()
        should_end_session = True
    else:
        speech_output = "Not sure." \
                        "Please try again."
        reprompt_text = "I'm not sure." \
                        "Please try again"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "PingIntent":
        return on_ping(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


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


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])


def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.DERP_REMOVED"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
