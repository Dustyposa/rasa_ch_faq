# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import random
from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

import cpca
import requests

QUERY_KEY = ""

CITY_LOOKUP_URL = "https://geoapi.qweather.com/v2/city/lookup"
WEATHER_URL = "https://devapi.qweather.com/v7/weather/now"


class ActionQueryWeather(Action):

    def name(self) -> Text:
        return "action_query_weather"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_in = tracker.latest_message.get("text")
        province, city = cpca.transform([user_in]).loc[0, ["省", "市"]]
        city = province if city in ["市辖区", None] else city
        text = self.get_weather(self.get_location_id(city))
        dispatcher.utter_message(text=text)
        return []

    @staticmethod
    def get_location_id(city):
        if not QUERY_KEY:
            raise ValueError("需要获得自己的key。。。看一下官方文档即可。 参考地址: qweather.com")
        params = {"location": city, "key": QUERY_KEY}
        return requests.get(CITY_LOOKUP_URL, params=params).json()["location"][0]["id"]
        # return 124

    @staticmethod
    def get_weather(location_id):
        params = {"location": location_id, "key": QUERY_KEY}
        res = requests.get(WEATHER_URL, params=params).json()["now"]
        # res = {'code': '200', 'updateTime': '2021-04-12T13:47+08:00', 'fxLink': 'http://hfx.link/2bc1',
        #        'now': {'obsTime': '2021-04-12T13:25+08:00', 'temp': random.randint(10, 30), 'feelsLike': '19',
        #                'icon': '305', 'text': '小雨', 'wind360': '315', 'windDir': '西北风', 'windScale': '0',
        #                'windSpeed': '0', 'humidity': '100', 'precip': '0.1', 'pressure': '1030', 'vis': '3',
        #                'cloud': '91', 'dew': '16'},
        #        'refer': {'sources': ['Weather China'], 'license': ['no commercial use']}}
        # res = res["now"]
        return f"{res['text']} 风向 {res['windDir']}\n温度: {res['temp']} 摄氏度\n体感温度：{res['feelsLike']}"


class ValidateRestaurantForm(FormValidationAction):
    """validation action 示例"""

    def name(self) -> Text:
        return "validate_饭店_form"

    @staticmethod
    def cuisine_db() -> List[Text]:
        """数据库支持的餐种 cuisines."""

        return [
            "西餐",
            "中餐",
            "泰餐",
            "火锅",
            "串串",
            "川菜",
            "粤菜",
            "本帮",
            "麻辣烫",
            "湘菜",
            "日料",
        ]

    @staticmethod
    def is_int(string: Text) -> bool:
        """检查 string 是一个 integer."""

        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_cuisine(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """检查 cuisine 值"""
        print(f"slots: {tracker.current_slot_values()}, value: {value}")
        if value.lower() in self.cuisine_db():
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"cuisine": value}
        else:
            dispatcher.utter_message(template="utter_wrong_cuisine")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"cuisine": None}

    def validate_num_people(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """检查 num_people 值"""
        value = next(tracker.get_latest_entity_values("number"), None)
        if self.is_int(value) and int(value) > 0:
            return {"num_people": value}
        else:
            dispatcher.utter_message(template="utter_wrong_num_people")
            # validation failed, set slot to None
            return {"num_people": None}

    def validate_outdoor_seating(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """检查 outdoor_seating 值"""

        if isinstance(value, str):
            if "外面" in value:
                # convert "out..." to True
                return {"outdoor_seating": True}
            elif "里面" in value:
                # convert "in..." to False
                return {"outdoor_seating": False}
            else:
                dispatcher.utter_message(template="utter_wrong_outdoor_seating")
                # validation failed, set slot to None
                return {"outdoor_seating": None}

        else:
            # affirm/deny was picked up as True/False by the from_intent mapping
            return {"outdoor_seating": value}


class ClearRestaurantFormSlot(Action):
    """清除掉上次收集的 slots"""
    def name(self) -> Text:
        return "action_clear_饭店_form_slots"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        clear_slots = domain.get("forms", {}).get('饭店_form', {}).keys()
        slots_data = domain.get("slots")
        return [SlotSet(slot_name, slots_data.get(slot_name)['initial_value']) for slot_name in clear_slots]


if __name__ == '__main__':
    # params = {"location": "上海", "key": QUERY_KEY}
    # print(requests.get(CITY_LOOKUP_URL, params=params).json()["location"][0]["id"])
    params = {"location": 101020100, "key": QUERY_KEY}
    print(requests.get(WEATHER_URL, params=params).json())
