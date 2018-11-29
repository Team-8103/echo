import logging
import uuid
import urllib3
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

baseServiceUrl = "https://housinghvac.itg.gatech.edu/gatechSSOauth"
baseCasUrl = "https://login.gatech.edu/cas/"


def handler(event, context):
    """
    Handles authorization of a GT student.
    @param: event Dictionary of event parameters.
    @param: context The context of the call.
    """
    _returnUrl = None
    _ticket = None
    _state = None
    _redirect_uri = "https://pitangui.amazon.com/spa/skill/account-linking-status.html?vendorId=MV8VM7SY8W1S6"

    logger.info("Invoked")
    logger.info("Alexalogin")
    logger.info("event=" + str(event))

    # Check for returnUrl or redirect_uri
    if 'queryStringParameters' in event:
        # if 'returnUrl' in event['queryStringParameters']:
        #     _returnUrl = event['queryStringParameters']['returnUrl']

        if 'redirect_uri' in event['queryStringParameters']:
            _redirect_uri = event['queryStringParameters']['redirect_uri']

        if 'state' in event['queryStringParameters']:
            _state = event['queryStringParameters']['state']

        if 'ticket' in event['queryStringParameters']:
            logger.info("Ticket is in Event")
            _ticket = event['queryStringParameters']['ticket']

    if _returnUrl is None and _redirect_uri is None:
        return raise_exception("returnUrl or redirect_uri is required")

    logger.info("serviceUrl=" + baseServiceUrl)
    # logger.info("returnUrl=" + _returnUrl)
    logger.info("redirect_uri=" + _redirect_uri)

    if _ticket is None:
        return redirect_to_cas(_state, _redirect_uri)
    logger.info("ticket=" + _ticket)

    # Validate ticket
    gtUsername = validate_ticket(_ticket, _state, _redirect_uri)
    if gtUsername is None:
        return raise_exception("Unable to validate ticket.")

    # Store username/token pair
    token = str(uuid.uuid4())
    if not write_record(gtUsername, token):
        return raise_exception("Unable to store token.")

    # Return to Alexa
    return return_to_alexa(token, _redirect_uri, _state)


def raise_exception(message, log_error=True):
    """
    Raises an exception and (optionally)
    logs it using the logger.
    """
    if log_error:
        logger.error(message)
    raise Exception(message)


def validate_ticket(ticket, state, redirect_uri):
    """
    Gets the GT Username from the ticket.
    @return: The username associated with the ticket.
    """
    serviceUrl = baseServiceUrl + \
        "?state=" + state + \
        "&redirect_uri=" + redirect_uri
    validateUrl = baseCasUrl + "serviceValidate" + \
        "?ticket=" + ticket + \
        "&service=" + serviceUrl
    logger.info("validateUrl=" + validateUrl)

    user = None
    try:
        xml = get_response(validateUrl)
        logger.info("validate_ticket xml=" + xml.replace("\n", "\t"))
        user = get_username(xml)
        logger.info("user=" + user)
    except Exception as e:
        logger.error("Unable to validate ticket.")
        logger.error("Error: " + str(e))

    return user


def write_record(user, token):
    """
    Writes the username/token pair to a database.
    @return: True if successful, false otherwise.
    """
    try:
        access_key = "AKIAJF273WN5WJ2UIGOA"
        secret_key = "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"
        client = boto3.client('dynamodb',
                              region_name='us-east-1',
                              aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key)
        response = client.put_item(
            TableName='CasAuthTable',
            Item={
                'gtUsername': {'S': user},
                'token': {'S': token}
            })
        return True
    except Exception as e:
        logger.error("Unable to write record.")
        logger.error("Error: " + str(e))

    return False


def redirect_to_cas(state, redirect_uri):
    """
    Returns a dictionary that will redirect the service
    to CAS in order to login.
    """
    logger.info("Redirecting to CAS. No ticket.")

    serviceUrl = baseServiceUrl + \
        "?state=" + state + \
        "&redirect_uri=" + redirect_uri

    loginUrl = baseCasUrl + "login?service=" + serviceUrl
    logger.info("loginUrl=" + loginUrl)

    return {'statusCode': 302, 'headers': {
        'Location': loginUrl}}


def return_to_alexa(token, redirect_uri, state):
    """
    Returns a dictionary that will redirect the service
    to the Alexa app.
    """
    redirect_uri = redirect_uri + \
        "#state=" + state + \
        "&access_token=" + token + \
        "&token_type=Bearer"
    logger.info("redirect_uri=" + redirect_uri)

    return {'statusCode': 302, 'headers': {
        'Location': redirect_uri}}


def get_response(url, decode_type='utf-8'):
    """
    Returns the string resulting from a GET
    request to the provided url.
    """
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    return response.data.decode(decode_type)


def get_username(xml):
    """
    Attempts to get the username from the XML string.
    @return: The username if found, None otherwise.
    """
    user = None
    try:
        user = xml.split("cas:user")[1][1:-2]
    except Exception as e:
        logger.error("Unable to parse XML.")
        logger.error("Error: " + str(e))
    return user
