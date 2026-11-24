"""Shared slot values and distractor pools. Hand-authored, no external data."""
from __future__ import annotations

NAMES = [
    "Maya", "Jordan", "Priya", "Luis", "Sam", "Nina", "Omar", "Elena", "Theo", "Grace",
    "Ravi", "Mia", "Noah", "Ava", "Kai", "Zoe", "Leo", "Amara", "Ben", "Sofia",
    "Ibrahim", "Hana", "Mateo", "Iris", "Dev", "Chloe", "Jonas", "Layla", "Marcus", "Yuki",
    "Ana", "Ethan", "Nora", "Felix", "Aisha", "Diego", "Ruth", "Caleb", "Sana", "Owen",
    "Lena", "Tariq", "Maeve", "Hugo", "Priyanka", "Eli", "June", "Rosa",
]
TIMES = [
    "this morning", "yesterday afternoon", "last night", "earlier today", "on Monday",
    "on Tuesday evening", "on Wednesday", "last Friday", "over the weekend", "around noon",
    "just after lunch", "before work", "after work", "at 7:15am", "at 9:40am",
    "at 12:10pm", "at 3:30pm", "at 6:45pm", "at 8:20pm", "late last week",
    "a few minutes ago", "on Saturday morning", "on Sunday afternoon", "the day before yesterday",
    "this afternoon", "tonight", "at rush hour", "during the lunch break",
    "at the end of the day", "first thing in the morning",
]

# A larger, still hand-authored time pool. The combinatorial suffixes are
# built locally from a small vocab so the generator can create enough unique
# inputs at the 1M-record scale without any external data.
_TIMES_MORE = []
for _pre in ("early", "late"):
    for _base in ("morning", "afternoon", "evening"):
        _TIMES_MORE.append(f"{_pre} {_base}")
for _pre in ("just after", "around", "before", "after"):
    for _base in ("morning", "afternoon", "evening", "lunch", "dinner",
                  "the school run", "the commute"):
        _TIMES_MORE.append(f"{_pre} {_base}")
for _day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
             "Saturday", "Sunday"):
    for _part in ("morning", "afternoon", "evening"):
        _TIMES_MORE.append(f"on {_day} {_part}")
for _hour in (6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22):
    for _minute in ("05", "20", "35", "50"):
        _h = _hour if _hour <= 12 else _hour - 12
        _ap = "am" if _hour < 12 else "pm"
        _TIMES_MORE.append(f"at {_h}:{_minute}{_ap}")
TIMES.extend(x for x in _TIMES_MORE if x not in TIMES)

PLACES = [
    "the office", "the break room", "the lobby", "the parking lot", "home", "the kitchen",
    "the living room", "the grocery store", "the pharmacy", "the gym", "a cafe", "the library",
    "the bus stop", "the train station", "the sidewalk", "the waiting room", "the hotel lobby", "the airport",
    "the restaurant", "the park", "the school", "the clinic", "the bank",
    "the hardware store", "the post office", "the copy room", "the conference room", "the elevator",
    "the front desk",
]
RELATIONS = ["friend", "coworker", "neighbor", "teammate", "manager", "sibling", "client"]
CITIES = [
    "Berlin", "Paris", "London", "Madrid", "Rome", "Amsterdam", "Vienna", "Prague", "Lisbon",
    "Dublin", "Copenhagen", "Stockholm", "Warsaw", "Budapest", "Zurich", "Brussels", "Oslo",
    "Helsinki", "Munich", "Barcelona", "Milan", "Athens", "Porto", "Seville", "Lyon",
]
DATES = [
    "today", "tomorrow", "on Monday", "on Tuesday", "on Wednesday", "on Thursday", "on Friday",
    "next Monday", "next Friday", "this weekend", "next weekend", "on the 3rd", "on the 12th",
    "on the 21st", "at the end of the month", "next month", "in two weeks", "on June 4",
    "on July 18", "on August 2", "on September 15", "on October 6", "on November 11",
    "on December 20",
]
DOCS = ["the invoice", "the report", "the contract", "the budget", "the agenda", "the slides",
        "the summary", "the receipt", "the proposal", "the schedule", "the notes", "the draft"]
