from typing import Text

from actions.utils.request import get, post

SEARCH_ANIME_URL = "https://trace.moe/api/search"


async def search_anime(url: Text) -> Text:
    try:
        url_type, url_data = url.split("_", maxsplit=1)
        if url_type == "u":
            res = await get(url=SEARCH_ANIME_URL, params={"url": url_data})
        else:
            res = await post(url=SEARCH_ANIME_URL, data={"image": url_data})
    except UnicodeDecodeError:
        return "搜索出错，请稍后再试"
    animes = res["docs"]
    if not animes:
        return "不好意思，没有搜出来呢～可以换一张试试哦"
    set_res = "\n".join(set(anime["anime"] for anime in animes))
    return f"可能来自下列动漫:\n {set_res}"


class AnimalImgSearch:
    @staticmethod
    async def get_dog_img():
        return (await get("https://aws.random.cat/meow"))["file"]

    @staticmethod
    async def get_cat_img():
        return (await get("https://randomfox.ca/floof/"))["image"]

    @staticmethod
    async def get_fox_img():
        return (await get("https://dog.ceo/api/breeds/image/random"))["message"]


if __name__ == '__main__':
    import time

    t1 = time.time()
    print(search_anime("https://i.loli.net/2021/05/08/6IqMaO3XYiQcBJd.png"))
    print(time.time() - t1)
