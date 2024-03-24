from slack.errors import SlackApiError
from slack import WebClient
# SLACK_API_TOKEN = "xoxb-6572192356949-6601582477027-eZzc5s7J76A1OTO4zlUCI08F"
SLACK_API_TOKEN = "xoxb-6574189581427-6633200010276-HCEy0DxjZjVXYYSxULHs4eOc"


def template_view(new_entries):
    fields = ["uid", "id", "salutation_id", "stars", "stars_feedback", "stars_projects", "stars_engagement", "stars_tools", "stars_knowledge", "score_feedback", "score_projects", "score_engagement", "score_tools", "score_knowledge", "score", "visible", "visible_list", "visible_map", "national_group_visible", "username", "firstname", "lastname", "company", "phone", "mobile", "street", "housenumber", "zipcode", "city", "country_name", "vat", "email", "website", "language", "longitude", "latitude", "communication_journal", "communication_journal_language_id", "country_id","Created_at"]
    greet = ":robot_face: *Scraping Status Report* :arrows_counterclockwise: \n *New Companies*\n"
    flds = ""

    for x in new_entries:
        for count, i in enumerate(x):
            flds += f"{fields[count]}:   {i}\n"

        flds += f"\n \n"

    note = "If you have any questions or concerns, feel free to reach out. Let's keep those scrapers running smoothly! :rocket:"
    return str(greet) + str(flds) + str(note)

def send_message(new_entries, channel='#knx-scraping-updates'):
    client = WebClient(token=SLACK_API_TOKEN)
    # new_entries = [[i for i in entry if i] for entry in new_entries]
    template = template_view(new_entries)
    try:
        client.chat_postMessage(channel=channel, text=f"{template}")
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")


def send_message_error(message, channel='#knx-scraping-updates'):
    client = WebClient(token=SLACK_API_TOKEN)
    # template = template_view(new_entries)
    try:
        client.chat_postMessage(channel=channel, text=f"{message}")
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")