TOPICS = ["the launch", "the budget", "the schedule", "the client feedback", "the hiring plan",
          "the quarterly numbers", "the travel policy", "the project update", "the contract",
          "the inventory", "the new design", "the support issue"]
ITEMS = ["the package", "the laptop", "the monitor", "the printer", "the router", "the phone",
         "the invoice", "the receipt", "the keys", "the charger", "the hard drive", "the camera"]
FILES = ["report.docx", "budget.xlsx", "notes.md", "main.py", "data.csv", "photo.jpg",
         "invoice.pdf", "slides.pptx", "config.yaml", "README.md", "backup.zip", "draft.txt"]

QUESTIONS = {
    "social": ["What do you say?", "What's the best response?", "How do you respond?", "What would you do?"],
    "everyday": ["What's the best move?", "What should you do?", "What's the next step?", "How do you handle it?"],
    "work": ["What's the best next step?", "What should you do first?", "How should you handle this?", "What do you do?"],
    "health": ["What should you do?", "What's the safest next step?", "How do you handle this?", "What's the best action?"],
    "money": ["What should you do?", "What's the best first step?", "How do you handle it?", "What's the right move?"],
    "travel": ["What should you do?", "What's the best next step?", "How do you handle this?", "What's the right move?"],
    "learning": ["What's the best next step?", "What should you do?", "How do you proceed?", "What's the right move?"],
    "communication": ["What do you say?", "What's the best response?", "How should you reply?", "What do you do?"],
    "ethics": ["What should you do?", "What's the right action?", "How do you handle this?", "What's the best choice?"],
    "tool": ["Which tool should you call?", "What's the right tool?", "Which action fits?", "What should you call?"],
}

