"""Special tool-router and tool-decline patterns."""
from __future__ import annotations

from .lexicon import CITIES, DATES, DOCS, FILES, NAMES, TIMES
from .seeds_tools import (ACTIVITIES, AMOUNTS, APPOINTMENTS, CUSTOMERS, FOLDERS, MEALS,
                          RECORDS, REPOS, ROOMS, TABLES, TASKS, TEMPS)

POLICIES = [
    "Use the most specific tool available.",
    "Choose the tool that directly matches the request.",
    "Prefer one clear action over several unrelated ones.",
    "Do not use a tool that changes data unless the request asks for it.",
    "Use the tool that needs the fewest assumptions.",
    "Keep the action limited to what the user asked.",
]


def S(behavior, request, tools, correct, slots, policy=None):
    return {"behavior": behavior, "request": request, "tools": tools,
            "correct": correct, "slots": slots, "policy": policy}


SPECIAL_PATTERNS = [
    S("clarify_confirm", "Book a flight for {name} to {city2}.", ["search_flights", "book_flight", "get_weather", "ask_user", "search_hotels", "check_balance"], "ask_user",
      {"name": NAMES, "city2": CITIES}, "Ask for missing travel details before booking."),
    S("clarify_confirm", "Delete the old {field} records for {customer} {date}.", ["delete_record", "query_database", "export_csv", "confirm_action", "update_customer", "create_ticket"], "confirm_action",
      {"field": ["email", "phone", "address", "status"], "customer": CUSTOMERS, "date": DATES}, "Confirm destructive actions before deleting data."),
    S("clarify_confirm", "Send {doc} to {name} at an external company.", ["send_email", "draft_email", "search_email", "confirm_action", "create_ticket", "update_record"], "confirm_action",
      {"doc": DOCS, "name": NAMES}, "External emails require confirmation."),
    S("clarify_confirm", "Charge {amount} to the card on file for {customer} {date}.", ["send_payment", "check_balance", "confirm_action", "create_ticket", "lookup_customer", "export_csv"], "confirm_action",
      {"amount": AMOUNTS, "customer": CUSTOMERS, "date": DATES}, "Confirm payments above the usual limit."),
    S("clarify_confirm", "Permanently delete {file} from {folder} {time}.", ["delete_file", "list_files", "move_file", "confirm_action", "read_file", "write_file"], "confirm_action",
      {"file": FILES, "folder": FOLDERS, "time": TIMES}, "Confirm permanent deletion before removing files."),
    S("clarify_confirm", "Unlock the {room} door for {name} {time}.", ["unlock_door", "lock_door", "turn_on_light", "confirm_action", "set_thermostat", "play_music"], "confirm_action",
      {"room": ROOMS, "name": NAMES, "time": TIMES}, "Confirm remote door unlocks."),
    S("clarify_confirm", "Book a table at {restaurant} {date}.", ["book_restaurant", "cancel_reservation", "get_directions", "ask_user", "search_flights", "create_task"], "ask_user",
      {"restaurant": ["Luigi's", "Casa Nova", "Sakura", "the Green Table", "the Corner Bistro", "the Riverside Grill"], "date": DATES}, "Ask for the party size and time before booking."),

    S("read_only", "Check whether {backup} for {name} finished {date}.", ["get_status", "list_backups", "delete_record", "run_tests", "export_csv", "send_email"], "get_status",
      {"backup": ["the nightly backup", "the weekly archive", "the database dump", "the pre-migration snapshot"], "name": NAMES, "date": DATES}, None),
    S("read_only", "See how much space {folder} uses on {name}'s account {time}.", ["get_folder_size", "delete_file", "move_file", "list_files", "write_file", "send_email"], "get_folder_size",
      {"folder": FOLDERS, "name": NAMES, "time": TIMES}, None),
    S("read_only", "Check the status of {repo} tests for {name} {time}.", ["get_status", "run_tests", "write_file", "delete_file", "move_file", "send_email"], "get_status",
      {"repo": REPOS, "name": NAMES, "time": TIMES}, None),
    S("read_only", "Check whether {backup} is safe to delete {date}.", ["list_backups", "delete_record", "export_csv", "check_balance", "send_email", "update_record"], "list_backups",
      {"backup": ["the nightly backup", "the weekly archive", "the database dump", "the pre-migration snapshot"], "date": DATES}, None),
    S("read_only", "Look up the last invoice for {customer} without changing it {date}.", ["query_database", "update_record", "delete_record", "export_csv", "send_email", "create_ticket"], "query_database",
      {"customer": CUSTOMERS, "date": DATES}, None),

    S("multi_step", "Book the cheapest flight to {city2} {date}.", ["search_flights", "book_flight", "get_weather", "search_hotels", "check_balance", "send_email"], "search_flights",
      {"city2": CITIES, "date": DATES}, "Search for options before booking."),
    S("multi_step", "Plan a trip to {city2} and book a hotel near the station {date}.", ["search_hotels", "book_hotel", "get_directions", "search_flights", "check_balance", "send_email"], "search_hotels",
      {"city2": CITIES, "date": DATES}, "Search for options before booking."),
    S("multi_step", "Book a train and then a hotel for {city2} {date}.", ["search_trains", "book_train", "book_hotel", "search_hotels", "check_balance", "send_email"], "search_trains",
      {"city2": CITIES, "date": DATES}, "Search for the first leg before booking."),
    S("multi_step", "Update {customer}'s {field} and notify them {date}.", ["lookup_customer", "update_customer", "send_email", "create_ticket", "export_csv", "delete_record"], "lookup_customer",
      {"customer": CUSTOMERS, "field": ["email", "phone number", "address", "status"], "date": DATES}, "Verify the customer before changing the record."),
    S("multi_step", "Email {name} the {table} export {date}.", ["export_csv", "send_email", "query_database", "delete_record", "update_record", "create_ticket"], "export_csv",
      {"name": NAMES, "table": TABLES, "date": DATES}, "Prepare the export before sending the file."),
]


