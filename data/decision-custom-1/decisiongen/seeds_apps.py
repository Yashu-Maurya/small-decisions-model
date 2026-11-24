"""Real-world application decisions.

Three families:
  * home_control - pick one of ten smart-home actions from a first-person intent.
  * animation   - pick one of eight avatar animations from first/second-person intent.
  * binary      - true/false spam, phishing and safety classification.

All templates are hand authored; slots are small local vocabularies plus the
shared time/name pools. Every placeholder used in a template must appear in
that pattern's ``slots`` dict or in ``APP_DEFAULT_SLOTS`` below.
"""
from __future__ import annotations

from .lexicon import NAMES, TIMES

HOME_ROOMS = [
    "living room", "kitchen", "bedroom", "hallway", "front porch", "home office",
    "garage", "basement", "dining room", "bathroom", "laundry room", "sunroom",
]
WHENS = [
    "right away", "when you can", "before I head out", "in a little while",
    "as soon as possible", "after dinner", "before bed", "in ten minutes",
]
TEMPS = ["19°C", "20°C", "21°C", "22°C", "23°C", "24°C", "25°C"]
MUSIC = ["the jazz playlist", "the focus mix", "the morning playlist", "the classical station",
         "the road trip mix", "the workout mix", "the news podcast", "the party mix"]
ANIM_PLACES = [
    "the door", "the hallway", "the kitchen", "the lobby", "the park", "the station",
    "the meeting room", "the front desk", "the sidewalk", "the waiting room",
    "the stage", "the living room", "the airport", "the classroom", "the cafe",
    "the parking lot",
]
SENDERS = [
    "a prize draw", "your bank", "the delivery service", "a colleague", "a newsletter",
    "an unknown sender", "the airline", "a store", "the IT desk", "a stranger",
    "the university", "a travel site", "your landlord", "a coupon site", "the clinic",
    "a crypto promoter", "the subscription service", "a job recruiter", "a friend",
    "the local council",
]
SUBJECTS = [
    "You have won a prize", "Your account will be closed", "Your package is on the way",
    "Meeting notes attached", "Limited offer just for you", "Please verify your password",
    "Your flight is delayed", "Invoice for last month", "Confirm your subscription",
    "A new device signed in", "Your order has shipped", "Weekly status update",
    "Claim your gift card", "Action needed on your account", "Lunch tomorrow?",
    "Your refund is ready", "Free ticket giveaway", "Security alert",
    "Payment receipt", "Important update",
]
DETAILS = [
    "click the link to claim it", "reply with your full password", "track it on the website",
    "see the attached file", "enter your card details", "call the number in the message",
    "ignore this note", "review it when you have time", "check the official app instead",
    "forward it to the whole team", "download the attachment", "delete this message",
]

APP_DEFAULT_SLOTS = {
    "room": HOME_ROOMS,
    "time": TIMES,
    "when": WHENS,
    "temp": TEMPS,
    "music": MUSIC,
    "place": ANIM_PLACES,
    "name": NAMES,
    "sender": SENDERS,
    "subject": SUBJECTS,
    "detail": DETAILS,
}

HOME_ACTIONS = {
    "turn_on_light": "switch a light on",
    "turn_off_light": "switch a light off",
    "set_thermostat": "change the target temperature",
    "lock_door": "lock a door",
    "unlock_door": "unlock a door",
    "close_blinds": "close the blinds",
    "open_blinds": "open the blinds",
    "start_vacuum": "start the robot vacuum",
    "arm_security": "arm the security system",
    "play_music": "play music",
}

ANIMATIONS = {
    "wave": "wave a greeting",
    "nod": "nod to agree",
    "shake_head": "shake the head to disagree",
    "clap": "clap for someone",
    "celebrate": "celebrate good news",
    "point": "point at something",
    "sit_down": "sit down",
    "stand_up": "stand up",
}

BINARY_TRUE = "true"
BINARY_FALSE = "false"