WRONG = {
    "social_positive": [
        "Change the subject to yourself", "Downplay their news", "Ask how much it pays",
        "Make a joke at their expense", "Compare it to your own success", "Check your phone mid-story",
        "Give unsolicited advice", "Say they got lucky", "Ask intrusive questions",
        "Promise to celebrate later and forget", "Criticize the choice", "Talk about your own plans",
        "Congratulate them sarcastically", "Walk away without responding", "Tell them it's not a big deal",
    ],
    "social_negative": [
        "Tell them to cheer up", "Offer a quick fix", "One-up their problem", "Make a joke",
        "Change the subject", "Blame them for the situation", "Minimize what happened", "Avoid them",
        "Promise to fix everything", "Share their news with others", "Give a lecture",
        "Compare it to your own problems", "Say it could be worse", "Check your phone", "Rush them to move on",
    ],
    "social_conflict": [
        "Send an angry message", "Avoid them indefinitely", "Complain to everyone else",
        "Escalate publicly", "Pretend nothing happened", "Demand an apology immediately",
        "Bring up old mistakes", "Give them the silent treatment", "Post about it online",
        "Threaten to report them", "Blame yourself for everything", "Ignore the issue and hope it fades",
        "Talk over them", "Make a sarcastic comment", "Leave without explanation",
    ],
    "social_boundary": [
        "Agree to everything", "Cancel at the last minute", "Make an excuse", "Ignore the message",
        "Say yes then avoid them", "Give a vague maybe", "Argue about the request",
        "Share their message with others", "Offer an unrelated favor", "Change the topic",
        "Promise more than you can do", "Respond passive-aggressively", "Block them without explanation",
        "Agree and complain later", "Ask why they even need it",
    ],
    "work_priority": [
        "Do the easiest task first", "Ignore the deadline", "Wait for someone to remind you",
        "Start everything at once", "Work through the night", "Skip the meeting",
        "Delegate the urgent task", "Reply to email all day", "Focus on low-impact busywork",
        "Cancel the deadline", "Ask for an extension at the last minute", "Do the fun task first",
        "Multitask everything", "Leave early", "Blame the tools",
    ],
    "work_communication": [
        "Reply angrily", "Ignore the message", "Copy the whole company", "Send a vague update",
        "Wait until the deadline", "Blame a teammate", "Overpromise", "Use sarcasm",
        "Schedule a meeting with no agenda", "Write a long rant", "Avoid the person",
        "Escalate without context", "Share confidential details", "Assume they understood",
        "Send it late at night",
    ],
    "work_conflict": [
        "Take sides publicly", "Ignore the argument", "Let it escalate", "Complain to HR immediately",
        "Confront them in front of everyone", "Send a passive-aggressive message", "Assign blame",
        "Cancel the project", "Threaten to quit", "Gossip about it", "Refuse to listen",
        "Make a joke at their expense", "Escalate to the CEO", "Shut down all discussion", "Leave the meeting",
    ],
    "work_quality": [
        "Ship it without checking", "Hide the mistake", "Blame the reviewer", "Skip the tests",
        "Rewrite everything", "Ignore the feedback", "Delete the failing test", "Merge without review",
        "Work around the bug", "Ask someone else to sign off", "Copy code from an unknown source",
        "Delay indefinitely", "Add more features instead", "Assume it works", "Document nothing",
    ],
    "everyday_fix": [
        "Ignore the problem", "Use the unsafe option", "Wait until it gets worse",
        "Buy an expensive replacement", "Try a random repair", "Ask a stranger to fix it", "Force it",
        "Use the wrong tool", "Skip the instructions", "Leave it for someone else",
        "Throw it away immediately", "Cover it with tape", "Turn it off and on repeatedly",
        "Guess the cause", "Post about it instead",
    ],
    "everyday_safety": [
        "Ignore the warning", "Keep using it", "Smell the gas and light a match",
        "Mix cleaning chemicals", "Block the exit", "Skip the safety gear", "Touch the exposed wire",
        "Leave the stove on", "Store fuel indoors", "Override the lock", "Run the generator inside",
        "Use water on an electrical fire", "Climb without support", "Remove the smoke alarm",
        "Continue driving on a flat tire",
    ],
    "everyday_time": [
        "Start the longest task last", "Wait until the last minute", "Cancel the important thing",
        "Do nothing", "Overbook yourself", "Forget the deadline", "Take the slowest route",
        "Ignore the clock", "Promise to be there early and leave late", "Skip the preparation",
        "Multitask while driving", "Start a new project", "Answer every notification",
        "Let someone else handle it", "Assume it will work out",
    ],
    "health_safety": [
        "Ignore the symptoms", "Double the dose", "Take someone else's medication",
        "Drive yourself while dizzy", "Wait until morning", "Search online and self-treat",
        "Mix medications", "Skip the follow-up", "Continue exercising through pain",
        "Drink alcohol with the medication", "Use an expired product", "Delay calling for help",
        "Hide the symptoms", "Guess the dosage", "Stop treatment suddenly",
    ],
    "health_habit": [
        "Skip sleep", "Crash diet", "Exercise through injury", "Drink more caffeine",
        "Start with an extreme routine", "Copy a stranger's plan", "Ignore the pain",
        "Train without warming up", "Take supplements without checking", "Replace meals with snacks",
        "Stay up all night", "Avoid the doctor", "Compare yourself to others",
        "Quit after one setback", "Do the hardest workout first",
    ],
    "money_consumer": [
        "Ignore the charge", "Pay cash without a receipt", "Share your card details",
        "Take a payday loan", "Buy the extended warranty without checking", "Cancel the card immediately",
        "Argue with the cashier", "Post the receipt online", "Send money to a stranger",
        "Click the urgent link", "Use the same password", "Skip the terms",
        "Pay the full price without comparing", "Borrow from a friend", "Assume it's a mistake",
    ],
    "money_budget": [
        "Spend the emergency fund", "Ignore the bill", "Pay only the minimum forever",
        "Borrow to invest", "Cut all food spending", "Cancel insurance", "Lend money you need",
        "Hide the bill", "Buy it on credit", "Skip the budget review", "Use a high-interest loan",
        "Delay the payment", "Assume you'll earn more", "Spend on wants first", "Share your bank login",
    ],
    "travel_disruption": [
        "Miss the flight", "Argue with the gate agent", "Leave your luggage unattended",
        "Sleep in the airport", "Book the first option without checking", "Ignore the delay notice",
        "Cancel the whole trip", "Drive without rest", "Share your passport photo",
        "Leave the terminal without your bags", "Demand a refund at the gate",
        "Wait until the last minute", "Follow a stranger's offer", "Overstay the connection",
        "Ignore the visa rules",
    ],
    "travel_planning": [
        "Book without checking the dates", "Skip travel insurance", "Carry all cash",
        "Share your itinerary publicly", "Pack prohibited items", "Ignore the weather",
        "Arrive at the last minute", "Use an unlicensed taxi", "Leave valuables in the car",
        "Book a hotel outside your budget", "Ignore local laws", "Copy a stranger's plans",
        "Skip the passport check", "Overpack and pay fees", "Assume the price includes everything",
    ],
    "learning_debug": [
        "Copy code blindly", "Restart from scratch", "Ignore the error message",
        "Change random lines", "Delete the failing test", "Blame the language",
        "Work through the night", "Skip the documentation", "Ask someone to do it for you",
        "Add more dependencies", "Disable the checks", "Assume it's a hardware problem",
        "Rewrite everything", "Ignore the stack trace", "Ship it anyway",
    ],
    "learning_study": [
        "Cram all night", "Skip the practice problems", "Read without taking notes",
        "Study only the easiest topic", "Copy a friend's work", "Ignore the syllabus",
        "Multitask while studying", "Memorize without understanding", "Start the day before",
        "Avoid asking questions", "Study in a noisy place", "Skip sleep",
        "Compare yourself to others", "Quit after one mistake", "Use only one source",
    ],
    "learning_security": [
        "Share your password", "Click the link", "Disable two-factor authentication",
        "Use the same password everywhere", "Email the code to yourself", "Ignore the update",
        "Install from an unknown site", "Plug in the found USB", "Approve every permission",
        "Post your API key", "Use public Wi-Fi without care", "Bypass the login",
        "Share the admin account", "Turn off the firewall", "Trust the caller",
    ],
    "communication_tone": [
        "Send an angry reply", "Use sarcasm", "Ignore the message", "Copy everyone",
        "Write a vague response", "Delay indefinitely", "Blame the other person",
        "Make it personal", "Use all caps", "Threaten to escalate", "Share the message publicly",
        "Assume the worst", "Talk over them", "Give the silent treatment", "Respond with a meme",
    ],
    "communication_conflict": [
        "Escalate publicly", "Avoid the person", "Gossip", "Send a passive-aggressive note",
        "Demand an apology", "Bring up old issues", "Refuse to listen", "Take sides",
        "Threaten to report them", "Complain to everyone", "Shut down the conversation",
        "Blame yourself", "Ignore the problem", "Make a joke", "Leave without a word",
    ],
    "ethics_integrity": [
        "Hide the mistake", "Lie about it", "Blame someone else", "Take credit", "Keep the money",
        "Fake the record", "Delete the evidence", "Break the rule quietly", "Ask for a cover-up",
        "Copy the work", "Misrepresent the results", "Ignore the conflict of interest",
        "Use insider information", "Break confidentiality", "Cut corners",
    ],
    "ethics_civic": [
        "Ignore the hazard", "Dump the waste", "Skip the permit", "Bypass the safety check",
        "Lie on the form", "Take the public funds", "Vote twice", "Harass the neighbor",
        "Ignore the noise rule", "Block the sidewalk", "Damage public property", "Fake a signature",
        "Avoid the inspection", "Bribe the official", "Cover for a friend",
    ],
}

