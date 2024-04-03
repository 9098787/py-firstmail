from requests import Session
from typing import Literal
import base64
import pyotp

from exceptions import LoginError, ExpiredJWT, GetMessagesError
from endpoints import endpoints

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

    def check_jwt(self) -> bool:
        '''
        Check JWT for expire

        :returns: true if valid else false
        '''
        check_jwt_request = self.__session.post(endpoints['check_jwt'], json={})
        if check_jwt_request.status_code == 200:
            return True
        else:
            return False

    def login(self, email: str, password: str, otpcode: str = None) -> None:
        '''
        Login method

        :param email: account's email
        :param password: account's password
        :param otpcode: (Optional) 6-digit code or base-32 secret code
        '''
        # Prepairing to request
        payload = {
            'username': email,
            'password': password
        }
        if otpcode:
            payload['code'] = self.__getotp(otpcode)
        # Request
        login_request = self.__session.post(endpoints['login'], data=payload)
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

    def get_messages(self, folder: Literal['inbox', 'starred', 'spam'] = 'inbox') -> dict[str: int, str: list]:
        '''
        Get messages method

        :param folder: inbox/starred/spam, default inbox
        :returns: dictionary with count and list of messages
        '''
        if folder not in ['inbox', 'starred', 'spam']:
            raise GetMessagesError('Invalid "folder" parameter')

        payload = {
            'folder': folder
        }
        get_messages_request = self.__session.post(endpoints['get_messages'], json=payload)
        if get_messages_request.status_code == 403:
            raise ExpiredJWT('Token has expired')



fm = Firstmail()
fm.login('mariebarnes2018@serodiemail.ru', 'joxbigwg5552', '61994')