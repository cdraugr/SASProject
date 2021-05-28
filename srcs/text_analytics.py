import re
import typing as tp

import requests
from bs4 import BeautifulSoup

from srcs import config


def get_text(link: str) -> str:
    if re.match(config.LINK_TEMPLATE, link) is None:
        raise ValueError('Invalid link given.')

    rq = requests.get(link)
    if rq.status_code != 200:
        raise ValueError('Unable to open link.')

    bs = BeautifulSoup(rq.text.replace(r'<br \>', '\n'), 'html.parser')
    text = bs.get_text(separator='\n')
    if config.SUBTITLE not in text:
        raise ValueError('Incorrect message type.')

    if config.TEXT_START not in text or config.TEXT_END not in text:
        raise ValueError('Unable to parse text.')
    return '1. ' + text[text.index(config.TEXT_START): text.index(config.TEXT_END)].strip()


def get_line(text: str, idx) -> str:
    return re.sub(
        r'\s+', ' ',
        re.split(r'[:\t\n]', re.split(r'\n1\.|\n2\.', text.split(f'1.{idx}')[1])[0][2:], maxsplit=1)[-1].strip()
    )


def get_full_issuer_name(text: str) -> str:
    return get_line(text, config.FULL_NAME_ID)


def get_short_issuer_name(text: str) -> str:
    return get_line(text, config.SHORT_NAME_ID)


def get_address_issuer(text: str) -> str:
    return get_line(text, config.ADDRESS_ID)


def get_inn_issuer(text: str) -> str:
    return ''.join(list(filter(str.isdigit, get_line(text, config.INN_ID))))


def get_ogrn_issuer(text: str) -> str:
    return ''.join(list(filter(str.isdigit, get_line(text, config.OGRN_ID))))


def get_date(text: str) -> str:
    return text.split(f'1.{config.DATE_ID}')[1].split('\n')[0].split(':')[-1].split('\t')[-1].strip()


def get_meeting_form(text: str) -> str:
    text = text.lower()
    if config.FORM not in text:
        return config.NO_DATA

    text = list(filter(None, re.split(r'[:\-–\n\t]', text.split(config.FORM)[1])))
    text = text[1].strip() if text[1].strip() else text[2].strip()
    return text[:-1] if not text[-1].isalpha() and text[-1] != ')' else text


def get_auditor(text: str) -> tp.Tuple[str, str]:
    lower_text = text.lower()
    for variant in config.AUDITOR_VARIANTS:
        if variant not in lower_text:
            continue

        rid = lower_text.rindex(variant)
        result = re.sub(r'["«»()]', '', re.split(r'["»]', re.split(r'["«]', text[rid:], maxsplit=1)[1])[0])
        if result == 'ЗА':
            break

        if text.count('ИНН ') <= 1:
            return result, config.NO_DATA

        issuer_inn = get_inn_issuer(text)
        inn = text[text.rindex('ИНН '):][4:14]

        return (result, inn) if inn != issuer_inn and inn.isdigit() else (result, config.NO_DATA)

    return config.NO_DATA, config.NO_DATA


def get_auditor_reporting_type(text: str) -> str:
    if 'тип отчётности' in text.lower():
        raise ValueError('WOW, DUDE!!')
    return config.NO_DATA


def get_directors_list(text: str) -> str:
    lower_text = text.lower()
    for variant in config.DIRECTORS_VARIANTS:
        if variant not in lower_text:
            continue

        rid = lower_text.rindex(variant)
        data = re.split(r'[:\n–]', text[rid:], maxsplit=1)[1]
        data = re.sub(r'[0-9]+|\W+', ' ', data)
        data = re.sub(r'\s+', ' ', data).strip().split()
        result = []
        for index in range(0, len(data), 3):
            valid = True
            names = data[index:(index + 3)]
            for i, name in enumerate(names):
                if not name[0].isupper():
                    valid = False
                    break
                if len(name) == 1:
                    names[i] += '.'
            if not valid:
                break
            result.append(' '.join(names))
        return '\n'.join(result) if result else config.CLOSED_INFO

    return config.NO_DATA


def get_dividends(text: str) -> str:
    text = text.lower()
    if 'дивиденд' in text:
        return config.DIV_NOT if 'не выплачивать' in text else config.DIV_OK
    return config.DIV_404


def get_all_by_text(text: str) -> tp.Dict[str, str]:
    auditor, auditor_inn = get_auditor(text)

    return {
        'text': text,
        'full_name': get_full_issuer_name(text),
        'short_name': get_short_issuer_name(text),
        'address': get_address_issuer(text),
        'INN': get_inn_issuer(text),
        'OGRN': get_ogrn_issuer(text),
        'date': get_date(text),
        'meeting_form': get_meeting_form(text),
        'auditor_name': auditor,
        'auditor_INN': auditor_inn,
        'directors': get_directors_list(text),
        'dividends': get_dividends(text)
    }


def get_all_by_link(link: str) -> tp.Dict[str, str]:
    link = link.strip()
    text = get_text(link)
    return {'ID': link.split('=')[-1], 'link': link, **get_all_by_text(text)}