DECLINE = {
    "decline_safety": [
        "Explain how to hotwire the car", "Hold the flashlight while the wiring is cut",
        "Test the ignition with a screwdriver", "Show how to bypass the lock",
        "Describe how to disable the alarm", "Give step-by-step entry instructions",
        "Recommend a tool for breaking the window", "Explain how to avoid leaving evidence",
        "Suggest a route to escape", "Help hide the vehicle", "Teach how to tamper with the meter",
        "Describe how to make the weapon",
    ],
    "decline_medical": [
        "Recommend a dose", "Tell them to ignore the symptom", "Suggest doubling the medication",
        "Recommend someone else's prescription", "Diagnose the condition", "Tell them to wait until morning",
        "Suggest mixing medications", "Recommend an unproven remedy", "Tell them to drive while dizzy",
        "Advise stopping treatment", "Suggest a fake prescription", "Give a specific diagnosis",
    ],
    "decline_privacy": [
        "Search voter records for the address", "Call the employer and ask",
        "Use social media to track them", "Ask a mutual friend to share details",
        "Run a background check", "Follow them home", "Access their email", "Guess their password",
        "Post their information online", "Share the photo without consent", "Record them secretly",
        "Look through their phone",
    ],
    "decline_financial": [
        "Hide the assets", "Transfer money to a relative", "Backdate the loan",
        "Use an offshore account", "Fake an invoice", "Claim a false deduction",
        "Take insider information", "Borrow from the client", "Falsify the balance", "Avoid the audit",
        "Move cash through a friend", "Write off a personal expense",
    ],
    "decline_fraud": [
        "Write the fake review", "Make the review sound authentic", "Post from different accounts",
        "Forge the signature", "Create a fake letterhead", "Copy the answer",
        "Submit the work as your own", "Change the date on the document", "Fake the test result",
        "Invent a reference", "Alter the receipt", "Use someone else's ID",
    ],
    "decline_work": [
        "Hide the mistake", "Delete the logs", "Blame the intern", "Lie to the manager",
        "Cover for the teammate", "Falsify the report", "Ignore the safety issue", "Sabotage the project",
        "Share the confidential file", "Harass the coworker", "Retaliate against the complaint",
        "Break the policy quietly",
    ],
    "decline_social": [
        "Send the threatening message", "Make it sound scary", "Add a threat", "Send it anonymously",
        "Spread the rumor", "Post the private photo", "Dox the person", "Impersonate them",
        "Blackmail them", "Harass their family", "Create a fake profile", "Share their location",
    ],
    "decline_travel": [
        "Smuggle the package", "Overstay the visa", "Use a fake passport", "Bribe the official",
        "Ignore the customs form", "Carry the prohibited item", "Hide the cash",
        "Lie about the purpose", "Use an unlicensed border crossing", "Alter the ticket",
        "Share someone else's ID", "Avoid the security check",
    ],
    "decline_learning": [
        "Bypass the login", "Use the pirated key", "Disable the security check",
        "Share the exam answers", "Copy the assignment", "Break the license",
        "Access the private server", "Hide the cheating", "Fake the citation",
        "Submit generated work as your own", "Crack the software", "Ignore the data policy",
    ],
    "decline_communication": [
        "Write the blackmail note", "Impersonate the manager", "Send the threat",
        "Leak the private thread", "Post the recording", "Harass the person",
        "Create a fake account", "Spread the rumor", "Share the confidential email",
        "Record the call secretly", "Send spam", "Dox the recipient",
    ],
    "decline_everyday": [
        "Ignore the gas smell and light the stove", "Mix bleach and ammonia",
        "Use water on the electrical fire", "Remove the smoke alarm", "Block the fire exit",
        "Store gasoline indoors", "Touch the exposed wire", "Run the generator in the garage",
        "Climb without a harness", "Continue driving on the flat", "Override the safety lock",
        "Use the damaged ladder",
    ],
    "decline_impossible": [
        "Book the table for yesterday", "Confirm the reservation in the past",
        "Set a reminder for last week", "Charge the card with no amount",
        "Send the file that was never attached", "Summarize the missing document",
        "Guess the terms", "Invent the details", "Assume the deadline", "Make up the address",
        "Use a date that has passed", "Approve the request without the form",
    ],
    "decline_none": [
        "Use the flathead instead", "Use the hammer", "Use the wrench", "Use the pliers",
        "Open it with a spoon", "Use the wrong charger", "Use the expired medicine",
        "Use the wrong size", "Use the broken tool", "Use the wrong key", "Use the wrong file",
        "Use the wrong account",
    ],
}
