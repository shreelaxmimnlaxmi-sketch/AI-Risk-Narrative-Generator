from groq import Client
client = Client(api_key='test')
print('base_url=', client.base_url)
print('has_post=', hasattr(client, 'post'))
print('has_request=', hasattr(client, 'request'))
print('dir_client=', [name for name in dir(client) if 'generate' in name.lower() or 'response' in name.lower() or 'post' in name.lower()])
