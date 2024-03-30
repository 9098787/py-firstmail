from requests import Session
import errors

class Firstmail:
    '''
    Firstmail account object

    Default user-agent is Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36
    '''
    def __init__(self, 
                 proxies: dict = None,
                 user_agent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36'):
        self.email = None
        self.password = None
        
        self.__session = Session()
        self.__session.headers = {
            'User-Agent': user_agent
        }
        self.__session.proxies = proxies
    
    def login(self, email: str, password: str, otpcode: str = None) -> None:
        '''
        Login method

        If you're using account with 2FA, you can provide 6-digits code from your app or secret 2FA key
        '''
        self.email = email
        self.password = password
        login_url = 'https://api.firstmail.ltd/mail/login/'
        payload = {
            'username': email,
            'password': password
        }
        #TODO: Editing payload with 2FA code

        login_request = self.__session.post(login_url, data=payload)
        login_result = login_request.json()
        if login_result['error']:
            raise errors.LoginError(login_result['message'])
        jwt_token = login_result['jwtToken']
        self.__session.headers['Authorization'] = 'Bearer ' + jwt_token

fm = Firstmail()
fm.login('sharonterry1903@semiaemail.ru', 'xsejiulg6214')