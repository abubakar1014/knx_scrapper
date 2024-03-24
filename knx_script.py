import requests

cookies = {
    'Cookie-Navigator--enabled': 'accepted',
    'Cookie-Navigator--Google-Analytics--disable': 'false',
    'Cookie-Navigator--Facebook-Pixel--disable': 'false',
    'Cookie-Navigator--Hotjar--disable': 'false',
    'Cookie-Navigator--YouTube--Wall': 'false',
    'Cookie-Navigator--Google-Maps--Wall': 'false',
    '_gcl_au': '1.1.534571940.1708362628',
    '_fbp': 'fb.1.1708362629210.1560213889',
    '_hjSessionUser_346379': 'eyJpZCI6ImY4ZjNkNTQzLTNjZTAtNTE4OS05MWU0LTA5Mjg5N2I2MTQ5OCIsImNyZWF0ZWQiOjE3MDgzNjI2MjkxNDksImV4aXN0aW5nIjp0cnVlfQ==',
    '_gid': 'GA1.2.2052715013.1709735112',
    'WSESSIONID': 'mout38393q9rfbromjql0v0o9a',
    '_hjSession_346379': 'eyJpZCI6Ijg1N2E2YTIxLTQwMjYtNDk4Zi1hN2I3LTQ4MjgxNjg4ODI3YSIsImMiOjE3MDk3NTM3MzcwNDYsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MX0=',
    '_gat_UA-5200821-3': '1',
    '_gat_UA-5200821-1': '1',
    '_ga_MP426EDT14': 'GS1.1.1709753737.3.1.1709753782.15.0.0',
    '_ga_G92MED9JS9': 'GS1.1.1709753737.3.1.1709753782.15.0.0',
    '_ga_NKNYYNG0S3': 'GS1.1.1709753737.3.1.1709753783.0.0.0',
    '_ga': 'GA1.2.1557507222.1708362629',
}

headers = {
    'authority': 'www.knx.org',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en-US,en;q=0.9',
    # 'cookie': 'Cookie-Navigator--enabled=accepted; Cookie-Navigator--Google-Analytics--disable=false; Cookie-Navigator--Facebook-Pixel--disable=false; Cookie-Navigator--Hotjar--disable=false; Cookie-Navigator--YouTube--Wall=false; Cookie-Navigator--Google-Maps--Wall=false; _gcl_au=1.1.534571940.1708362628; _fbp=fb.1.1708362629210.1560213889; _hjSessionUser_346379=eyJpZCI6ImY4ZjNkNTQzLTNjZTAtNTE4OS05MWU0LTA5Mjg5N2I2MTQ5OCIsImNyZWF0ZWQiOjE3MDgzNjI2MjkxNDksImV4aXN0aW5nIjp0cnVlfQ==; _gid=GA1.2.2052715013.1709735112; WSESSIONID=mout38393q9rfbromjql0v0o9a; _hjSession_346379=eyJpZCI6Ijg1N2E2YTIxLTQwMjYtNDk4Zi1hN2I3LTQ4MjgxNjg4ODI3YSIsImMiOjE3MDk3NTM3MzcwNDYsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MX0=; _gat_UA-5200821-3=1; _gat_UA-5200821-1=1; _ga_MP426EDT14=GS1.1.1709753737.3.1.1709753782.15.0.0; _ga_G92MED9JS9=GS1.1.1709753737.3.1.1709753782.15.0.0; _ga_NKNYYNG0S3=GS1.1.1709753737.3.1.1709753783.0.0.0; _ga=GA1.2.1557507222.1708362629',
    'referer': 'https://www.knx.org/knx-en/for-professionals/community/partners/index.php?country=',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

params = {
    'type': 'json',
    'country': '',
    'per_page': '20',
    'qualification': 'total',
}


total_count = 122216
total_loop = int(total_count/20)
total_loop += 2
increment_count = 120000
real_records = []
for x in range(total_loop):
    increment_count += 60
    params["per_page"] = increment_count
    response = requests.get(
    'https://www.knx.org/knx-en/for-professionals/community/partners/index.php',
    params=params,
    cookies=cookies,
    headers=headers,
    )
    json_response = response.json()
    for record in json_response["rows"]:
        real_records.append(record)   
    import pdb
    pdb.set_trace()


[record['company'] for record in real_records]