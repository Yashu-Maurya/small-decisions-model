"""Tool catalog and router patterns."""
from __future__ import annotations

from .lexicon import CITIES, DATES, DOCS, FILES, ITEMS, NAMES, TIMES, TOPICS

ROOMS = ["living room", "kitchen", "bedroom", "office", "hallway", "garage", "bathroom", "dining room", "basement", "front porch"]
TEMPS = ["18°C", "20°C", "21°C", "22°C", "23°C", "24°C"]
SONGS = ["the morning playlist", "the jazz playlist", "the focus mix", "the party mix", "the news podcast", "the workout mix", "the classical station", "the road trip mix"]
VOLUMES = ["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%"]
ACTIVITIES = ["a 5km run", "a 30-minute walk", "a strength session", "a yoga class", "a bike ride", "a swim", "a stretch session", "a hike"]
DURATIONS = ["10 minutes", "20 minutes", "30 minutes", "45 minutes", "1 hour", "90 minutes"]
MEALS = ["oatmeal and coffee", "a chicken salad", "pasta with vegetables", "rice and beans", "a turkey sandwich", "soup and bread", "eggs and toast", "a smoothie"]
TASKS = ["finish the report", "call the dentist", "send the invoice", "book the tickets", "review the deck", "water the plants", "renew the license", "clean the garage", "email the landlord", "update the budget"]
REMINDERS = ["take the medication", "call mom", "submit the timesheet", "pick up the dry cleaning", "renew the subscription", "check the oven", "send the follow-up", "pay the electricity bill"]
APPOINTMENTS = ["dentist", "doctor", "physio", "eye exam", "vaccination", "annual checkup", "therapy session", "blood test"]
PRODUCTS = ["a desk lamp", "a USB-C cable", "a phone case", "a coffee grinder", "a desk chair", "a water bottle", "a keyboard", "a monitor stand"]
CUSTOMERS = ["Maya Chen", "Jordan Lee", "Priya Shah", "Luis Ortiz", "Sam Patel", "Nina Rossi", "Omar Haddad", "Elena Petrova"]
RECORDS = ["customer 1042", "invoice 8821", "order 5520", "ticket 319", "account 7712", "case 9044"]
BACKUPS = ["the nightly backup", "the weekly archive", "the pre-migration snapshot", "the database dump"]
FOLDERS = ["the project folder", "the downloads folder", "the archive folder", "the shared drive", "the media folder"]
REPOS = ["the API repo", "the web app", "the data pipeline", "the mobile app"]
TABLES = ["orders", "customers", "invoices", "events", "users", "tickets"]
RESTAURANTS = ["Luigi's", "the Riverside Grill", "Casa Nova", "the Green Table", "Sakura", "the Corner Bistro"]
PLACE_TYPES = ["pharmacy", "coffee shop", "hardware store", "grocery store", "ATM", "charging station"]
AMOUNTS = ["$12", "$25", "$40", "$75", "$120", "$250"]
LANGS = ["Python", "JavaScript", "SQL", "Bash"]
FIELDS = ["email", "phone number", "address", "status", "owner"]
EVENTS = ["dentist appointment", "team sync", "product review", "lunch with Alex", "annual checkup", "project kickoff"]


def T(domain, desc, requests, slots):
    return {"domain": domain, "desc": desc, "requests": requests, "slots": slots}


