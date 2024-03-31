from requests import Session
from errors import LoginError
from typing import Literal
import base64
import pyotp

class Firstmail:
    '''
    Firstmail account object

    Default user-agent is Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36
    '''
    def __init__(self, 
                 proxies: dict = None,
                 user_agent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36') -> None:      
        # Creating session
        self.__session = Session()
        self.__session.headers = {
            'User-Agent': user_agent
        }
        self.__session.proxies = proxies
    
    def __getotp(self, otpcode: str) -> str:
        '''
        Handle "otpcode" from login method's parameter
        '''
        if len(otpcode) == 6:
            return otpcode
        else:
            try:
                totp = pyotp.TOTP(otpcode)
                current_code = totp.now()
                return current_code
            except base64.binascii.Error:
                return otpcode

    def login(self, email: str, password: str, otpcode: str = None) -> None:
        '''
        Login method

        If you're using account with 2FA, you can provide 6-digits code from your app or secret 2FA key
        '''
        # Prepairing to request
        login_url = 'https://api.firstmail.ltd/mail/login/'
        payload = {
            'username': email,
            'password': password
        }
        if otpcode:
            payload['code'] = self.__getotp(otpcode)
        # Request
        login_request = self.__session.post(login_url, data=payload)
        login_result = login_request.json()
        # Catching errors
        if login_result['error']:
            if 'status' in login_result:
                raise LoginError(login_result['status'])
            else:
                raise LoginError(login_result['message'])
        if 'status' in login_result:
            if login_result['status'] == 'bad 2fa':
                raise LoginError('Need 2FA code. Provide it using parameter "otpcode"')
        # Saving JWT
        jwt_token = login_result['jwtToken']
        self.__session.headers['Authorization'] = 'Bearer ' + jwt_token

    def get_messages(self,
                      folder: Literal['inbox', 'starred', 'spam'] = 'inbox',
                        check_jwt: bool = False) -> dict[str: int, str: list]:
        '''
        Get messages method
        '''


fm = Firstmail()
fm.login('mariebarnes2018@serodiemail.ru', 'joxbigwg5552', '61994')