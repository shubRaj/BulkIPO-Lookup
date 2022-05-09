import requests
import base64
import json
from requests.auth import HTTPBasicAuth
# curl -X POST -u "apikey:<API-KEY>" --header "Content-Type: audio/wav" --data-binary @test.wav "https://api.jp-tok.speech-to-text.watson.cloud.ibm.com/instances/40fdcffc-2720-4001-992a-4badd27776c4/v1/recognize"


class NepseIPOLookup:
    ALPHA_NUMBERS = {
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9"
    }

    def __init__(self, server, apikey):
        self._auth = HTTPBasicAuth('apikey', apikey)
        self._session = requests.Session()
        self._server = server

    def __captcha(self):
        data = self._session.get(
            "https://iporesult.cdsc.com.np/result/companyShares/fileUploaded").json()
        captcha = data["body"]["captchaData"]
        self.captcha_audio = captcha["audioCaptcha"]
        self.captcha_identifier = captcha["captchaIdentifier"]
        return self

    def __userCaptcha(self):
        text_response = self._session.post(f"{self._server}/v1/recognize", headers={
            "Content-Type": "audio/wav",
            'Accept': 'application/json',
        }, data=base64.b64decode(self.captcha_audio), auth=self._auth).json()["results"][0]["alternatives"][0]["transcript"]
        self.user_captcha = "".join(
            [self.ALPHA_NUMBERS[alpha.lower()]
             for alpha in text_response.split()]
        )
        return self

    def checkIPO(self, companyShareID, boid):
        # 5 retries
        for _ in range(5):
            self.__captcha()
            self.__userCaptcha()
            data = json.dumps({
                "companyShareId": companyShareID,
                "boid": boid,
                "userCaptcha": self.user_captcha,
                "captchaIdentifier": self.captcha_identifier
            })
            resp_message = self._session.post("https://iporesult.cdsc.com.np/result/result/check", headers={
                                              "Content-Type": "application/json"}, data=data).json()["message"]
            if "sorry" in resp_message.lower() or "congratulation" in resp_message.lower():
                break
        return resp_message


if __name__ == "__main__":
    nepse = NepseIPOLookup("<SERVER>", "<API_KEY>")
    print(nepse.checkIPO("<ORG>", "<BIOID>"))