TOOLS = {
    # calendar_email
    "create_event": T("calendar_email", "create a calendar event", [
        "Put {event} on my calendar {date} at {time}.", "Schedule a meeting with {name} {date} at {time}.", "Add {event} to my calendar {date}."],
        {"event": EVENTS, "name": NAMES, "date": DATES, "time": ["9am", "10:30am", "noon", "2pm", "3:30pm", "5pm"]}),
    "update_event": T("calendar_email", "change an existing event", [
        "Move my {event} {date} at {time}.", "Change the time of the meeting with {name} to {time}.", "Reschedule {event} {date}."],
        {"event": EVENTS, "name": NAMES, "date": DATES, "time": ["9am", "10:30am", "noon", "2pm", "3:30pm", "5pm"]}),
    "delete_event": T("calendar_email", "cancel a calendar event", [
        "Cancel the {event} {date}.", "Remove the meeting with {name} from my calendar.", "Delete {event} from my calendar."],
        {"event": EVENTS, "name": NAMES, "date": DATES}),
    "list_events": T("calendar_email", "list calendar events", [
        "What's on my calendar {date}?", "List my meetings {date}.", "Show my schedule {date}."],
        {"date": DATES}),
    "find_free_slots": T("calendar_email", "find common free time", [
        "Find a free hour with {name} {date}.", "When are {name} and I both free {date}?", "Find an open slot for a {duration} meeting {date}."],
        {"name": NAMES, "date": DATES, "duration": DURATIONS}),
    "send_email": T("calendar_email", "send an email", [
        "Email {name} about {topic}.", "Send {doc} to {name}.", "Reply to {name} with the updated {doc}.", "Forward {doc} to {name}."],
        {"name": NAMES, "topic": TOPICS, "doc": DOCS}),
    "draft_email": T("calendar_email", "draft an email without sending", [
        "Draft a reply to {name} about {topic}.", "Write an email to {name} about {doc}.", "Prepare an email to {name} about {topic}."],
        {"name": NAMES, "topic": TOPICS, "doc": DOCS}),
    "search_email": T("calendar_email", "search email", [
        "Find the email from {name} about {topic}.", "Search my inbox for {doc}.", "Look up the thread about {topic}."],
        {"name": NAMES, "topic": TOPICS, "doc": DOCS}),
    # search_web
    "web_search": T("search_web", "search the web", [
        "Search the web for {topic}.", "Look up {topic} online.", "Find information about {topic}."],
        {"topic": TOPICS}),
    "news_search": T("search_web", "search recent news", [
        "Find recent news about {topic}.", "What's the latest on {topic}?", "Search the news for {topic}."],
        {"topic": TOPICS}),
    "image_search": T("search_web", "search for images", [
        "Find images of {item}.", "Search for a photo of {item}.", "Show me pictures of {item}."],
        {"item": ITEMS}),
    "get_weather": T("search_web", "get current weather", [
        "What's the weather in {city} {date}?", "Will it rain in {city} {date}?", "Check the weather in {city}."],
        {"city": CITIES, "date": DATES}),
    "get_forecast": T("search_web", "get a weather forecast", [
        "Give me the forecast for {city} {date}.", "What's the forecast for {city} this week?", "Forecast the weather in {city} {date}."],
        {"city": CITIES, "date": DATES}),
    "maps_search": T("search_web", "search a map", [
        "Find the nearest {place_type} in {city}.", "Search the map for {place_type} locations in {city}.", "Where is the nearest {place_type} to {city}?"],
        {"place_type": PLACE_TYPES, "city": CITIES}),
    # files_code
    "read_file": T("files_code", "read a file", [
        "Read {file}.", "Show me the contents of {file}.", "Open {file} and summarize it."],
        {"file": FILES}),
    "write_file": T("files_code", "write or save a file", [
        "Write {file} with the {topic} notes.", "Save the {doc} to {file}.", "Create {file} with a short summary."],
        {"file": FILES, "topic": TOPICS, "doc": DOCS}),
    "delete_file": T("files_code", "delete a file", [
        "Delete {file}.", "Remove {file} from {folder}.", "Permanently delete {file}."],
        {"file": FILES, "folder": FOLDERS}),
    "list_files": T("files_code", "list files in a folder", [
        "List the files in {folder}.", "What's in {folder}?", "Show the contents of {folder}."],
        {"folder": FOLDERS}),
    "move_file": T("files_code", "move a file", [
        "Move {file} to {folder}.", "Put {file} in {folder}.", "Move {file} out of the downloads folder."],
        {"file": FILES, "folder": FOLDERS}),
    "run_code": T("files_code", "execute code", [
        "Run {file}.", "Execute the {lang} script.", "Run the {lang} file and show the output."],
        {"file": FILES, "lang": LANGS}),
    "run_tests": T("files_code", "run a test suite", [
        "Run the tests in {repo}.", "Check whether {repo} passes.", "Run the test suite for {repo}."],
        {"repo": REPOS}),
    # shopping_payments
    "search_products": T("shopping_payments", "search for products", [
        "Find {product} under {budget}.", "Search for {product} with good reviews.", "Compare prices for {product}."],
        {"product": PRODUCTS, "budget": AMOUNTS}),
    "add_to_cart": T("shopping_payments", "add an item to the cart", [
        "Add {product} to my cart.", "Put {product} in the basket.", "Add the item I just found to my cart."],
        {"product": PRODUCTS}),
    "checkout": T("shopping_payments", "complete a purchase", [
        "Check out my cart.", "Place the order for {product}.", "Buy the items in my cart."],
        {"product": PRODUCTS}),
    "track_order": T("shopping_payments", "track an order", [
        "Where is order {order}?", "Track the delivery for {product}.", "What's the status of order {order}?"],
        {"order": RECORDS, "product": PRODUCTS}),
    "return_item": T("shopping_payments", "start a return", [
        "Return {product}.", "Start a return for {product}.", "Send back {product} I bought."],
        {"product": PRODUCTS}),
    "send_payment": T("shopping_payments", "send a payment", [
        "Send {amount} to {name}.", "Pay {name} {amount}.", "Transfer {amount} to {name}."],
        {"amount": AMOUNTS, "name": NAMES}),
    "check_balance": T("shopping_payments", "check an account balance", [
        "What's my account balance?", "How much is left in {account}?", "Show the balance for {account}."],
        {"account": ["checking", "savings", "the joint account", "the business account"]}),
    # travel_maps
    "search_flights": T("travel_maps", "find flights", [
        "Find flights from {city1} to {city2} {date}.", "What flights go to {city2} {date}?", "Compare flights from {city1} to {city2}."],
        {"city1": CITIES, "city2": CITIES, "date": DATES}),
    "book_flight": T("travel_maps", "book a flight", [
        "Book the {time} flight to {city2} {date}.", "Reserve a seat on the flight to {city2}.", "Book a flight from {city1} to {city2} {date}."],
        {"city1": CITIES, "city2": CITIES, "date": DATES, "time": ["7am", "9am", "noon", "3pm", "6pm"]}),
    "search_hotels": T("travel_maps", "find hotels", [
        "Find hotels in {city2} {date}.", "What hotels are available near {place}?", "Compare hotels in {city2} {date}."],
        {"city2": CITIES, "date": DATES, "place": ["the station", "the airport", "the old town", "the convention center"]}),
    "book_hotel": T("travel_maps", "book a hotel", [
        "Book a hotel in {city2} {date}.", "Reserve a room near {place}.", "Book the hotel in {city2} for {n} nights."],
        {"city2": CITIES, "date": DATES, "place": ["the station", "the airport", "the old town", "the convention center"], "n": ["1", "2", "3", "4"]}),
    "search_trains": T("travel_maps", "find train routes", [
        "Find trains from {city1} to {city2} {date}.", "What rail options go to {city2}?", "Compare trains from {city1} to {city2}."],
        {"city1": CITIES, "city2": CITIES, "date": DATES}),
    "book_train": T("travel_maps", "book a train", [
        "Book the {time} train to {city2}.", "Reserve a seat on the train to {city2}.", "Book a train from {city1} to {city2} {date}."],
        {"city1": CITIES, "city2": CITIES, "date": DATES, "time": ["7am", "9am", "noon", "3pm", "6pm"]}),
    "get_directions": T("travel_maps", "get directions", [
        "Give me directions to {place}.", "How do I get to {place} from {city1}?", "Route me to {place}."],
        {"place": ["the airport", "the station", "the hotel", "the office", "the venue", "the clinic"], "city1": CITIES}),
    "find_nearby": T("travel_maps", "find nearby places", [
        "Find {place_type} locations near {place}.", "What's nearby in {city1}?", "Find {place_type} locations close to the hotel."],
        {"place_type": PLACE_TYPES, "place": ["the hotel", "the station", "the office", "the venue"], "city1": CITIES}),
    # messaging
    "send_message": T("messaging", "send a message", [
        "Text {name} that I'm running late.", "Send {name} a message about {topic}.", "Message {name} to confirm {time}."],
        {"name": NAMES, "topic": TOPICS, "time": ["9am", "noon", "3pm", "6pm"]}),
    "read_messages": T("messaging", "read messages", [
        "Show me the messages from {name}.", "What did {name} say?", "Open the chat with {name}."],
        {"name": NAMES}),
    "create_group": T("messaging", "create a group chat", [
        "Create a group chat with {name} and {name2}.", "Start a group for the {topic} project.", "Add {name} and {name2} to a new group."],
        {"name": NAMES, "name2": NAMES, "topic": TOPICS}),
    "search_messages": T("messaging", "search messages", [
        "Find the message about {topic}.", "Search my chats for {name}.", "Look up what {name} said about {topic}."],
        {"name": NAMES, "topic": TOPICS}),
    # data_crm
    "query_database": T("data_crm", "query a database", [
        "Query the {table} table for {topic}.", "How many rows in {table} match {topic}?", "Search {table} for {record}."],
        {"table": TABLES, "topic": TOPICS, "record": RECORDS}),
    "export_csv": T("data_crm", "export data to CSV", [
        "Export {table} to CSV.", "Download the {table} data as a CSV.", "Save the {table} query as CSV."],
        {"table": TABLES}),
    "update_record": T("data_crm", "update a record", [
        "Update {record} with the new {field}.", "Change the {field} on {record}.", "Set the {field} for {record}."],
        {"record": RECORDS, "field": FIELDS}),
    "delete_record": T("data_crm", "delete a record", [
        "Delete {record}.", "Remove {record} from the database.", "Permanently delete {record}."],
        {"record": RECORDS}),
    "lookup_customer": T("data_crm", "look up a customer", [
        "Look up {customer}.", "Find the account for {customer}.", "Show the profile for {customer}."],
        {"customer": CUSTOMERS}),
    "update_customer": T("data_crm", "update customer details", [
        "Update {customer}'s {field}.", "Change the {field} for {customer}.", "Set a new {field} for {customer}."],
        {"customer": CUSTOMERS, "field": FIELDS}),
    "create_ticket": T("data_crm", "create a support ticket", [
        "Create a ticket for {topic}.", "Open a support ticket about {topic}.", "Log a ticket for {record}."],
        {"topic": TOPICS, "record": RECORDS}),
    # smart_home
    "turn_on_light": T("smart_home", "turn on a light", [
        "Turn on the {room} light.", "Switch on the lights in the {room}.", "At {time}, turn on the {room} light."],
        {"room": ROOMS, "time": TIMES}),
    "turn_off_light": T("smart_home", "turn off a light", [
        "Turn off the {room} light.", "Switch off the lights in the {room}.", "At {time}, turn off the {room} light."],
        {"room": ROOMS, "time": TIMES}),
    "set_thermostat": T("smart_home", "set the thermostat", [
        "Set the {room} thermostat to {temp}.", "Make the {room} {temp}.", "At {time}, set the {room} to {temp}."],
        {"room": ROOMS, "temp": TEMPS, "time": TIMES}),
    "lock_door": T("smart_home", "lock a door", [
        "Lock the {room} door.", "Secure the front door.", "At {time}, lock the {room} door."],
        {"room": ROOMS, "time": TIMES}),
    "unlock_door": T("smart_home", "unlock a door", [
        "Unlock the {room} door.", "Open the front door.", "At {time}, unlock the {room} door."],
        {"room": ROOMS, "time": TIMES}),
    # health
    "log_workout": T("health", "log a workout", [
        "Log {activity}.", "Record that I did {activity}.", "Add {activity} to my workout log."],
        {"activity": ACTIVITIES}),
    "log_meal": T("health", "log a meal", [
        "Log {meal} for lunch.", "Add {meal} to my food diary.", "Record {meal} as dinner."],
        {"meal": MEALS}),
    "schedule_appointment": T("health", "schedule an appointment", [
        "Book a {appointment} {date}.", "Schedule a {appointment} for {time}.", "Find a {appointment} appointment {date}."],
        {"appointment": APPOINTMENTS, "date": DATES, "time": ["9am", "11am", "2pm", "4pm"]}),
    # productivity
    "create_task": T("productivity", "create a task", [
        "Add '{task}' to my tasks.", "Create a task to {task}.", "Put '{task}' on my to-do list."],
        {"task": TASKS}),
    "complete_task": T("productivity", "complete a task", [
        "Mark '{task}' as done.", "Complete the task to {task}.", "Check off '{task}'."],
        {"task": TASKS}),
    "set_reminder": T("productivity", "set a reminder", [
        "Remind me to {reminder} {date}.", "Set a reminder for {reminder} at {time}.", "Remind me at {time} to {reminder}."],
        {"reminder": REMINDERS, "date": DATES, "time": ["8am", "10am", "noon", "3pm", "6pm", "8pm"]}),
    # other
    "play_music": T("other", "play music", [
        "Play {song}.", "Put on {song}.", "Start {song} at {volume}."],
        {"song": SONGS, "volume": VOLUMES}),
    "set_volume": T("other", "set the volume", [
        "Set the volume to {volume}.", "Turn the volume up to {volume}.", "Lower the volume to {volume}."],
        {"volume": VOLUMES}),
    "book_restaurant": T("other", "book a restaurant", [
        "Book a table for {n} at {restaurant} {date}.", "Reserve dinner at {restaurant} {time}.", "Get a table for {n} at {restaurant}."],
        {"n": ["2", "3", "4", "5", "6"], "restaurant": RESTAURANTS, "date": DATES, "time": ["6pm", "7pm", "7:30pm", "8pm"]}),
    "cancel_reservation": T("other", "cancel a reservation", [
        "Cancel my reservation at {restaurant}.", "Cancel the table {date}.", "Cancel dinner at {restaurant} {time}."],
        {"restaurant": RESTAURANTS, "date": DATES, "time": ["6pm", "7pm", "7:30pm", "8pm"]}),
}

SPECIAL_TOOLS = {
    "ask_user": {"desc": "ask the user for missing details"},
    "confirm_action": {"desc": "ask for confirmation before a risky action"},
    "get_status": {"desc": "check the status of a running job"},
    "list_backups": {"desc": "list available backups"},
    "get_folder_size": {"desc": "calculate folder disk usage"},
}
