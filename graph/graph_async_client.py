import fastapi.exceptions as ex

import project_settings

from lib.logger import CustomLogger
from msgraph_async import GraphAdminClient
from pydantic import BaseModel


logger = CustomLogger.get_logger('bot')


async def mobile_validation(mobile: str) -> str:
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


async def build_digital_endpoint(cleared_request):
    if cleared_request.isdigit() and len(cleared_request) == 8:
        endpoint = f"&$filter=employeeId eq \'{cleared_request}\'"

    elif len(cleared_request) == 12:
        endpoint = f"&$filter=mobilePhone eq \'{'%2B' + cleared_request}\'&$count=true"

    else:
        raise ex.HTTPException(status_code=400, detail="Bad input data (BadRequest)")

    return endpoint


async def build_mail_endpoint(cleared_request):
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


async def get_user(search_request: str, manager=False):
    client = GraphAdminClient()

    user_profile_endpoint = "?$select=id,employeeid,displayName,givenName,surname,userPrincipalName,mail," \
                            "mobilePhone,bussinessPhones,jobTitle," \
                            "companyName,department,createdDateTime,manager,manager_mail,onPremisesExtensionAttributes"

    user_mobile_phone_endpoint = "https://graph.microsoft.com/v1.0/users?$select=id,employeeid,displayName,givenName,surname,userPrincipalName,mail," \
                                 "mobilePhone,bussinessPhones,jobTitle," \
                                 "companyName,department,createdDateTime,manager,manager_mail,onPremisesExtensionAttributes"

    user_manager_endpoint = '/manager'

    user_group_endpoint = '/memberOf'

    cleared_request = search_request.lower()
    cleared_request = cleared_request.replace('+', '')
    cleared_request = cleared_request.strip()

    endpoint_suffix = ''
    try:
        int(cleared_request)
        endpoint_suffix = await build_digital_endpoint(cleared_request)
    except ValueError:
        pass

    if '@' in cleared_request:
        endpoint_suffix = await build_mail_endpoint(cleared_request)

    endpoint = f"{user_profile_endpoint}{endpoint_suffix}"

    await client.manage_token(
        project_settings.MICROSOFT_AUTH_CLIENT_ID,
        project_settings.MICROSOFT_AUTH_CLIENT_SECRET,
        project_settings.MICROSOFT_AUTH_TENANT_ID
    )

    try:
        res = await client.get_user(f"{endpoint}")
    except Exception as e:
        raise ex.HTTPException(status_code=299, detail=f"{e} (RequestAborted)")
    if int(res[1]) != 200:
        raise ex.HTTPException(status_code=299, detail=f"{res[1]} (RequestAborted)")
    if len(res[0]['value']) == 0:
        print('User Not Found')
        return 'User Not Found'
        # raise ex.HTTPException(status_code=299, detail=f"{res[1]} (Bad response data (EmptyResultSet))")

    user_data = res[0]['value'][0]
    status_code =  res[1]
    # print('user_data', user_data, '\nstatus code', status_code)

    if user_data['mobilePhone'] is None:
        mobilePhone = None
    else:
        mobilePhone = await mobile_validation(user_data['mobilePhone'])

    user_data['mobilePhone'] = mobilePhone

    all_user_data = user_data

    if all_user_data['onPremisesExtensionAttributes']['extensionAttribute15'] is None:
        extensionAttribute15 = None
    else:
        extensionAttribute15 = await mobile_validation(all_user_data['onPremisesExtensionAttributes']['extensionAttribute15'])

    all_user_data['extensionAttribute15'] = extensionAttribute15
    all_user_data.pop('onPremisesExtensionAttributes')

    if not manager:
        # print('\n', all_user_data)
        return user_data

    is_manager_exists = None

    manager_endpoint = f"{user_data['id']}{user_manager_endpoint}"
    try:
        manager_res = await client.get_user(f"{manager_endpoint}")
    except Exception as e:
        raise ex.HTTPException(status_code=299, detail=f"{e} (RequestAborted)")
    if int(manager_res[1]) != 200:
        raise ex.HTTPException(status_code=299, detail=f"{manager_res[1]} (RequestAborted)")
    if len(manager_res[0]['userPrincipalName']) is None:
        raise ex.HTTPException(status_code=299, detail=f"{manager_res[1]} (Bad response data (EmptyResultSet))")
    else:
        is_manager_exists = True

    manager_data = manager_res[0]
    if is_manager_exists:
        if manager_data['mobilePhone'] is None:
            mobilePhone = None
        else:
            mobilePhone = await mobile_validation(manager_data['mobilePhone'])

        all_user_data['manager'] = [
            manager_data['displayName'],
            manager_data['userPrincipalName'],
            mobilePhone
        ]
    else:
        all_user_data['manager'] = [
            None,
            None,
            None
        ]

    # print(all_user_data)
    return all_user_data
