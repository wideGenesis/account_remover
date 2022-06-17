import project_settings
from .graph_api_2 import GraphApi


client = GraphApi(
 client_id=project_settings.MICROSOFT_AUTH_CLIENT_ID,
 client_secret=project_settings.MICROSOFT_AUTH_CLIENT_SECRET,
 tenant_id=project_settings.MICROSOFT_AUTH_TENANT_ID,
)
