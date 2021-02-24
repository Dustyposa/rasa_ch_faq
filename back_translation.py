from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import as_completed
from enum import Enum

import click
import requests


class TransSupportEnum(str, Enum):
    Chinese = "zh"
    English = "en"
    Arabic = "ar"
    French = "fr"
    German = "de"
    Italian = "it"
    Portuguese = "pt"
    Russian = "ru"
    Spanish = "es"


@click.command()
@click.option('--original_string', prompt='回译原始字符串',
              help='需要回译的文本')
def trans(original_string: str):
    with ThreadPoolExecutor() as executor:
        res = []
        for target in TransSupportEnum:
            if target != TransSupportEnum.Chinese:
                res.append(executor.submit(get_trans_data, original_string, "zh", target))
        for r in as_completed(res):
            print(r.result())


TRANS_URL = "https://libretranslate.com/translate"


def get_trans_data(q: str, source: TransSupportEnum, target: TransSupportEnum):
    try:
        res = requests.post(TRANS_URL, data={
            "q": q,
            "source": source,
            "target": target
        }).json()
        data = {"source": target.value, "q": res["translatedText"], "target": "zh"}
    except KeyError:
        return
    return requests.post(TRANS_URL, data=data).json()["translatedText"]


if __name__ == '__main__':
    trans()
    # print(TransSupportEnum)
