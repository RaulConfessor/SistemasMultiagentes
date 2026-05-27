from google_auth_oauthlib.flow import InstalledAppFlow
import pickle, base64

SCOPES = ['https://www.googleapis.com/auth/calendar'] #Permissões desejadas

flow = InstalledAppFlow.from_client_secrets_file('credenciais.json', SCOPES)
creds = flow.run_local_server(port=0)

with open('token.pickle', 'wb') as f:
    pickle.dump(creds, f)

print('\n=== Cole isso como GOOGLE_TOKEN_B64 no Render ===\n')
print(base64.b64encode(open('token.pickle', 'rb').read()).decode())