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
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

from knx.models import ProfileData
from knx.utils import configure_webdriver
from knx.utils import start_new_thread


def accept_cookie(driver):
    try:
        btns = driver.find_element(By.CLASS_NAME, "cookieButtons")
        btns.find_elements(By.TAG_NAME, "button")[1].click()
        time.sleep(2)
    except:
        pass

def load_jobs(driver):
    flag = True
    count = 0
    while(flag):
        if count > 20:
            flag = False
        count += 1
        try:
            load = driver.find_elements(By.CLASS_NAME, "load_more")
            if len(load)>0:
                time.sleep(1)
                load[0].click()
            else:
                flag = False
        except:
            flag = False
            print("")

def append_data(data, comp):
    data.append(str(comp[0]).strip("+"))
    data.append(str(comp[1]).strip("+"))
    data.append(str(comp[3]).strip("+"))
    data.append(str(comp[4]).strip("+"))
    if 'Mobile:' in comp[5]:
        data.append(str(comp[5]).strip("+"))
    else:
        data.append(str("N/A").strip("+"))
    return data

def scrap_jobs(driver):
    time.sleep(2)
    scrapped_data = []
    try:
        companies = driver.find_elements(By.CLASS_NAME, "accordion-list-item")
        driver.execute_script("window.scrollTo(0, 0);")
    except:
        pass
    for company in companies:
        try:
            data = []
            company.click()
            comp = company.text.split('\n')
            data = append_data(data, comp)
            web = company.find_element(By.CLASS_NAME, "partner-col-2")
            website = web.find_element(By.TAG_NAME, "a").get_attribute('href')
            data.append(str(website).strip("+"))
            links = company.find_elements(By.CLASS_NAME, "link_to_map")
            links[1].get_attribute('href')
            data.append(str(links[0].get_attribute('href')).strip("+"))
            data.append(str(links[1].get_attribute('href')).strip("+"))
            scrapped_data.append(data)
            company.location_once_scrolled_into_view
            time.sleep(2)
        except:
            pass
    return scrapped_data

def index(request):
    # run_fun_in_loop()
    print("Function called in a seperate thread")
    return render(request, 'home.html')

def profiles(request):
    profiles = ProfileData.objects.all()
    return render(request, 'show_data.html',{'profiles':profiles})
    
    
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


def start_script():
    total_data = 0
    try:
        driver = configure_webdriver(True)
        driver.maximize_window()
        url = "https://www.knx.org/knx-en/for-professionals/community/partners/index.php"
        driver.get(url)
        accept_cookie(driver)
        load_jobs(driver)
        start_time = datetime.datetime.now()
        scraped_data = scrap_jobs(driver)
        driver.quit()
        user_profiles = [ProfileData(company_name=profile[0], owner_name=profile[1], address=profile[2], phone_number=profile[3], mobile_number=profile[4], website=profile[5], email=profile[6], location=profile[7]) for profile in scraped_data]
        print(f"Total Scrapped Data is : {len(user_profiles)}")
        ProfileData.objects.bulk_create(user_profiles, ignore_conflicts=True)
        end_time = datetime.datetime.now()
        newly_objects = ProfileData.objects.filter(created_at__range=(start_time, end_time))
        if len(newly_objects) > 0:
            new_entries = [[x.company_name,x.owner_name,x.address,x.phone_number,x.mobile_number,x.website,x.email,x.location]for x in newly_objects]
            append_values(
                "1dfjWG-rWG1J6_hFA8QIOQzRCALE_eTZlBlLG5xkDcYU",
                "Sheet1",
                "USER_ENTERED",
                new_entries,
                )
            print(f"Saved in database objects are : {newly_objects.count()}")
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