def A(domain: str, template: str, correct: str, slots: dict | None = None,
      question: str | None = None) -> dict:
    return {"domain": domain, "template": template, "correct": correct,
            "slots": slots or {}, "question": question}


# --- Home control: 30 intents, ten possible actions -------------------------
HOME_PATTERNS = [
    A("home_control", "I want the {room} light turned on. Can you do it {time}, {when}?", "turn_on_light"),
    A("home_control", "It's too dark in the {room} {time}, so switch the light on {when}.", "turn_on_light"),
    A("home_control", "I'm heading into the {room} {time} and need the light on. Please do it {when}.", "turn_on_light"),
    A("home_control", "Please switch off the {room} light {time}; I'll do it {when}.", "turn_off_light"),
    A("home_control", "I'm finished in the {room} {time}; turn the light off {when}.", "turn_off_light"),
    A("home_control", "The {room} light is still lit {time}; please turn it off {when}.", "turn_off_light"),
    A("home_control", "I'm cold in the {room} {time}; set the thermostat to {temp} {when}.", "set_thermostat"),
    A("home_control", "Please make the {room} warmer {time}, say {temp}, {when}.", "set_thermostat"),
    A("home_control", "It's too warm in the {room} {time}; set it to {temp} {when}.", "set_thermostat"),
    A("home_control", "I'm leaving the house {time}; lock the {room} door {when}.", "lock_door"),
    A("home_control", "Please lock the {room} door {time} before I go out {when}.", "lock_door"),
    A("home_control", "The {room} door is unlocked {time}; can you lock it {when}?", "lock_door"),
    A("home_control", "I'm outside the {room} door {time}; please unlock it {when}.", "unlock_door"),
    A("home_control", "I locked myself out of the {room} {time}; unlock the door {when}.", "unlock_door"),
    A("home_control", "Could you open the {room} door for me {time}, {when}?", "unlock_door"),
    A("home_control", "The sun is glaring into the {room} {time}; close the blinds {when}.", "close_blinds"),
    A("home_control", "It's bright in the {room} {time}; please close the blinds {when}.", "close_blinds"),
    A("home_control", "Close the {room} blinds {time} so I can nap {when}.", "close_blinds"),
    A("home_control", "It's gloomy in the {room} {time}; open the blinds {when}.", "open_blinds"),
    A("home_control", "Please let some light into the {room} {time}; open the blinds {when}.", "open_blinds"),
    A("home_control", "The {room} blinds are shut {time}; could you open them {when}?", "open_blinds"),
    A("home_control", "The {room} floor needs cleaning {time}; start the vacuum {when}.", "start_vacuum"),
    A("home_control", "Please run the robot vacuum in the {room} {time}, {when}.", "start_vacuum"),
    A("home_control", "I spilled crumbs in the {room} {time}; start the vacuum {when}.", "start_vacuum"),
    A("home_control", "I'm going to bed {time}; arm the security system {when}.", "arm_security"),
    A("home_control", "We're leaving the {room} {time}; please arm the security system {when}.", "arm_security"),
    A("home_control", "Nobody is home {time}; arm the alarm system {when}, please.", "arm_security"),
    A("home_control", "I'd like {music} in the {room} {time}; play it {when}.", "play_music"),
    A("home_control", "Please play some music in the {room} {time}, {when}.", "play_music"),
    A("home_control", "Put on {music} for the {room} {time}; start it {when}.", "play_music"),
]

