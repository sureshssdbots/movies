import logging

# लॉगिंग को कॉन्फ़िगर करें
logging.basicConfig(
    level=logging.DEBUG,  # लॉग का स्तर सेट करें (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # लॉग फॉर्मेट सेट करें
    handlers=[
        logging.StreamHandler(),  # कंसोल पर लॉग दिखाने के लिए
        logging.FileHandler('app.log')  # फ़ाइल में लॉग लिखने के लिए
    ]
)

# लॉगिंग की जांच के लिए एक प्रारंभिक संदेश
logging.info("Logging setup complete.")
