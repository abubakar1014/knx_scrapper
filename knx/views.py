from django.shortcuts import render,redirect
from django.http import HttpResponse
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium import webdriver
import datetime
import time
import pandas as pd
import re
from Scraper_Project.utils import send_message
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

from knx.models import ProfileData, ScraperDetail
from knx.utils import configure_webdriver, parse_date
from knx.utils import start_new_thread


def accept_cookie(driver):
    try:
        btns = driver.find_element(By.CLASS_NAME, "cookieButtons")
        btns.find_elements(By.TAG_NAME, "button")[1].click()
        time.sleep(2)
    except:
        pass

def load_jobs(driver):
    data = []
    flag = True
    start_count = 0
    while(flag):
        try:
            start_count += 1
            print(f"Load More Count is : {start_count}")
            scraped_data = scrap_jobs(driver)
            data += scraped_data
            load = driver.find_elements(By.CLASS_NAME, "load_more")
            time.sleep(1)
            load[0].click()
        except Exception as e:
            print(e)
            flag = False
    return data

def append_data(data, comp):
    data.append(str(comp[1]).strip("+"))
    address = comp[2] + " " + comp[3]
    data.append(str(address).strip("+"))
    if '+' in comp[4]:
        data.append(str(comp[4].strip('Phone: ').strip('Mobile: ')).strip(","))
    else:
        data.append(str("N/A").strip("+"))
    if 'Mobile:' in comp[5]:
        if '+' in comp[5]:
            data.append(str(comp[4].strip('Mobile: ').strip('Phone: ')).strip(","))
        else:
            data.append(str("N/A").strip("+"))
    else:
        data.append(str("N/A").strip("+"))
    comp
    try:
        country = comp[3].split(', ')[-1]
    except:
        country = "N/A"
    return data, country

def scrap_jobs(driver):
    scrapped_data = []
    try:
        time.sleep(2)
        last_twenty = 20
        companies = driver.find_elements(By.CLASS_NAME, "accordion-list-item")[-last_twenty:]
        driver.execute_script("window.scrollTo(0, 0);")
        for company in companies:
            try:
                data = []
                company.click()
                country = ""
                name_comp = company.find_elements(By.TAG_NAME, "td")
                data.append(str(name_comp[0].text).strip("+"))
                comp = company.text.split('\n')
                data, country = append_data(data, comp)
                web = company.find_element(By.CLASS_NAME, "partner-col-2")
                website = web.find_element(By.TAG_NAME, "a").text
                if '.' in website:
                    data.append(str(website).strip("+"))
                else:
                    data.append(str("N/A").strip("+"))
                links = company.find_elements(By.CLASS_NAME, "link_to_map")
                if len(links) > 1:
                    data.append(str(links[0].get_attribute('href')).strip("+"))
                    data.append(str(links[1].get_attribute('href')).strip("+"))
                else:
                    mail = company.find_element(By.CLASS_NAME, "partner-col-2")
                    email = mail.find_elements(By.TAG_NAME, "span")[1].text
                    data.append(str(email.split('Email: ')[1]).strip("+"))
                    data.append(str(links[0].get_attribute('href')).strip("+"))
                city = str(name_comp[1].text).strip("+")  
                data.append(city)
                try:
                    value = driver.find_element(By.ID, "partner-list-app").find_element(By.CLASS_NAME, "top-buffer").find_element(By.CLASS_NAME, "country").find_element(By.TAG_NAME, "button").text
                    data.append(value)
                except:
                    value = "N/A"
                    data.append(value)
                scrapped_data.append(data)
                company.location_once_scrolled_into_view
            except:
                pass
        return scrapped_data
    except:
        return scrapped_data

def index(request): 
    # run_fun_in_loop()
    print("Function called in a seperate thread")
    return render(request, 'home.html')

def profiles(request):
    profiles = ProfileData.objects.all()
    return render(request, 'show_data.html', {'profiles':profiles})
    
    