def X(reason, request, tools, slots, policy=None):
    return {"reason": reason, "request": request, "tools": tools, "slots": slots, "policy": policy}


TOOL_DECLINE_PATTERNS = [
    X("unsafe_destructive", "Delete every record in {table} for {customer}.", ["delete_record", "query_database", "export_csv", "update_customer", "create_ticket", "lookup_customer"],
      {"table": TABLES, "customer": CUSTOMERS}, "Do not perform destructive actions without explicit authorization."),
    X("unsafe_destructive", "Email me the passwords for {account}.", ["send_email", "search_email", "draft_email", "create_ticket", "update_record", "check_balance"],
      {"account": ["the admin account", "the shared mailbox", "the customer portal", "the payroll system"]}, "Never send credentials by email."),
    X("unsafe_destructive", "Unlock the {room} door for a stranger while I'm away {time}.", ["unlock_door", "lock_door", "turn_on_light", "set_thermostat", "play_music", "set_volume"],
      {"room": ROOMS, "time": TIMES}, "Do not unlock doors for unverified people."),
    X("unsafe_destructive", "Disable the smoke alarm in the {room} before cooking {meal}.", ["set_thermostat", "turn_off_light", "lock_door", "unlock_door", "play_music", "set_volume"],
      {"room": ROOMS, "meal": MEALS}, "Never disable a safety device."),

    X("missing_args", "Transfer {amount}.", ["send_payment", "check_balance", "search_email", "create_ticket", "update_record", "export_csv"],
      {"amount": AMOUNTS}, "Ask for the recipient before sending money."),
    X("missing_args", "Charge the customer.", ["send_payment", "check_balance", "lookup_customer", "update_customer", "create_ticket", "export_csv"],
      {"customer": CUSTOMERS}, "Ask for the amount and invoice before charging."),
    X("missing_args", "Send the file.", ["send_email", "draft_email", "delete_file", "move_file", "create_ticket", "update_record"],
      {"file": FILES}, "Ask which file and recipient before sending."),
    X("missing_args", "Book a table {date}.", ["book_restaurant", "cancel_reservation", "get_directions", "send_message", "create_task", "set_reminder"],
      {"date": DATES}, "Ask for the restaurant, time, and party size."),

    X("no_suitable_tool", "Translate this sentence to {lang}.", ["send_email", "create_event", "get_weather", "search_flights", "play_music", "check_balance"],
      {"lang": ["French", "Spanish", "German", "Italian", "Portuguese", "Japanese"]}, None),
    X("no_suitable_tool", "Order a pizza for {n} people.", ["search_flights", "book_hotel", "create_ticket", "send_email", "set_thermostat", "play_music"],
      {"n": ["2", "3", "4", "5", "6", "8"]}, None),
    X("no_suitable_tool", "Fix the leak under the sink {time}.", ["send_email", "create_event", "get_weather", "search_flights", "play_music", "check_balance"],
      {"time": TIMES}, None),

    X("policy_privacy", "Send the customer's medical record to {name}.", ["send_email", "search_email", "export_csv", "query_database", "create_ticket", "update_record"],
      {"name": NAMES}, "Never share sensitive records without authorization."),
    X("policy_privacy", "Record the meeting without telling anyone {date}.", ["create_event", "send_email", "create_task", "set_reminder", "search_email", "update_record"],
      {"date": DATES}, "Do not record people without consent."),
    X("policy_privacy", "Share the confidential {doc} with {name} outside the company.", ["send_email", "export_csv", "update_record", "create_ticket", "search_email", "query_database"],
      {"doc": ["slides", "report", "contract", "budget", "invoice", "notes", "proposal", "schedule", "receipt", "draft"], "name": NAMES}, "Confidential files require authorization."),

    X("ambiguous", "Handle it for {name} {time}.", ["send_email", "create_event", "delete_file", "book_flight", "send_payment", "update_record"],
      {"name": NAMES, "time": TIMES}, None),
    X("ambiguous", "Send it to her {time}.", ["send_email", "send_message", "create_task", "set_reminder", "update_record", "create_ticket"],
      {"time": TIMES}, None),

    X("already_done", "I already booked the flight to {city2} {date}.", ["book_flight", "search_flights", "get_weather", "search_hotels", "send_email", "check_balance"],
      {"city2": CITIES, "date": DATES}, None),
    X("already_done", "I already sent the report to {name} {date}.", ["send_email", "draft_email", "search_email", "create_task", "set_reminder", "update_record"],
      {"name": NAMES, "date": DATES}, None),
]