# --- Animations: 20 intents, eight possible animations ----------------------
ANIMATION_PATTERNS = [
    A("animation", "I'm greeting {name} at {place} {time}; wave at them.", "wave"),
    A("animation", "You see a friend at {place} {time}. Say hello with a gesture.", "wave"),
    A("animation", "I want to agree with {name} at {place} {time} without speaking.", "nod"),
    A("animation", "You want to say yes at {place} {time} but stay quiet.", "nod"),
    A("animation", "I need to disagree with {name} at {place} {time} without words.", "shake_head"),
    A("animation", "You heard a bad suggestion at {place} {time}. Respond without talking.", "shake_head"),
    A("animation", "I enjoyed the performance at {place} {time} and want to show it.", "clap"),
    A("animation", "You watched {name} finish a talk at {place} {time}. Show approval.", "clap"),
    A("animation", "I just got good news at {place} {time}; celebrate with me.", "celebrate"),
    A("animation", "You passed the exam {time} and feel like celebrating at {place}.", "celebrate"),
    A("animation", "I need to show {name} the exit at {place} {time}.", "point"),
    A("animation", "You should indicate the way to {place} {time} without speaking.", "point"),
    A("animation", "I've been on my feet at {place} {time}; I want to sit down.", "sit_down"),
    A("animation", "You are tired at {place} {time} and need to rest.", "sit_down"),
    A("animation", "I've been sitting in {place} {time} too long; help me get up.", "stand_up"),
    A("animation", "You should get up at {place} {time} and stretch.", "stand_up"),
    A("animation", "I want to welcome {name} at {place} {time} with a friendly gesture.", "wave"),
    A("animation", "You agreed with the plan at {place} {time}; show it silently.", "nod"),
    A("animation", "I saw something amazing at {place} {time} and want to react.", "celebrate"),
    A("animation", "You need to rest for a moment at {place} {time}.", "sit_down"),
]

# --- Binary classification: spam, phishing and safety flags ----------------
BINARY_PATTERNS = [
    A("binary", 'Is this message spam? Message from {sender} {time}: "{subject} - {detail}".', "true",
      question="Answer true if it is spam, false otherwise."),
    A("binary", 'Is this message spam? From {sender} {time}: "{subject} - {detail}".', "false",
      question="Answer true if it is spam, false otherwise."),
    A("binary", 'Is this a phishing attempt? From {sender} {time}: "{subject} - {detail}".', "true",
      question="Answer true if it tries to steal credentials or money, false otherwise."),
    A("binary", 'Is this a phishing attempt? From {sender} {time}: "{subject} - {detail}".', "false",
      question="Answer true if it tries to steal credentials or money, false otherwise."),
    A("binary", 'Is this comment abusive? Posted by {name} {time}: "{subject} - {detail}".', "true",
      question="Answer true if it is abusive, false otherwise."),
    A("binary", 'Is this comment abusive? Posted by {name} {time}: "{subject} - {detail}".', "false",
      question="Answer true if it is abusive, false otherwise."),
    A("binary", 'Is this review fake? Written by {name} {time}: "{subject} - {detail}".', "true",
      question="Answer true if the review looks fake, false otherwise."),
    A("binary", 'Is this review fake? Written by {name} {time}: "{subject} - {detail}".', "false",
      question="Answer true if the review looks fake, false otherwise."),
    A("binary", 'Should this request be flagged as unsafe? From {sender} {time}: "{subject} - {detail}".', "true",
      question="Answer true if the request is unsafe, false otherwise."),
    A("binary", 'Should this request be flagged as unsafe? From {sender} {time}: "{subject} - {detail}".', "false",
      question="Answer true if the request is unsafe, false otherwise."),
    A("binary", 'Is this email unsolicited bulk mail? From {sender} {time}: "{subject} - {detail}".', "true",
      question="Answer true if it is unsolicited bulk mail, false otherwise."),
    A("binary", 'Is this email unsolicited bulk mail? From {sender} {time}: "{subject} - {detail}".', "false",
      question="Answer true if it is unsolicited bulk mail, false otherwise."),
    A("binary", 'Does this message contain a scam link? From {sender} {time}: "{subject} - {detail}".', "true",
      question="Answer true if it contains a scam link, false otherwise."),
    A("binary", 'Does this message contain a scam link? From {sender} {time}: "{subject} - {detail}".', "false",
      question="Answer true if it contains a scam link, false otherwise."),
    A("binary", 'Is this support ticket a duplicate? Filed by {name} {time}: "{subject} - {detail}".', "true",
      question="Answer true if it is a duplicate, false otherwise."),
    A("binary", 'Is this support ticket a duplicate? Filed by {name} {time}: "{subject} - {detail}".', "false",
      question="Answer true if it is a duplicate, false otherwise."),
    A("binary", 'Is this an automated notification? From {sender} {time}: "{subject} - {detail}".', "true",
      question="Answer true if it is automated, false otherwise."),
    A("binary", 'Is this an automated notification? From {sender} {time}: "{subject} - {detail}".', "false",
      question="Answer true if it is automated, false otherwise."),
    A("binary", 'Does this message expose private data? From {sender} {time}: "{subject} - {detail}".', "true",
      question="Answer true if it exposes private data, false otherwise."),
    A("binary", 'Does this message expose private data? From {sender} {time}: "{subject} - {detail}".', "false",
      question="Answer true if it exposes private data, false otherwise."),
    A("binary", 'Is this a legitimate service notice? From {sender} {time}: "{subject} - {detail}".', "true",
      question="Answer true if it is legitimate, false otherwise."),
    A("binary", 'Is this a legitimate service notice? From {sender} {time}: "{subject} - {detail}".', "false",
      question="Answer true if it is legitimate, false otherwise."),
    A("binary", 'Should this message go to the spam folder? From {sender} {time}: "{subject} - {detail}".', "true",
      question="Answer true if it should be filtered, false otherwise."),
    A("binary", 'Should this message go to the spam folder? From {sender} {time}: "{subject} - {detail}".', "false",
      question="Answer true if it should be filtered, false otherwise."),
]

