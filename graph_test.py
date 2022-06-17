from graph.graph_client import client

# client.get_msgraph_data('andrey.benimovich@metinvestholding.com ')
print(client.get_msgraph_data('tatyana.barabash@metinvest.digital'))
# client.get_msgraph_data('+380502767384')


"""
viktoriya.nartenko@metinvest.digital (Заблокований ІБ тимчасово, людина на НКТ, продовжує працювати у МІД)
{'id': 'a2d92f02-b985-4cde-8cdb-5977d7abf8b2', 'employeeId': '70000123', 
'displayName': 'Нартенко Виктория Ивановна', 'givenName': 'Виктория', 'surname': 'Нартенко', 
'userPrincipalName': 'viktoriya.nartenko@metinvestholding.com', 'mail': 'viktoriya.nartenko@metinvest.digital', 
'mobilePhone': '+380675432271', 'jobTitle': 'Ведущий специалист по развитию', 'companyName': 'ООО Метинвест Диджитал', 
'department': 'Управление функциональной экспертизы', 'createdDateTime': '2015-03-26T13:00:02Z', 
'manager': ['Берестовенко Юрий Анатольевич', 'yuriy.berestovenko@metinvestholding.com', '+380675432849'], 
'extensionAttribute15': 'Нет записи в AD'}


tatyana.barabash@metinvest.digital (Заблокований, співробітник був на НКТ після звільнився)
{'id': 'dd14e27a-dc2b-48bb-8473-91960df61b89', 'employeeId': '70000322', 'displayName': 'Барабаш Татьяна Сергеевна', 
'givenName': 'Татьяна', 'surname': 'Барабаш', 'userPrincipalName': 'tatyana.barabash@metinvestholding.com', 
'mail': 'tatyana.barabash@metinvest.digital', 'mobilePhone': '+380676296044', 'jobTitle': 'Начальник отдела', 
'companyName': 'ООО Метинвест Диджитал', 'department': 'Отдел архитектуры и технологий', 
'createdDateTime': '2016-07-11T10:33:53Z', 
'manager': ['Павленко Елена Васильевна', 'E.V.Pavlenko@metinvestholding.com', '+380674452617'], 
'extensionAttribute15': 'Нет записи в AD'}
"""