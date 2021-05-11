import base64
import io
import datetime
import time
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import pandas as pd
import pytz

from actions.utils.request import get

DT_FORMAT_STRING = "%Y-%m-%dT%H:%M:%S%z"
DT_FORMAT_CONVERT_STRING = "%H:%M"

TZ_INFO = pytz.timezone("Asia/Shanghai")


class CoinDataManager:
    def __init__(self, coin_name: str = "btc-bitcoin"):
        self.coin_searcher = CoinSearcher(coin_name)

    async def get_img(self, img_type: str = "base64") -> str:
        data = await self.coin_searcher.get_history()
        df = pd.DataFrame(data)
        df["timestamp"] = df["timestamp"].apply(
            lambda x: datetime.datetime.strptime(x, DT_FORMAT_STRING).astimezone(TZ_INFO).strftime(
                DT_FORMAT_CONVERT_STRING))
        df["mean"] = df["price"].mean()
        return Ploter.plot_line_chat(df, to_type=img_type)


class CoinSearcher:
    """API DOC Address: https://api.coinpaprika.com/"""
    HISTORY_URL = "https://api.coinpaprika.com/v1/tickers/{}/historical"
    INTERVAL_TIME = 24 * 60 * 60

    def __init__(self, coin_name: str = "btc-bitcoin"):
        self.coin_id = self.convert_coin_name_to_id(coin_name)

    @staticmethod
    def convert_coin_name_to_id(coin_name: str) -> str:
        return coin_name

    async def get_history(self) -> List[Dict[Any, Any]]:
        past_ts = time.time() - self.INTERVAL_TIME
        history = await get(url=self.HISTORY_URL.format(self.coin_id),
                            params={"start": int(past_ts), "interval": "1h"})
        return history


class Ploter:
    BASE64_PREFIX = "data:image/jpeg;base64,"

    @classmethod
    def plot_line_chat(cls, data: pd.DataFrame, to_type: str = "base64") -> str:
        plt.figure(figsize=(12, 6))
        plt.plot("timestamp", "price", data=data, marker="o")
        plt.plot(data["mean"], "g--", label="mean price")
        plt.legend()
        plt.xlabel("time")
        plt.xticks(rotation=45)
        plt.ylabel("price")
        plt.title("btc past 24 hours price")

        if to_type == "base64":
            return cls.BASE64_PREFIX + cls.plot_to_base64(plt)
        raise NotImplementedError(f"尚未支持的格式: {to_type}")

    @staticmethod
    def plot_to_base64(plt):
        bytes_io = io.BytesIO()
        plt.savefig(bytes_io, format='png')
        bytes_io.seek(0)
        return base64.b64encode(bytes_io.read()).decode("u8")


if __name__ == '__main__':
    import asyncio
    import base64

    # history = asyncio.run(CoinSearcher().get_history())
    history = [{'timestamp': '2021-05-09T11:00:00Z', 'price': 58154.54, 'volume_24h': 64815608951,
                'market_cap': 1087757589631},
               {'timestamp': '2021-05-09T12:00:00Z', 'price': 57459.75, 'volume_24h': 65527707659,
                'market_cap': 1074765494068},
               {'timestamp': '2021-05-09T13:00:00Z', 'price': 57096.02, 'volume_24h': 66861708379,
                'market_cap': 1067964125363},
               {'timestamp': '2021-05-09T14:00:00Z', 'price': 57514.98, 'volume_24h': 67201240611,
                'market_cap': 1075804076839},
               {'timestamp': '2021-05-09T15:00:00Z', 'price': 57587.07, 'volume_24h': 66827703749,
                'market_cap': 1077157695809},
               {'timestamp': '2021-05-09T16:00:00Z', 'price': 57844.19, 'volume_24h': 65540209486,
                'market_cap': 1081970848207},
               {'timestamp': '2021-05-09T17:00:00Z', 'price': 57750.37, 'volume_24h': 64214755439,
                'market_cap': 1080217220194},
               {'timestamp': '2021-05-09T18:00:00Z', 'price': 57772.28, 'volume_24h': 62781932260,
                'market_cap': 1080631254566},
               {'timestamp': '2021-05-09T19:00:00Z', 'price': 57691.66, 'volume_24h': 61894813342,
                'market_cap': 1079125022056},
               {'timestamp': '2021-05-09T20:00:00Z', 'price': 57922.38, 'volume_24h': 62351429539,
                'market_cap': 1083442714226},
               {'timestamp': '2021-05-09T21:00:00Z', 'price': 58193.44, 'volume_24h': 63028207259,
                'market_cap': 1088515650604},
               {'timestamp': '2021-05-09T22:00:00Z', 'price': 58399.51, 'volume_24h': 63082754013,
                'market_cap': 1092371937086},
               {'timestamp': '2021-05-09T23:00:00Z', 'price': 58479.23, 'volume_24h': 63496464027,
                'market_cap': 1093863948485},
               {'timestamp': '2021-05-10T00:00:00Z', 'price': 58611.26, 'volume_24h': 64202465213,
                'market_cap': 1096337008403},
               {'timestamp': '2021-05-10T01:00:00Z', 'price': 59052.41, 'volume_24h': 65331346676,
                'market_cap': 1104592932060},
               {'timestamp': '2021-05-10T02:00:00Z', 'price': 59076.65, 'volume_24h': 65237671588,
                'market_cap': 1105049551735},
               {'timestamp': '2021-05-10T03:00:00Z', 'price': 59520.15, 'volume_24h': 65767597328,
                'market_cap': 1113347675423},
               {'timestamp': '2021-05-10T04:00:00Z', 'price': 59492.69, 'volume_24h': 64673794143,
                'market_cap': 1112837758726},
               {'timestamp': '2021-05-10T05:00:00Z', 'price': 59246.58, 'volume_24h': 63264532420,
                'market_cap': 1108238066299},
               {'timestamp': '2021-05-10T06:00:00Z', 'price': 59188.36, 'volume_24h': 63434006406,
                'market_cap': 1107151193337},
               {'timestamp': '2021-05-10T07:00:00Z', 'price': 58986.83, 'volume_24h': 63288842407,
                'market_cap': 1103384864564},
               {'timestamp': '2021-05-10T08:00:00Z', 'price': 58556.07, 'volume_24h': 63705656538,
                'market_cap': 1095329802757},
               {'timestamp': '2021-05-10T09:00:00Z', 'price': 58439.17, 'volume_24h': 63841785669,
                'market_cap': 1093145090727}]
