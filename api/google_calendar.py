from datetime import datetime,timedelta,timezone
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import base64
import os


#Permissoes Google
SCOPES = ['https://www.googleapis.com/auth/calendar']

#Login
def autenticar():
    token = os.getenv('GOOGLE_TOKEN_B64')

    if token:
        creds = pickle.loads(base64.b64decode(token))
    elif os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as f:
            creds = pickle.load(f)
    else:
        raise Exception('Credenciais não encontradas. Rode gerar_token.py primeiro.')

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build('calendar', 'v3', credentials=creds)

service = autenticar()


def buscar_eventos(data_inicio=None, data_fim=None):
    agora = datetime.now(timezone.utc)

    if not data_inicio:
        data_inicio = agora.isoformat()
    if not data_fim:
        data_fim = agora.replace(hour=23, minute=59, second=59).isoformat()

    eventos = service.events().list(
        calendarId='primary',
        timeMin=data_inicio,
        timeMax=data_fim,
        maxResults=20,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    itens = eventos.get('items', [])

    if not itens:
        return 'Você não possui eventos nesse período.'

    resposta = ''
    for evento in itens:
        titulo = evento['summary']
        inicio_raw = evento['start'].get('dateTime', evento['start'].get('date'))

        # Formata para mostrar só HH:MM
        try:
            dt = datetime.fromisoformat(inicio_raw)
            hora = dt.strftime('%H:%M')
        except Exception:
            hora = inicio_raw  # fallback se vier só data sem hora

        resposta += f'- {titulo} | {hora}\n'

    return resposta

def criar_evento(titulo: str, data_inicio: str, data_fim: str, descricao = ''):
    evento = {
        'summary': titulo,
        'description': descricao,
        'start': {'dateTime': data_inicio, 'timeZone': 'America/Fortaleza'},
        'end':   {'dateTime': data_fim,    'timeZone': 'America/Fortaleza'},       
    }

    criado = service.events().insert(calendarId='primary', body=evento).execute()

    return f"Evento '{titulo}' criado com sucesso! ID: {criado['id']}"

def deletar_evento(evento_id: str) -> str:
    service.events().delete(calendarId='primary', eventId=evento_id).execute()
    return f"Evento deletado com sucesso."

def alterar_evento(evento_id: str, titulo: str = None, data_inicio: str = None,
                   data_fim: str = None, descricao: str = None) -> str:
    # Busca o evento atual para não sobrescrever campos não alterados
    evento = service.events().get(calendarId='primary', eventId=evento_id).execute()

    if titulo:
        evento['summary'] = titulo
    if descricao:
        evento['description'] = descricao
    if data_inicio:
        evento['start'] = {'dateTime': data_inicio, 'timeZone': 'America/Fortaleza'}
    if data_fim:
        evento['end'] = {'dateTime': data_fim, 'timeZone': 'America/Fortaleza'}

    atualizado = service.events().update(
        calendarId='primary', eventId=evento_id, body=evento
    ).execute()
    return f"Evento '{atualizado['summary']}' atualizado com sucesso."

def buscar_evento_por_titulo(titulo: str) -> list:
    """Busca eventos pelo nome — necessário para alterar/deletar por nome."""
    resultado = service.events().list(
        calendarId='primary',
        q=titulo,  # pesquisa por texto
        maxResults=5,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return resultado.get('items', [])