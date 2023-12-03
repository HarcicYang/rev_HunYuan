import requests, sys
from collections import deque


class HunYuan:
    def __init__(self, cookie: str, chatId: str = "new", isAutoRecreateChatId: bool = True):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cookie": cookie}
        if chatId == "new":
            self.chatId = requests.post("https://hunyuan.tencent.com/api/generate/id", headers=self.headers).text
        else:
            self.chatId = chatId
        self.url = "https://hunyuan.tencent.com/api/chat/" + self.chatId
        self.history_url = "https://hunyuan.tencent.com/api/conv/" + self.chatId
        self.delete_url = "https://hunyuan.tencent.com/api/conv/delete" + self.chatId
        self.isAutoRecreateChatId = isAutoRecreateChatId

    def ask(self, prompt: str, model: str = "gpt_175B_0404", isSkipHistory: bool = False):
        response = requests.get(self.history_url, headers=self.headers)
        if self.isAutoRecreateChatId:
            try:
                if len(response.json()["convs"]) == 40:
                    requests.get(self.delete_url, headers=self.headers)
                    self.chatId = requests.get("https://hunyuan.tencent.com/api/generate/id", headers=self.headers).text
                    self.url = "https://hunyuan.tencent.com/api/chat/" + self.chatId
                    self.history_url = "https://hunyuan.tencent.com/api/conv/" + self.chatId
                    self.delete_url = "https://hunyuan.tencent.com/api/conv/delete" + self.chatId
            except:
                pass
        Payload = {
            "model": model,
            "prompt": prompt,
            "displayPrompt": prompt,
            "displayPromptType": 1,
            "plugin": "Adaptive",
            "isSkipHistory": isSkipHistory
        }
        response = requests.post(self.url, headers=self.headers, json=Payload)
        if response.status_code != 200:
            print(Payload)
            print(self.url)
            raise ConnectionError
        response = requests.get(self.history_url, headers=self.headers)
        if response.status_code != 200:
            raise ConnectionError
        raw_result = deque(response.json()["convs"]).pop()["speechesV2"][0]["content"]
        if raw_result[0]["type"] == "text":
            result = {"text": raw_result[0]["msg"], "images": []}
        elif raw_result[0]["type"] == "image":
            images = []
            for i in raw_result:
                try:
                    imgUrlLow = i["imageUrlLow"]
                    imgUrlHigh = i["imageUrlHigh"]
                    imgList = {"highImgUrl": imgUrlHigh, "lowImgUrl": imgUrlLow}
                    images.append(imgList)
                except Exception:
                    pass
            result = {"text": "这是一条图片信息", "images": images}
        else:
            result = {"text": "未知信息", "images": []}
        return result

    def stream(self):
        try:
            while 1:
                prompt = input("You: ")
                print(self.ask(prompt))
        except KeyboardInterrupt:
            sys.exit()


