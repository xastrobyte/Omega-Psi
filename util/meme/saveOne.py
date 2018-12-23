from util.image.image import MemeTemplate

# IMAGE = "https://lh3.googleusercontent.com/A8DL1PjutxJYJHiqXtWSB6mZ9OEpvF_1l-U7sGUwRSt7vBopZT_N3uRMPUYxYilpYfzOCYLGOXStWkXqEYqVId_AeugUdZGrHFHPYprQBtLs9N_Vx5e4wlolkIpdLcZFQeQB4GCwrIPYbidAx3vSeqcSCb7amO-KoKogZMwlOnrzTclmEoZUCfHmO5m6z4fABTfCjOGdciImzxgRIVUmU0wpwO5jYPqhsIZ5TPqJE-KUAKNss2CQrJP9vcEKQj6uWyO8hss1j0DRp7kSiZsk1mIBVrlnNN3AiP_cYSuKsPtUp68YEvl8BWHlelIO6BgErS5uzQYRKErJYMOfxdFZxSbyA0t8AFBPry2LCL8FSE1yxmaKx42TgawRpYm9hHp-ToQifyhj2yCiokUy_1hu8fNcrsvM042mSCEZK44aSy4W3asYyObNnm06d6HRlu4d40en7Sx5ZWH1g3BTodV1d9-AwfzphZyZa_fdPRWZz7ajpBIvtUrO7xRRfuID_F6t1_7zK7RtnfrQSrbVenWsBEm3GknE8ErnXgxQdv9S0ZAbfzkxFsU1pOiPzga8kq1ORnRhtx20UGedqDtBtJzhBDmLMHKo-u-IylZ4AfoTit7ZVb7eIHy08YoQH_EZlKKc05qvYBz4Hw8eW-rXU24t0rsBdzzyQtgk4oDb8ocU6zlpbpnzHp9uP3zy0i9csN3pRhtK2XXF5WdDn4_XZK--N634r6KIgj-FV1kKiLk=w1013-h889-no"
IMAGE = "https://tinyurl.com/saveOneMeme"

saveOne = MemeTemplate(
    "save one",
    IMAGE,
    {
        "personText": {
            "location": [240, 250],
            "size": 80, "max": 15
        },
        "leftBehindText": {
            "location": [600, 235],
            "size": 60, "max": 10
        },
        "saveText": {
            "location": [900, 210],
            "size": 60, "max": 10
        }
    }
)

def generateImage(personText, leftBehindText, saveText):
    return saveOne.generateImage(
        personText = personText,
        leftBehindText = leftBehindText,
        saveText = saveText
    )