def append_values(spreadsheet_id, range_name, value_input_option, values):
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = None
    if os.path.exists("knx/token.json"):
        credentials = Credentials.from_authorized_user_file("knx/token.json", SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("knx/credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)
            with open("knx/token.json", "w") as token:
                token.write(credentials.to_json())
    # pylint: disable=maybe-no-member
    try:
        service = build("sheets", "v4", credentials=credentials)

        body = {"values": values}
        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body,
            )
            .execute()
        )
        print(f"{result.get('updates').get('updatedCells')} cells appended.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error
    
def check_count():
    scraper = ScraperDetail.objects.filter()
    if not scraper.exists():
        scraper.create(count=0)
    driver = configure_webdriver()
    driver.get("https://www.knx.org/knx-en/for-professionals/community/partners/index.php")
    time.sleep(1)
    accept_cookie(driver)
    time.sleep(1)
    list_count = driver.find_element(By.CLASS_NAME, "total-selected").find_element(By.TAG_NAME, "b").text
    driver.quit()
    if ScraperDetail.objects.filter(count=list_count).exists():
        return False
    ScraperDetail.objects.all().update(count=list_count)
    return True

def sort_qualification(driver):
    data = []
    start_time = datetime.datetime.now()
    scraped_data = load_jobs(driver)
    data += scraped_data
    driver.execute_script("window.scrollTo(0, 0);")
    btn = driver.find_elements(By.CLASS_NAME, "dropdown-toggle")
    btn[1].click()
    fields = driver.find_elements(By.CLASS_NAME, "dropdown-menu")[-1]
    fields.find_elements(By.TAG_NAME, "a")[-1].click()
    scraped_data = load_jobs(driver)
    data += scraped_data
    driver.execute_script("window.scrollTo(0, 0);")
    first_occurrence = {}
    unique_list_of_lists = [entry for entry in data if not entry[6].startswith("https") or first_occurrence.setdefault(entry[0], entry) == entry]
    # unique_list_of_lists = [inner_list for inner_list in data if not inner_list[6].startswith("https")]
    user_profiles = [ProfileData(company_name=profile[0], owner_name=profile[1], address=profile[2], phone_number=profile[3], mobile_number=profile[4], website=profile[5], email=profile[6], location=profile[7], city=profile[8], country=profile[9]) for profile in unique_list_of_lists]    
    print(f"Total Scrapped Data is : {len(user_profiles)}")
    ProfileData.objects.bulk_create(user_profiles, ignore_conflicts=True, batch_size=500)
    end_time = datetime.datetime.now()
    newly_objects = ProfileData.objects.filter(created_at__range=(start_time, end_time))
    if len(newly_objects) > 0:
        new_entries = [[x.company_name,x.owner_name,x.address,"'"+x.phone_number if x.phone_number != "N/A" else x.phone_number,"'"+x.mobile_number if x.mobile_number != "N/A" else x.mobile_number, x.website,x.email,x.location,x.city,x.country,parse_date(x.created_at)]for x in newly_objects]
        # send_message(new_entries)
        append_values(
            "1dfjWG-rWG1J6_hFA8QIOQzRCALE_eTZlBlLG5xkDcYU",
            "Sheet1",
            "USER_ENTERED",
            new_entries,
            )

def start_script():
    try:
        if check_count():
            urls = [
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=148",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=193",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=112",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=178",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=149",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=122",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=6",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=114",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=246",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=150",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=123",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=134",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=179",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=151",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=37",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=31",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=206",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=180",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=207",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=194",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=7",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=135",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=124",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=50",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=195",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=181",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=72",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=9",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=87",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=164",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=208",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=115",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=196",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=32",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=11",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=136",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=38",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=125",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=209",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=74",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=217",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=214",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=53",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=182",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=153",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=126",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=152",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=89",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=99",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=100",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=137",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=165",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=197",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=154",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=12",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=166",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=167",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=247",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=77",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=198",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=155",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=55",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=199",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=14",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=138",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=168",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=200",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=15",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=39",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=201",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=245",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=127",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=33",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=101",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=183",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=40",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=184",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=210",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=156",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=116",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=128",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=16",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=139",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=140",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=57",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=34",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=157",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=129",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=17",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=169",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=158",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=185",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=108",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=102",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=130",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=103",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=141",
                    "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=159"
                    ]
            print(f"Total Queries are : {len(urls)}")
            for count, url in enumerate(urls):
                print(f"Query number {count + 1} running")
                driver = configure_webdriver()
                driver.get(url)
                accept_cookie(driver)
                sort_qualification(driver)
                driver.quit()
                print("SCRAPING_ENDED")
    except Exception as e:
        print(e)

@start_new_thread        
def run_fun_in_loop():
    print("yes called successfully")
    while(1):
        start_script()
        time.sleep(36000)
        
def scrape(request):
    run_fun_in_loop()
    print("Function called in a seperate thread")
    return redirect('index')



#Ali Waly Links

# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=148",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=193",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=112",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=178",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=149",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=122",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=6",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=114",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=246",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=150",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=123",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=134",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=179",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=151",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=37",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=31",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=206",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=180",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=207",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=194",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=7",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=135",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=124",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=50",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=195",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=181",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=72",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=9",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=87",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=164",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=208",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=115",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=196",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=32",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=11",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=136",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=38",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=125",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=209",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=74",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=217",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=214",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=53",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=182",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=153",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=126",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=152",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=89",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=99",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=100",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=137",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=165",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=197",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=154",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=12",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=166",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=167",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=247",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=77",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=198",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=155",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=55",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=199",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=14",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=138",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=168",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=200",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=15",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=39",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=201",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=245",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=127",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=33",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=101",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=183",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=40",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=184",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=210",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=156",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=116",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=128",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=16",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=139",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=140",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=57",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=34",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=157",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=129",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=17",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=169",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=158",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=185",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=108",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=102",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=130",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=103",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=141",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=159"



# My Links



# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=170",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=186",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=29",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=187",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=20",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=90",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=142",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=60",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=211",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=202",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=143",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=144",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=118",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=160",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=203",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=82",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=41",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=91",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=249",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=188",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=36",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=92",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=131",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=161",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=42",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=132",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=21",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=105",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=93",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=109",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=110",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=111",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=94",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=25",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=229",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=83",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=44",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=189",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=65",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=252",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=145",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=162",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=171",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=67",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=95",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=30",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=84",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=172",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=173",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=174",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=204",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=97",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=230",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=241",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=146",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=205",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=46",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=190",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=191",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=106",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=68",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=69",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=85",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=175",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=47",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=163",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=176",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=120",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=133",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=121",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=147",
# "https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=177",
