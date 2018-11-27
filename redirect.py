baseServiceUrl = "https://hvac.aws.itg.gatech.edu/auth/login"
baseCasUrl = "https://login.gatech.edu/cas/"

def to_cas(state, redirect_uri):
    """
    Returns a dictionary that will direct the user
    to CAS in order to login.
    @param String: state The state provided by the lambda function.
    @param String: redirect_uri Where the user should be taken after authentication.
    """
    logger.info("Redirecting to CAS. No ticket.")
    
    serviceUrl = baseServiceUrl + \
            "?state=" + state + \
            "&redirect_uri=" + redirect_uri
    loginUrl = baseCasUrl + "login?service=" + serviceUrl
    logger.info("loginUrl=" + loginUrl)

    return {'statusCode':302, 'headers':{
        'Location': loginUrl}}

def to_alexa(access_token, state, redirect_uri):
    """
    Returns a dictionary that will direct the user
    to the Alexa app.
    @param String: access_token The access token retrieved from authenticating a user.
    @param String: state The state provided by the lambda function.
    @param String: redirect_uri Where the user should be taken after authentication.
    """
    redirect_uri = redirect_uri + \
        "#state=" + state + \
        "&access_token=" + token + \
        "&token_type=Bearer"
    logger.info("redirect_uri=" + redirect_uri)

    return {'statusCode':302, 'headers':{
        'Location': redirect_uri}}