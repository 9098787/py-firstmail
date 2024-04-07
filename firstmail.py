from requests import Session
from typing import Literal
from string import ascii_letters
import base64
import pyotp
import random

from exceptions import LoginError, ExpiredJWT, GetMessagesError, NeedLogin, ChangePasswordError
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
            'User-Agent': user_agent,
            'Authorization': None
        }
        self.__session.proxies = proxies
        self.__email = None
        self.__password = None
        self.__otp_key = None
    
    @staticmethod
    def getotp(otpcode: str) -> str:
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

    @staticmethod
    def validate_password(password: str) -> bool:
        '''
        Validating password before change
        '''
        if len(password) < 8:
            return False
        for char in password:
            if char not in ascii_letters + '0123456789' + '!@#$%^&*()':
                return False
        return True

    @staticmethod
    def generate_password() -> str:
        '''
        :returns: random password (8 chars + 4 digits)
        '''
        password = ''
        for _ in range(8):
            password += random.choice(ascii_letters)
        for _ in range(4):
            password += str(random.randint(0, 9))
        return password

    def check_jwt(self) -> bool:
        '''
        Check JWT for expire

        :returns: true if valid, else false
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
        self.__email = email
        self.__password = password

    def get_messages(self, folder: Literal['inbox', 'starred', 'spam'] = 'inbox') -> dict:
        '''
        Get messages method. This method returns only first 10 messages from folder.
        If you need more, you can use search method

        :param folder: inbox/starred/spam, default inbox
        :returns: dictionary with count and list of messages
        '''
        if folder not in ['inbox', 'starred', 'spam']:
            raise GetMessagesError('Invalid "folder" parameter')
        if 'Authorization' not in self.__session.headers:
            raise NeedLogin('Need login for using this method')

        payload = {
            'folder': folder
        }
        get_messages_request = self.__session.post(endpoints['get_messages'], json=payload)
        if get_messages_request.status_code in [403, 500]:
            raise ExpiredJWT('Token has expired')
        get_messages_result = get_messages_request.json()
        return get_messages_result
    
    def change_password(self, new_password: str) -> None:
        '''
        Change password method

        :param new_password: new password, 8 only ASCII-letters with special chars
        '''
        # Exceptions before request
        if 'Authorization' not in self.__session.headers:
            raise NeedLogin('Need login for using this method')
        if not self.validate_password(new_password):
            raise ChangePasswordError('The password does not meet the requirements')
        # Main request
        payload = {
            'cpassword': self.__password,
            'npassword': new_password,
            'npassword2': new_password
        }
        change_password_request = self.__session.post(endpoints['change_password'], data=payload)
        # Catching errors
        if change_password_request.status_code in [403, 500]:
            raise ExpiredJWT('Token has expired')
        change_password_result = change_password_request.json()
        if change_password_result['error']:
            raise ChangePasswordError(change_password_result['message'])
        # Saving new password and JWT
        self.__password = new_password
        self.__session.headers['Authorization'] = change_password_result['Token']

    def search(self, query: str = '') -> dict:
        '''
        Search messages method
        Only with this method you can get all messages from firstmail without using IMAP

        :param query: search query (you can keep it empty to get all messages)
        :returns: dict with messages count, empty (True if empty, else False), messages list
        '''
        # Exceptions before request
        if 'Authorization' not in self.__session.headers:
            raise NeedLogin('Need login for using this method')
        

    def get_credentials(self) -> dict:
        '''
        Get credentials method

        :returns: dict with email, password, JWT and 2fa secret key
        '''
        return {
            'email': self.__email,
            'password': self.__password,
            'jwt_token': self.__session.headers['Authorization'],
            'otp_key': self.__otp_key
        }






fm = Firstmail()
fm.login('hvdxukwd@sfirstmail.com', 'Ganster09')
messages = fm.get_messages()
print(messages)
print(fm.get_credentials())