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
from collections import Counter
import re
from Scraper_Project.utils import send_message
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

from knx.models import ProfileData, ScraperDetail, UrlCount
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
            # print(f"Load More Count is : {start_count}")
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
    
def check_count(driver, link, all):
    driver.get(link)
    time.sleep(1)
    accept_cookie(driver)
    time.sleep(1)
    list_count = driver.find_element(By.CLASS_NAME, "total-selected").find_element(By.TAG_NAME, "b").text
    if all:
        if UrlCount.objects.filter(count=list_count, url=link).exists():
            return False
        UrlCount.objects.all().update(count=list_count, url=link)
        return True
    else:
        if ScraperDetail.objects.filter(count=list_count, url=link).exists():
            return False
        ScraperDetail.objects.filter(url=link).update(count=list_count, url=link)
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
    unique_entries = {}
    for sublist in data:
        key = tuple(sublist[i] for i in [0, 3])
        fourth_element = sublist[3]
        sixth_element = sublist[6]
        if key not in unique_entries:
            unique_entries[key] = sublist
        else:
            if "http" not in sixth_element and "http" in unique_entries[key][6]:
                unique_entries[key] = sublist
            elif "http" not in sixth_element and "http" not in unique_entries[key][6]:
                continue
    unique_comp = list(unique_entries.values())
    for x in unique_comp:
        phone = x[3]
        mobile = x[4]
        if '+' in phone:
            x[3]= "'"+phone
        if '+' in mobile:
            x[4]= "'"+mobile
    
    # user_profiles = [ProfileData(company_name=profile[0], owner_name=profile[1], address=profile[2], phone_number=profile[3], mobile_number=profile[4], website=profile[5], email=profile[6], location=profile[7], city=profile[8], country=profile[9]) for profile in unique_comp]    
    # print(f"Total Scrapped Data is : {len(user_profiles)}")
    # ProfileData.objects.bulk_create(user_profiles, ignore_conflicts=True, batch_size=500)
    # time.sleep(5)
    # end_time = datetime.datetime.now()
    # newly_objects = ProfileData.objects.filter(created_at__range=(start_time, end_time))
    # if len(newly_objects) > 0:
    #     new_entries = [[x.company_name,x.owner_name,x.address,"'"+x.phone_number if x.phone_number != "N/A" else x.phone_number,"'"+x.mobile_number if x.mobile_number != "N/A" else x.mobile_number, x.website,x.email,x.location,x.city,x.country,parse_date(x.created_at)]for x in newly_objects]
    #     # send_message(new_entries)
    #     append_values(
    #         "1dfjWG-rWG1J6_hFA8QIOQzRCALE_eTZlBlLG5xkDcYU",
    #         "Sheet1",
    #         "USER_ENTERED",
    #         new_entries,
    #         )
    append_values(
            "1dfjWG-rWG1J6_hFA8QIOQzRCALE_eTZlBlLG5xkDcYU",
            "Sheet1",
            "USER_ENTERED",
            unique_comp,
            )

def start_script():
    try:
        driver = configure_webdriver()
        scraper = UrlCount.objects.filter()
        if not scraper.exists():
            scraper.create(count=0)
        link = "https://www.knx.org/knx-en/for-professionals/community/partners/index.php"
        if check_count(driver, link, True):
            driver.quit()
            links = ScraperDetail.objects.all().only('url').values() #Uzair check kr lena y proper working kr ra h k ni 
            for count, link in enumerate(links):
                if count > 0:
                    driver = configure_webdriver()
                    if check_count(driver, link["url"], False):
                        print(f"\n\n\n\n\nQuery number {count + 1} running\n\n\n\n")
                        driver.get(link["url"])
                        accept_cookie(driver)
                        sort_qualification(driver)
                        print("SCRAPING_ENDED")
                    driver.quit()
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