# Distinct message pools for the two labels: a message is never generated with
# contradictory true/false labels just because it landed in a different pattern.
BAD_SUBJECTS = [
    "You have won a prize", "Your account will be closed", "Verify your password now",
    "Claim your gift card", "Action needed on your account", "Free ticket giveaway",
    "Security alert: sign in", "Your refund is ready to collect", "Limited offer just for you",
    "Important: confirm your card", "You have been selected", "Urgent payment request",
    "Unusual activity detected", "Congratulations, claim now", "Final notice",
    "Click to avoid suspension", "Exclusive deal for you", "Wire transfer needed",
]
BAD_DETAILS = [
    "click the link to claim it", "reply with your full password", "enter your card details",
    "call the number in the message", "download the attachment", "forward it to the whole team",
    "send money to the listed account", "sign in on the linked page", "confirm your security code",
    "open the file to continue", "provide your bank details", "act within 24 hours",
]
GOOD_SUBJECTS = [
    "Meeting notes attached", "Your package is on the way", "Your flight is delayed",
    "Invoice for last month", "Weekly status update", "Your order has shipped",
    "Lunch tomorrow?", "Payment receipt", "Important update", "Appointment confirmed",
    "Team dinner on Friday", "Library book due", "Password changed successfully",
    "Delivery scheduled", "Timesheet reminder", "Project kickoff notes",
    "Reply to your request", "Photos from the trip", "Meeting rescheduled", "Welcome aboard",
]
GOOD_DETAILS = [
    "see the attached file", "review it when you have time", "check the official app instead",
    "ignore this note", "look at the schedule", "reply if you have questions",
    "open the document for details", "the change is already applied", "no action is needed",
    "we will be in touch", "thank you for your patience", "let me know your availability",
]
for _p in BINARY_PATTERNS:
    _bad = _p["correct"] == BINARY_TRUE
    _p["slots"] = {
        "subject": BAD_SUBJECTS if _bad else GOOD_SUBJECTS,
        "detail": BAD_DETAILS if _bad else GOOD_DETAILS,
    }

APP_PATTERNS = HOME_PATTERNS + ANIMATION_PATTERNS + BINARY_PATTERNS
