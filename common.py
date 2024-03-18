import telebot
from configparser import ConfigParser
from pathlib import Path
import os
from socket import gaierror
from ssl import SSLEOFError
from datetime import datetime, timedelta, date
from colorama import Fore, Style, init
import traceback
from typing import Union, Callable, Any, List, Dict, Generator
from googleapiclient.errors import HttpError
import httplib2
import googleapiclient.discovery
import time
import random
from google.oauth2 import service_account
from googleapiclient.discovery import build


SLEEP_GOOGLE = 20
MAX_ROW = 1000
init()
random.seed()
CREDS = service_account.Credentials.from_service_account_file('keys.json', scopes=['https://www.googleapis.com/auth/spreadsheets'])


def BuildService() -> googleapiclient.discovery.Resource:
    Stamp(f'Trying to build service', 'i')
    try:
        service = build('sheets', 'v4', credentials=CREDS)
    except (HttpError, TimeoutError, httplib2.error.ServerNotFoundError, gaierror, SSLEOFError) as err:
        Stamp(f'Status = {err} on building service', 'e')
        Sleep(SLEEP_GOOGLE)
        BuildService()
    else:
        Stamp('Built service successfully', 's')
        return service


def Sleep(timer: int, ratio: float = 0.0) -> None:
    rand_time = random.randint(int((1 - ratio) * timer), int((1 + ratio) * timer))
    Stamp(f'Sleeping {rand_time} seconds', 'l')
    time.sleep(rand_time)


def Stamp(message: str, level: str) -> None:
    time_stamp = datetime.now().strftime('[%m-%d|%H:%M:%S]')
    match level:
        case 'i':
            print(Fore.LIGHTBLUE_EX + time_stamp + '[INF] ' + message + '.' + Style.RESET_ALL)
        case 'w':
            print(Fore.LIGHTMAGENTA_EX + time_stamp + '[WAR] ' + message + '!' + Style.RESET_ALL)
        case 's':
            print(Fore.LIGHTGREEN_EX + time_stamp + '[SUC] ' + message + '.' + Style.RESET_ALL)
        case 'e':
            print(Fore.RED + time_stamp + '[ERR] ' + message + '!!!' + Style.RESET_ALL)
        case 'l':
            print(Fore.WHITE + time_stamp + '[SLE] ' + message + '...' + Style.RESET_ALL)
        case 'b':
            print(Fore.LIGHTYELLOW_EX + time_stamp + '[BOR] ' + message + '.' + Style.RESET_ALL)
        case _:
            print(Fore.WHITE + time_stamp + '[UNK] ' + message + '?' + Style.RESET_ALL)


def ParseConfig(direct: str = '') -> (ConfigParser, list):
    config = ConfigParser()
    config.read(Path.cwd() / direct / 'config.ini', encoding='utf-8')
    sections = config.sections()
    return config, sections


def GetColumn(column: str, service: googleapiclient.discovery.Resource, sheet_name: str, sheet_id: str, skip_empty: bool = True, start_row: int = 2, end_row: int = MAX_ROW) -> list:
    Stamp(f'Trying to get column {column} from sheet {sheet_name}', 'i')
    try:
        res = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=f'{sheet_name}!{column}{start_row}:{column}{end_row}').execute().get('values', [])
    except (TimeoutError, httplib2.error.ServerNotFoundError, gaierror, HttpError, SSLEOFError) as err:
        Stamp(f'Status = {err} on getting column {column} from sheet {sheet_name}', 'e')
        Sleep(SLEEP_GOOGLE)
        res = GetColumn(column, service, sheet_name, sheet_id, skip_empty, start_row, end_row)
    else:
        if not res:
            Stamp(f'No elements in column {column} sheet {sheet_name} found', 'w')
        else:
            Stamp(f'Found {len(res)} elements from column {column} sheet {sheet_name}', 's')
            if skip_empty:
                res = [item for sublist in res for item in sublist]
            else:
                res = [None if not sublist else item for sublist in res for item in (sublist if sublist else [None])]
    return res
