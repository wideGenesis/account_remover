import json

import fastapi.exceptions as ex
import msal
import requests

from lib.logger import CustomLogger


logger = CustomLogger.get_logger('bot')


def mobile_validation(mobile: str) -> str:
    # clear
    _mobile = mobile.strip()
    _mobile = mobile.replace(' ', '')
    _mobile = _mobile.replace('-', '')
    _mobile = _mobile.replace('(', '')
    _mobile = _mobile.replace(')', '')

    # restore
    length = len(_mobile)
    if length == 13:
        return _mobile
    elif length == 12:
        return '+' + _mobile
    elif length == 11:
        return '+3' + _mobile
    elif length == 10:
        return '+38' + _mobile
    elif length == 9:
        return '+380' + _mobile
    else:
        return 'Нет записи в AD'


def build_digital_endpoint(cleared_request):

    if cleared_request.isdigit() and len(cleared_request) == 8:
        endpoint = f"&$filter=employeeId eq \'{cleared_request}\'"

    elif len(cleared_request) == 12:
        endpoint = f"&$filter=mobilePhone eq \'{'%2B' + cleared_request}\'&$count=true"

    else:
        raise ex.HTTPException(status_code=400, detail="Bad input data (BadRequest)")

    return endpoint


def build_mail_endpoint(cleared_request):
    upn = 'metinvestholding.com'
    domains = [
        'metinvest.digital',
        'zaporizhstal.com',
        'dmkd.dp.ua',
        'zlmz.zaporizhstal.com',
        'mih.onmicrosoft.com'
    ]
    domain_in_request = cleared_request.split('@')

    if domain_in_request[1] == upn:
        endpoint = f"&$filter=userPrincipalName eq \'{cleared_request}\'"

    elif domain_in_request[1] in domains:
        endpoint = f"&$filter=mail eq \'{cleared_request}\'"

    else:
        raise ex.HTTPException(status_code=400, detail="Bad input data (BadRequest)")


    return endpoint


class GraphApi:
    client_id = None
    client_secret = None
    tenant_id = None
    bearer = None
    tenant_base_url = 'https://login.microsoftonline.com/'
    scope = ["https://graph.microsoft.com/.default"]
    graph_base_url = 'https://graph.microsoft.com/v1.0/users/'
    user_profile_endpoint = "?$select=id,employeeid,displayName,givenName,surname,userPrincipalName,mail," \
                            "mobilePhone,bussinessPhones,jobTitle," \
                            "companyName,department,createdDateTime,manager,manager_mail,onPremisesExtensionAttributes"

    user_mobile_phone_endpoint = "https://graph.microsoft.com/v1.0/users?$select=id,employeeid,displayName,givenName,surname,userPrincipalName,mail," \
                                 "mobilePhone,bussinessPhones,jobTitle," \
                                 "companyName,department,createdDateTime,manager,manager_mail,onPremisesExtensionAttributes"

    user_manager_endpoint = '/manager'
    user_group_endpoint = '/memberOf'

    def __init__(self,
                 client_id=None, client_secret=None, tenant_id=None, bearer=bearer):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.bearer = bearer
        self.auth()

    def auth(self):
        # Create a preferably long-lived app instance which maintains a token cache.
        try:
            app = msal.ConfidentialClientApplication(
                self.client_id, authority=f'{self.tenant_base_url}{self.tenant_id}/',
                client_credential=self.client_secret)
        except:
            raise ValueError('Bad response from msal')

        # Firstly, looks up a token from cache
        # Since we are looking for token for the current app, NOT for an end user,
        # notice we give account parameter as None.

        try:
            result = app.acquire_token_silent(self.scope, account=None)
        except Exception:
            raise ValueError('Acquire token silently has been failure')

        if not result:
            # print("No suitable token exists in cache. Let's get a new one from AAD.")
            result = app.acquire_token_for_client(scopes=self.scope)
        if "access_token" not in result:
            raise ValueError('Acquire token has been failure')
        # self.bearer = {'Authorization': 'Bearer ' + result['access_token']}
        self.bearer = {'Authorization': 'Bearer ' + result['access_token'], 'ConsistencyLevel': 'eventual'}

    def get_msgraph_data(self, search_request):
        self.auth()

        # print('>>>>>>>>>> incoming request', len(search_request), search_request)
        cleared_request = search_request.lower()
        cleared_request = cleared_request.replace('+', '')
        cleared_request = cleared_request.strip()
        # print('>>>>>>>>>> cleared request', len(cleared_request), cleared_request)

        endpoint_ends = ''
        try:
            int(cleared_request)
            endpoint_ends = build_digital_endpoint(cleared_request)
        except ValueError:
            pass

        if '@' in cleared_request:
            endpoint_ends = build_mail_endpoint(cleared_request)

        endpoint = f"{self.graph_base_url}{self.user_profile_endpoint}{endpoint_ends}"

        try:
            print('>>>>>>>>>>', endpoint)
            response = requests.get(endpoint, headers=self.bearer)
            print('>>>>>>>>>>', response)
        except Exception as e:
            raise ex.HTTPException(status_code=299, detail=f"{e} (RequestAborted)")


        if response.status_code != 200:
            raise ex.HTTPException(status_code=299, detail=f"{response.json()} (RequestAborted)")

        graph_data = response.json()
        res = json.dumps(graph_data, indent=2)
        res = json.loads(res)
        # print('>>>>>>>>>>>>>>>>>>>>', res)
        if not res or 'value' not in res:
            raise ex.HTTPException(status_code=444, detail="Bad response data (EmptyResultSet)")

        if not res['value']:
            raise ex.HTTPException(status_code=404, detail="Error 404 (ObjectDoesNotExist)")

        if res['value'][0]['mobilePhone'] is None:
            mobilePhone = 'Нет записи в AD'
        else:
            mobilePhone = mobile_validation(res['value'][0]['mobilePhone'])

        res['value'][0]['mobilePhone'] = mobilePhone

        all_user_data = res['value'][0]
        is_manager_exists = None
        try:
            response = requests.get(
                f"{self.graph_base_url}{res['value'][0]['id']}{self.user_manager_endpoint}",
                headers=self.bearer)
        except Exception as e:
            raise ex.HTTPException(status_code=299, detail=f"{e} (RequestAborted)")


        if response.status_code != 200:
            is_manager_exists = False
            # logger.debug('Graph Error %s', response.json())

        if response.status_code == 200:
            is_manager_exists = True

        if is_manager_exists:
            manager_graph_data = response.json()
            manager_result = json.dumps(manager_graph_data, indent=2)
            manager_result = json.loads(manager_result)

            if manager_result['mobilePhone'] is None:
                mobilePhone = 'Нет записи в AD'
            else:
                mobilePhone = mobile_validation(manager_result['mobilePhone'])

            all_user_data['manager'] = [
                manager_result['displayName'],
                manager_result['userPrincipalName'],
                mobilePhone
            ]
        else:
            all_user_data['manager'] = [
                'Нет записи в AD',
                'Нет записи в AD',
                'Нет записи в AD'
            ]

        if all_user_data['onPremisesExtensionAttributes']['extensionAttribute15'] is None:
            extensionAttribute15 = 'Нет записи в AD'
        else:
            extensionAttribute15 = mobile_validation(all_user_data['onPremisesExtensionAttributes']['extensionAttribute15'])

        all_user_data['extensionAttribute15'] = extensionAttribute15
        all_user_data.pop('onPremisesExtensionAttributes')
        # logger.debug(all_user_data)
        return all_user_data
