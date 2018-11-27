import logging
import uuid
import urllib3
import xml.etree.ElementTree as ET
import boto3
import redirect

logger = logging.getLogger()
logger.setLevel(logging.INFO)

baseServiceUrl = "https://hvac.aws.itg.gatech.edu/auth/login"
baseCasUrl = "https://login.gatech.edu/cas/"

def get_username(event):
    """
    Retrieves the username and token from the event data. Will throw an exception
    if the event parameters are invalid or missing.
    @param: event Dictionary of event parameters passed to the lambda function.
    @return: A dictionary containing 'gtUsername' and 'token' if successful,
    otherwise returns a dictionary that, when returned by the lambda function,
    will redirect the user to authenticate themselves.
    """
    _returnUrl = None;
    _ticket = None;
    _state = None;
    _redirect_uri = None;

    logger.info("Invoked")
    logger.info("Alexalogin")
    logger.info("event=" + str(event))

    # Check for returnUrl or redirect_uri
    if 'returnUrl' in event:
        _returnUrl = event['returnUrl']

    if 'redirect_uri' in event:
        _redirect_uri = event['redirect_uri']

    if _returnUrl is None and _redirect_uri is None:
        return _raise_exception("returnUrl or redirect_uri is required")

    logger.info("serviceUrl=" + baseServiceUrl)
    logger.info("returnUrl=" + _returnUrl)
    logger.info("redirect_uri=" + _redirect_uri)

    # Check for state and ticket
    if 'state' in event:
        _state = event['state']

    if 'ticket' in event:
        _ticket = event['ticket']

    if _ticket is None:
        return redirect.to_cas(_state, _redirect_uri)
    logger.info("ticket=" + _ticket)

    # Validate ticket
    gtUsername = _validate_ticket(_ticket, _state, _redirect_uri)
    if gtUsername is None:
        return _raise_exception("Unable to validate ticket.")

    # Store username/token pair
    token = str(uuid.uuid4())
    if not _write_record(gtUsername, token):
        return _raise_exception("Unable to store token.")

    # Return to Alexa
    return {'gtUsername': gtUsername, 'token': token}

def _raise_exception(message, log_error=True):
    """
    Raises an exception and (optionally)
    logs it using the logger.
    """
    if log_error:
        logger.error(message)
    raise Exception(message)

def _validate_ticket(ticket, state, redirect_uri):
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
        xml = _get_response(validateUrl)
        logger.info("validate_ticket xml=" + xml.replace("\n", "\t"))
        user = _get_username_from_xml(xml)
        logger.info("user=" + user)
    except Exception as e:
        logger.error("Unable to validate ticket.")
        logger.error("Error: " + str(e))
    
    return user

def _write_record(user, token):
    """
    Writes the username/token pair to a database.
    @return: True if successful, false otherwise.
    """
    try:
        access_key = "AKIAJUH6GWDIONKYCVEQ"
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

def _get_response(url, decode_type='utf-8'):
    """
    Returns the string resulting from a GET
    request to the provided url.
    """
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    return response.data.decode(decode_type)

def _get_username_from_xml(xml):
    """
    Attempts to get the username from the XML string.
    @return: The username if found, None otherwise.
    """
    root = ET.fromstring(xml)
    user = None
    try:
        a = 'cas:serviceResponse'
        b = 'cas:authenticationSuccess'
        c = 'cas:user'
        user = root.find(a).find(b).find(c)
    except Exception as e:
        logger.error("Unable to parse XML.")
        logger.error("Error: " + str(e))
    return user