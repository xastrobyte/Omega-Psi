from util.image.image import MemeTemplate

# IMAGE = "https://lh3.googleusercontent.com/70CdRIbwtm_58qoxp5MgpplMnDC8BDwoS89HNxohXKpY8kks-L6Tj0e2eKNFssUvmloaFCUppnpyGEeh3CjLVEKVxmwZsxZmCMrFExcxIpPHlnOWaC2XrES8qeQw8FhZzOeCN7_KqutzjOkh6Q2jtAVR2VJON5aqb8btX2gUWW6IjkGBw9oVqdzcIqAj-RP8GYNZGoG3FIEZIgq1XWnCFnXO9YGHF_CSsR_mTPxHZs3KORNBN2UGaxYWJOSXczWUHTW_jwd3qgxwhFnUj5dn1O8rqgKHCG3FoKzFPO77f7dSLd9RiTbFD7oRYJ2QmkuEgr7G3r-8ujQEimoLesJLLhVDiiC-JOWdP0ZfXR96KI4dpme35v01jCbA3rLlMFqQKUjpLKG6yaCe855BQ0dyMR5kjM10cuiGGFDaABhMQ0PksdumZF4GO1UVav9CfUHA99CTPlq9MxrO094YpuYQ_ElSXDMATjFjORbA3Hv194DZ5BGZQZh8qxRguzCpJhO52yXZEElaHPiiyXPvyVomhDWcF6CaDLXztnZF6teMxVrkiIlDRZEU133TOV2u9wbqUdI-a7nEsib5GfU6-PeleDVQAI5TOpv1SsACBd3_N76ZmypoQk4j-J_rcexa--U-M1HQuQg9DTIoj53fl9EtQDiXlY4OGmAA4Urgrj9CIz6ZGclWL6RsBzVC84OIkGhyAm0n2h2vd95RI5RFwZLQPh_sgcgv9d_Re2P11w=w940-h889-no"
IMAGE = "https://tinyurl.com/carSkidding"


carSkidding = MemeTemplate(
    "car skidding",
    IMAGE,
    {
        "carText": {
            "location": [450, 660], "angle": 0,
            "color": [255, 255, 255], "size": 60,
            "max": 10
        },
        "straightText": {
            "location": [285, 210], "angle": 0,
            "color": [255, 255, 255], "size": 60,
            "max": 10
        },
        "exitText": {
            "location": [570, 210], "angle": 0,
            "color": [255, 255, 255], "size": 60,
            "max": 10
        }
    }
)

def generateImage(carText, straightText, exitText):
    return carSkidding.generateImage(
        carText = carText,
        straightText = straightText,
        exitText = exitText
    )