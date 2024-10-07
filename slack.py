import requests
import json


class Slack(object):
    SLACK_URL = 'https://hooks.slack.com/services/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'


    def post(self, message):

        payload = {"text": message}
        try:
            response = requests.post(Slack.SLACK_URL, json=payload,
                                     headers={'Content-type': 'application/json'})

            if response.status_code != 200:
                print('http error code: {0}'.format(response.status_code))
                return False
            else:
                return True
        except (ValueError, KeyError, TypeError, AttributeError) as e:
            print(e)
            return False
        return False


if __name__ == "__main__":
    s = Slack()
    print(s.post("I am testing message by Ahmad."))
