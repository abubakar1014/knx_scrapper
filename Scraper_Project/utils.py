from slack.errors import SlackApiError
from slack import WebClient
SLACK_API_TOKEN = "xoxb-6572192356949-6601582477027-YFZ1QIYUayf0mInJwYbyNncU"

def template_view(new_entries):
    fields = ["company_name", "owner_name", "address", "phone_number", "mobile_number", "website", "email", "location"]
    greet = ":robot_face: *Scraping Status Report* :arrows_counterclockwise: \n *New Companies*\n"
    flds = ""

    for x in new_entries:
        for count, i in enumerate(x):
            flds += f"{fields[count]}:   {i}\n"

        flds += f"\n \n"

    note = "If you have any questions or concerns, feel free to reach out. Let's keep those scrapers running smoothly! :rocket:"
    return str(greet) + str(flds) + str(note)

def send_message(new_entries, channel='#new-companies_updates'):
    client = WebClient(token=SLACK_API_TOKEN)
    template = template_view(new_entries)
    try:
        client.chat_postMessage(channel=channel, text=f"{template}")
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")
