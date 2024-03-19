from django.db import models
from threading import Thread
from selenium import webdriver
from datetime import datetime
from django.utils import timezone
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True
        
def configure_webdriver(open_browser=False, block_media=False, block_elements=['css', 'img', 'js']):
    options = webdriver.ChromeOptions()

    # Install the extension
    extension_path = 'knx/pia.crx'

    if not open_browser:
        options.add_argument("--headless=new")
    if block_media:
        hide_elements = {
            'plugins': 2, 'popups': 2, 'geolocation': 2, 'notifications': 2,
            'auto_select_certificate': 2, 'fullscreen': 2, 'mouselock': 2, 'mixed_script': 2,
            'media_stream': 2, 'media_stream_mic': 2, 'media_stream_camera': 2,
            'protocol_handlers': 2, 'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2,
            'push_messaging': 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2,
            'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement': 2, 'durable_storage': 2
        }
        if 'cookies' in block_elements:
            hide_elements.update({'cookies': 2})
        if 'js' in block_elements:
            hide_elements.update({'javascript': 2})
        if 'img' in block_elements:
            hide_elements.update({'images': 2})
        prefs = {'profile.default_content_setting_values': hide_elements}
        options.add_argument('--disable-features=EnableNetworkService')
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_experimental_option('prefs', prefs)
    options.add_argument("window-size=1200,1100")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36")

    options.add_extension(extension_path)

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.maximize_window()

    if block_media:
        # Enable Chrome DevTools Protocol
        driver.execute_cdp_cmd("Page.enable", {})
        driver.execute_cdp_cmd("Network.enable", {})

        # Set blocked URL patterns to disable images and stylesheets
        blocked_patterns = []
        if 'img' in block_elements:
            blocked_patterns.extend(["*.jpg", "*.jpeg", "*.png", "*.gif", ])
        if 'css' in block_elements:
            blocked_patterns.extend(["*.css"])
        if 'js' in block_elements:
            blocked_patterns.extend(["*.js"])
        driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": blocked_patterns})
    return driver


def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return decorator

def parse_date(date):
    human_readable_date = str(date).split(' ')[0]
    return human_readable_date

COUNTRIES   = {
    0: "N/A",
    5: "Ethiopia",
    6: "Kenya",
    7: "Madagascar",
    9: "Mauritius",
    11: "Mozambique",
    12: "Réunion",
    14: "Seychelles",
    15: "Somalia",
    16: "Tanzania, United Republic of",
    17: "Uganda",
    20: "Angola",
    21: "Cameroon",
    25: "Congo, Democratic Republic of the",
    29: "Algeria",
    30: "Egypt",
    31: "Libya",
    32: "Morocco",
    33: "Sudan",
    34: "Tunisia",
    36: "Botswana",
    37: "Lesotho",
    38: "Namibia",
    39: "South Africa",
    40: "Swaziland",
    41: "Benin",
    42: "Burkina Faso",
    44: "Cote d'Ivoire",
    46: "Ghana",
    47: "Guinea",
    50: "Mali",
    53: "Nigeria",
    55: "Senegal",
    57: "Togo",
    60: "Aruba",
    65: "Cuba",
    67: "Dominican Republic",
    68: "Grenada",
    69: "Guadeloupe",
    71: "Jamaica",
    72: "Martinique",
    74: "Netherlands Antilles",
    77: "Saint Lucia",
    82: "Belize",
    83: "Costa Rica",
    84: "El Salvador",
    85: "Guatemala",
    87: "Mexico",
    89: "Panama",
    90: "Argentina",
    91: "Bolivia",
    92: "Brazil",
    93: "Chile",
    94: "Colombia",
    95: "Ecuador",
    97: "French Guiana",
    99: "Paraguay",
    100: "Peru",
    101: "Suriname",
    102: "Uruguay",
    103: "Venezuela",
    105: "Canada",
    106: "Greenland",
    108: "United States",
    109: "China",
    110: "China - Hong Kong Special Administrative Region",
    111: "China - Macao Special Administrative Region",
    112: "Japan",
    114: "Korea, Republic of",
    115: "Mongolia",
    116: "Taiwan",
    118: "Bangladesh",
    120: "India",
    121: "Iran, Islamic Republic of",
    122: "Kazakhstan",
    123: "Kyrgyzstan",
    124: "Maldives",
    125: "Nepal",
    126: "Pakistan",
    127: "Sri Lanka",
    128: "Tajikistan",
    129: "Turkmenistan",
    130: "Uzbekistan",
    131: "Brunei Darussalam",
    132: "Cambodia",
    133: "Indonesia",
    134: "Lao People's Democratic Republic",
    135: "Malaysia",
    136: "Myanmar",
    137: "Philippines",
    138: "Singapore",
    139: "Thailand",
    140: "Timor-Leste",
    141: "Viet Nam",
    142: "Armenia",
    143: "Azerbaijan",
    144: "Bahrain",
    145: "Cyprus",
    146: "Georgia",
    147: "Iraq",
    148: "Israel",
    149: "Jordan",
    150: "Kuwait",
    151: "Lebanon",
    152: "Palestinian Territory, Occupied",
    153: "Oman",
    154: "Qatar",
    155: "Saudi Arabia",
    156: "Syria",
    157: "Turkey",
    158: "United Arab Emirates",
    159: "Yemen",
    160: "Belarus",
    161: "Bulgaria",
    162: "Czech Republic",
    163: "Hungary",
    164: "Moldova, Republic of",
    165: "Poland",
    166: "Romania",
    167: "Russian Federation",
    168: "Slovakia",
    169: "Ukraine",
    170: "Aland Islands",
    171: "Denmark",
    172: "Estonia",
    173: "Faeroe Islands",
    174: "Finland",
    175: "Guernsey",
    176: "Iceland",
    177: "Ireland",
    178: "Jersey",
    179: "Latvia",
    180: "Lithuania",
    181: "Man, Isle of",
    182: "Norway",
    183: "Svalbard and Jan Mayen Islands",
    184: "Sweden",
    185: "United Kingdom",
    186: "Albania",
    187: "Andorra",
    188: "Bosnia and Herzegovina",
    189: "Croatia",
    190: "Gibraltar",
    191: "Greece",
    193: "Italy",
    194: "Macedonia",
    195: "Malta",
    196: "Montenegro",
    197: "Portugal",
    198: "San Marino",
    199: "Serbia",
    200: "Slovenia",
    201: "Spain",
    202: "Austria",
    203: "Belgium",
    204: "France",
    205: "Germany",
    206: "Liechtenstein",
    207: "Luxembourg",
    208: "Monaco",
    209: "Netherlands",
    210: "Switzerland",
    211: "Australia",
    214: "New Zealand",
    217: "New Caledonia",
    229: "Cook Islands",
    230: "French Polynesia",
    241: "French Southern Territories",
    245: "Spain - Canary Islands",
    246: "Kosovo",
    247: "Saint Barthélemy",
    249: "Bonaire",
    252: "Curaçao",
    253: "N/A",
}