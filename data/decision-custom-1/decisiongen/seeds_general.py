"""Authored general-decision patterns. Each row becomes one card."""
from __future__ import annotations

from .lexicon import QUESTIONS


def P(pid, domain, clauses, wrong, rows, questions=None, slots=None):
    return {
        "id": pid, "domain": domain, "clauses": clauses, "wrong": wrong,
        "rows": rows, "questions": questions or QUESTIONS[domain], "slots": slots or {},
    }


PATTERNS = []

# 1. Work priority
PATTERNS.append(P("priority", "work", [
    ("You have to {a} by {da}, and {b} by {db}.", "Your {relation} {name} is waiting for an update {time}."),
    ("Two tasks are due {time}: {a} by {da} and {b} by {db}.", "Your {relation} {name} asks what you're doing first at {place}."),
    ("I have to {a} by {da}, and {b} by {db}.", "My {relation} {name} is waiting for an update {time_i}."),
], "work_priority", [
    {"slots": {"a": "finish the client report", "b": "clean out the inbox", "da": "noon", "db": "Friday"},
     "best": ["Finish the client report first"], "wrong_extra": ["Clean out the inbox first"]},
    {"slots": {"a": "fix the outage affecting customers", "b": "update the internal wiki", "da": "10:30am", "db": "next week"},
     "best": ["Fix the customer outage first"], "wrong_extra": ["Update the wiki first"]},
    {"slots": {"a": "prepare the board deck", "b": "answer routine emails", "da": "3pm", "db": "end of day"},
     "best": ["Prepare the board deck first"], "wrong_extra": ["Answer routine emails first"]},
    {"slots": {"a": "call the upset client", "b": "organize the desk", "da": "5pm", "db": "sometime this week"},
     "best": ["Call the upset client first"], "wrong_extra": ["Organize the desk first"]},
    {"slots": {"a": "submit the compliance form", "b": "plan the team lunch", "da": "today", "db": "next month"},
     "best": ["Submit the compliance form first"], "wrong_extra": ["Plan the team lunch first"]},
    {"slots": {"a": "review the security patch", "b": "tweak the dashboard colors", "da": "now", "db": "Monday"},
     "best": ["Review the security patch first"], "wrong_extra": ["Tweak the dashboard colors first"]},
    {"slots": {"a": "send the overdue invoice", "b": "research new software", "da": "end of day", "db": "next quarter"},
     "best": ["Send the overdue invoice first"], "wrong_extra": ["Research new software first"]},
    {"slots": {"a": "prepare tomorrow's demo", "b": "clean up old tickets", "da": "tomorrow morning", "db": "this month"},
     "best": ["Prepare tomorrow's demo first"], "wrong_extra": ["Clean up old tickets first"]},
    {"slots": {"a": "fix the payroll error", "b": "update LinkedIn", "da": "today", "db": "next year"},
     "best": ["Fix the payroll error first"], "wrong_extra": ["Update LinkedIn first"]},
    {"slots": {"a": "approve the hiring packet", "b": "read industry news", "da": "before the interview", "db": "later today"},
     "best": ["Approve the hiring packet first"], "wrong_extra": ["Read industry news first"]},
], slots={"relation": ["manager", "teammate", "client", "director"], "place": ["the office", "the break room", "the conference room"], "time_i": ["today", "right now", "this morning", "before lunch", "this afternoon", "tonight", "before the deadline", "this week", "over the weekend", "first thing tomorrow"]}))

# 2. Social events
PATTERNS.append(P("social_event", "social", [
    ("Your {relation} {name} just {event}.", "They're telling you at {place} {time}."),
    ("At {place} {time}, your {relation} {name} shares some news: they just {event}.", "They seem to be waiting for your reaction."),
    ("My {relation} {name} just {event}.", "They're telling me at {place} {time}."),
], "social_positive", [
    {"slots": {"event": "got promoted", "relation": "coworker"}, "best": ["Congratulate them sincerely"]},
    {"slots": {"event": "got engaged", "relation": "friend"}, "best": ["Offer warm congratulations"]},
    {"slots": {"event": "had a baby", "relation": "sibling"}, "best": ["Congratulate them and ask how everyone is doing"]},
    {"slots": {"event": "graduated", "relation": "friend"}, "best": ["Celebrate the achievement with them"]},
    {"slots": {"event": "bought their first home", "relation": "coworker"}, "best": ["Congratulate them on the new home"]},
    {"slots": {"event": "retired", "relation": "manager"}, "best": ["Congratulate them and wish them well"]},
    {"slots": {"event": "passed a difficult exam", "relation": "friend"}, "best": ["Tell them you're proud of them"]},
    {"slots": {"event": "landed a new job", "relation": "neighbor"}, "best": ["Congratulate them on the new role"]},
    {"slots": {"event": "recovered from surgery", "relation": "sibling"}, "best": ["Say you're glad they're recovering"]},
    {"slots": {"event": "won a community award", "relation": "teammate"}, "best": ["Congratulate them on the recognition"]},
    {"slots": {"event": "had to say goodbye to their dog", "relation": "coworker"}, "best": ["Offer sincere condolences"], "wrong": "social_negative"},
    {"slots": {"event": "lost their job", "relation": "friend"}, "best": ["Listen and offer support"], "wrong": "social_negative"},
    {"slots": {"event": "went through a breakup", "relation": "friend"}, "best": ["Listen and acknowledge how hard it is"], "wrong": "social_negative"},
    {"slots": {"event": "got bad medical news", "relation": "sibling"}, "best": ["Ask what kind of support they want"], "wrong": "social_negative"},
], slots={"relation": ["friend", "coworker", "neighbor", "sibling", "teammate"], "place": ["the office", "a cafe", "the park", "home"]}))

# 3. Social boundaries
PATTERNS.append(P("social_boundary", "social", [
    ("Your {relation} {name} {request} {time}.", "You're at {place} and don't want to agree."),
    ("At {place} {time}, your {relation} {name} {request}.", "You feel pressured to say yes."),
], "social_boundary", [
    {"slots": {"request": "asks to borrow your car for the weekend"}, "best": ["Decline politely and explain why"]},
    {"slots": {"request": "asks for a large loan"}, "best": ["Say no clearly and kindly"]},
    {"slots": {"request": "invites you to an event you don't want to attend"}, "best": ["Decline politely without over-explaining"]},
    {"slots": {"request": "asks you to cover their shift again"}, "best": ["Set a boundary about repeated coverage"]},
    {"slots": {"request": "wants to vent for hours"}, "best": ["Set a time limit and listen briefly"]},
    {"slots": {"request": "asks for free professional work"}, "best": ["Decline or offer your paid rate"]},
    {"slots": {"request": "asks you to keep a secret that feels wrong"}, "best": ["Say you can't promise that"]},
    {"slots": {"request": "asks you to lie for them"}, "best": ["Refuse and explain your boundary"]},
    {"slots": {"request": "asks to borrow expensive gear"}, "best": ["Decline and suggest a rental option"]},
    {"slots": {"request": "asks to stay at your place indefinitely"}, "best": ["Offer a short, clear limit"]},
], slots={"relation": ["friend", "coworker", "neighbor", "sibling", "teammate"], "place": ["the office", "a cafe", "the park", "home"]}))

# 4. Cooking substitution
PATTERNS.append(P("substitution", "everyday", [
    ("You're making {dish} in {place} {time} and realize you're out of {ingredient}.", "The store is closed and you need a substitute."),
    ("Halfway through {dish}, you find there is no {ingredient} left in {place}.", "You're in {place} {time} and the store is closed."),
    ("I'm making {dish} in {place} {time} and realize I'm out of {ingredient}.", "The store is closed and I need a substitute."),
], "everyday_fix", [
    {"slots": {"dish": "pasta sauce", "ingredient": "garlic"}, "best": ["Use garlic powder instead"]},
    {"slots": {"dish": "pancakes", "ingredient": "buttermilk"}, "best": ["Use milk with a little lemon juice"]},
    {"slots": {"dish": "cookies", "ingredient": "eggs"}, "best": ["Use a flaxseed or applesauce substitute"]},
    {"slots": {"dish": "cake", "ingredient": "butter"}, "best": ["Use a neutral oil instead"]},
    {"slots": {"dish": "soup", "ingredient": "cream"}, "best": ["Use milk with a little butter"]},
    {"slots": {"dish": "salad dressing", "ingredient": "lemon"}, "best": ["Use lime juice instead"]},
    {"slots": {"dish": "stir-fry", "ingredient": "soy sauce"}, "best": ["Use tamari or a little salt"]},
    {"slots": {"dish": "tea", "ingredient": "honey"}, "best": ["Use sugar syrup instead"]},
    {"slots": {"dish": "meatballs", "ingredient": "breadcrumbs"}, "best": ["Use crushed crackers instead"]},
    {"slots": {"dish": "risotto", "ingredient": "wine"}, "best": ["Use broth with a splash of vinegar"]},
    {"slots": {"dish": "gravy", "ingredient": "cornstarch"}, "best": ["Use flour and cook it a little longer"]},
    {"slots": {"dish": "brownies", "ingredient": "vanilla"}, "best": ["Use maple syrup or skip it"]},
], slots={"place": ["the kitchen", "a friend's kitchen"], "dish": ["pasta sauce", "pancakes", "cookies", "cake", "soup", "salad dressing", "stir-fry", "tea", "meatballs", "risotto", "gravy", "brownies"]}))

# 5. Everyday repair
PATTERNS.append(P("repair", "everyday", [
    ("Your {object} is {problem} at {place} {time}.", "You need it working soon."),
    ("At {place} {time}, your {object} starts to {problem}.", "You have limited time to deal with it."),
    ("My {object} is {problem} at {place} {time}.", "I need it working soon."),
], "everyday_fix", [
    {"slots": {"object": "phone", "problem": "not charging"}, "best": ["Check the cable and outlet first"]},
    {"slots": {"object": "laptop", "problem": "running very slowly"}, "best": ["Close heavy apps and restart it"]},
    {"slots": {"object": "fridge", "problem": "not staying cold"}, "best": ["Check the seal and temperature setting"]},
    {"slots": {"object": "washing machine", "problem": "leaking water"}, "best": ["Shut off the water and check the hose"]},
    {"slots": {"object": "bike tire", "problem": "flat"}, "best": ["Patch or replace the tube"]},
    {"slots": {"object": "printer", "problem": "jammed"}, "best": ["Turn it off and clear the paper path"]},
    {"slots": {"object": "Wi-Fi", "problem": "dropping"}, "best": ["Restart the router and check the connection"]},
    {"slots": {"object": "kitchen sink", "problem": "clogged"}, "best": ["Use a plunger before chemicals"]},
    {"slots": {"object": "car", "problem": "not starting"}, "best": ["Check the battery and connections"]},
    {"slots": {"object": "smoke detector", "problem": "chirping"}, "best": ["Replace the battery"]},
    {"slots": {"object": "door lock", "problem": "sticking"}, "best": ["Lubricate the lock and check alignment"]},
    {"slots": {"object": "toilet", "problem": "running constantly"}, "best": ["Adjust or replace the flapper"]},
], slots={"place": ["home", "the office"], "object": ["phone", "laptop", "fridge", "washing machine", "bike tire", "printer", "Wi-Fi", "kitchen sink", "car", "smoke detector", "door lock", "toilet"]}))

# 6. First aid
PATTERNS.append(P("first_aid", "health", [
    ("You {symptom} at {place} {time}.", "You're not sure what to do."),
    ("At {place} {time}, you {symptom}.", "You need to decide what to do next."),
], "health_safety", [
    {"slots": {"symptom": "feel dizzy after standing up"}, "best": ["Sit down and drink some water"]},
    {"slots": {"symptom": "burn your hand on a hot pan"}, "best": ["Cool the burn under running water"]},
    {"slots": {"symptom": "get a deep cut on your finger"}, "best": ["Apply pressure and seek medical help"]},
    {"slots": {"symptom": "see someone choking"}, "best": ["Call for help and start choking first aid"]},
    {"slots": {"symptom": "feel chest pain and arm numbness"}, "best": ["Call emergency services immediately"]},
    {"slots": {"symptom": "have a severe allergic reaction"}, "best": ["Use epinephrine if prescribed and call for help"]},
    {"slots": {"symptom": "sprain your ankle"}, "best": ["Rest, ice, compress and elevate it"]},
    {"slots": {"symptom": "get a nosebleed"}, "best": ["Lean forward and pinch the nose"]},
    {"slots": {"symptom": "feel faint in the heat"}, "best": ["Move to shade, cool down and hydrate"]},
    {"slots": {"symptom": "touch a live wire"}, "best": ["Do not touch the source; call for help"]},
    {"slots": {"symptom": "get chemicals in your eye"}, "best": ["Rinse with water and seek help"]},
    {"slots": {"symptom": "have food poisoning symptoms"}, "best": ["Hydrate and seek care if it worsens"]},
], slots={"place": ['home', 'the office', 'the gym', 'the park'], "symptom": ["feel dizzy after standing up", "burn your hand on a hot pan", "get a deep cut on your finger", "see someone choking", "feel chest pain and arm numbness", "have a severe allergic reaction", "sprain your ankle", "get a nosebleed", "feel faint in the heat", "touch a live wire", "get chemicals in your eye", "have food poisoning symptoms"]}))

# 7. Health habits
PATTERNS.append(P("habit", "health", [
    ("You want to {goal} but {problem} at {place} {time}.", "You need a realistic next step."),
    ("At {place} {time}, you're trying to {goal}, but {problem}.", "You're tempted to give up."),
], "health_habit", [
    {"slots": {"goal": "sleep better", "problem": "you keep scrolling late at night"}, "best": ["Set a consistent bedtime and put the phone away"]},
    {"slots": {"goal": "start exercising", "problem": "you keep planning an extreme routine"}, "best": ["Start with a short, sustainable routine"]},
    {"slots": {"goal": "eat healthier", "problem": "you skip meals and snack later"}, "best": ["Plan simple regular meals"]},
    {"slots": {"goal": "reduce stress", "problem": "you never take breaks"}, "best": ["Schedule short breaks during the day"]},
    {"slots": {"goal": "drink less caffeine", "problem": "you drink coffee all afternoon"}, "best": ["Set a caffeine cutoff time"]},
    {"slots": {"goal": "recover from an injury", "problem": "you want to train through the pain"}, "best": ["Follow the recovery plan and rest"]},
    {"slots": {"goal": "build a walking habit", "problem": "you keep waiting for perfect weather"}, "best": ["Walk indoors or dress for the weather"]},
    {"slots": {"goal": "improve your posture", "problem": "you sit all day"}, "best": ["Take movement breaks and adjust your setup"]},
], slots={"place": ['home', 'the office', 'the gym'], "goal": ["sleep better", "start exercising", "eat healthier", "reduce stress", "drink less caffeine", "recover from an injury", "build a walking habit", "improve your posture"]}))

# 8. Consumer problems
PATTERNS.append(P("consumer", "money", [
    ("You notice {problem} on your {account} at {place} {time}.", "The amount is {amount}."),
    ("At {place} {time}, you discover {problem} on your {account}.", "It's for {amount} and you didn't expect it."),
    ("I notice {problem} on my {account} at {place} {time}.", "The amount is {amount}."),
], "money_consumer", [
    {"slots": {"problem": "a duplicate charge", "account": "credit card"}, "best": ["Contact the card issuer and dispute the charge"]},
    {"slots": {"problem": "an unauthorized subscription", "account": "card"}, "best": ["Cancel it and ask for a refund"]},
    {"slots": {"problem": "a package that never arrived", "account": "order"}, "best": ["Contact the seller and request a replacement"]},
    {"slots": {"problem": "an item that arrived damaged", "account": "order"}, "best": ["Request a replacement or refund"]},
    {"slots": {"problem": "the wrong item in the box", "account": "order"}, "best": ["Contact the seller for an exchange"]},
    {"slots": {"problem": "a denied warranty claim", "account": "purchase"}, "best": ["Appeal with proof of purchase"]},
    {"slots": {"problem": "an unexpected ATM fee", "account": "bank account"}, "best": ["Ask the bank to reverse the fee"]},
    {"slots": {"problem": "an unexpected subscription renewal", "account": "card"}, "best": ["Cancel it and ask for a refund"]},
    {"slots": {"problem": "an unrecognized cash withdrawal", "account": "bank account"}, "best": ["Call the bank immediately"]},
    {"slots": {"problem": "a fraudulent transfer", "account": "bank account"}, "best": ["Call the bank immediately"]},
    {"slots": {"problem": "an error on a hotel bill", "account": "hotel bill"}, "best": ["Ask for an itemized bill and correction"]},
    {"slots": {"problem": "a delayed insurance claim", "account": "insurance policy"}, "best": ["Follow up in writing and ask for a timeline"]},
], slots={"place": ["home", "the office", "a cafe"], "amount": ["$18", "$42", "$79", "$120", "$250", "$480", "$9.99", "$35", "$67", "$310", "$1,200", "$24"]}))

# 9. Budget decisions
PATTERNS.append(P("budget", "money", [
    ("You're reviewing your budget at {place} {time}.", "{problem}"),
    ("At {place} {time}, you look at your budget.", "{problem}"),
], "money_budget", [
    {"slots": {"problem": "Rent is due and the balance is tight."}, "best": ["Cover essentials first and delay optional spending"]},
    {"slots": {"problem": "Your credit card balance is growing."}, "best": ["Pay more than the minimum and stop new charges"]},
    {"slots": {"problem": "You have no emergency fund."}, "best": ["Start a small automatic transfer each month"]},
    {"slots": {"problem": "Groceries are over budget."}, "best": ["Plan meals and shop with a list"]},
    {"slots": {"problem": "You want an expensive impulse buy."}, "best": ["Wait 24 hours before deciding"]},
    {"slots": {"problem": "Several unused subscriptions are renewing."}, "best": ["Cancel the ones you don't use"]},
    {"slots": {"problem": "A loan offer looks tempting."}, "best": ["Compare the total cost and interest rate"]},
    {"slots": {"problem": "You got an unexpected bonus."}, "best": ["Save a portion before spending"]},
    {"slots": {"problem": "A repair bill is due."}, "best": ["Use the emergency fund and rebuild it"]},
    {"slots": {"problem": "Holiday spending is creeping up."}, "best": ["Set a clear limit and track gifts"]},
], slots={"place": ["home", "the office"], "problem": ["Rent is due and the balance is tight.", "Your credit card balance is growing.", "You have no emergency fund.", "Groceries are over budget.", "You want an expensive impulse buy.", "Several unused subscriptions are renewing.", "A loan offer looks tempting.", "You got an unexpected bonus.", "A repair bill is due.", "Holiday spending is creeping up."]}))

# 10. Purchase choices
PATTERNS.append(P("purchase", "money", [
    ("You need {item} at {place} {time}.", "Your budget is {budget} and {constraint}."),
    ("At {place} {time}, you're shopping for {item}.", "You can spend {budget}, but {constraint}."),
], "money_consumer", [
    {"slots": {"item": "a laptop", "budget": "$800", "constraint": "the cheaper model has a poor warranty"}, "best": ["Compare specs and warranty before buying"]},
    {"slots": {"item": "a winter coat", "budget": "$150", "constraint": "you need it for a cold trip"}, "best": ["Choose a warm coat within budget"]},
    {"slots": {"item": "a replacement phone", "budget": "$400", "constraint": "you need a reliable battery"}, "best": ["Buy a reputable refurbished model"]},
    {"slots": {"item": "a mattress", "budget": "$600", "constraint": "you can't try it in person"}, "best": ["Choose a seller with a return policy"]},
    {"slots": {"item": "a used car", "budget": "$6,000", "constraint": "the history is unclear"}, "best": ["Get an inspection before buying"]},
    {"slots": {"item": "headphones", "budget": "$120", "constraint": "reviews are mixed"}, "best": ["Compare return terms and sound quality"]},
    {"slots": {"item": "a dishwasher", "budget": "$700", "constraint": "installation costs extra"}, "best": ["Include installation in the total cost"]},
    {"slots": {"item": "running shoes", "budget": "$100", "constraint": "you have wide feet"}, "best": ["Try them on or choose a wide fit"]},
    {"slots": {"item": "an office chair", "budget": "$250", "constraint": "you sit for long hours"}, "best": ["Prioritize support and adjustability"]},
    {"slots": {"item": "a camera", "budget": "$500", "constraint": "you mainly shoot indoors"}, "best": ["Compare low-light performance"]},
], slots={"place": ['the store', 'the mall', 'the electronics store'], "budget": ["$800", "$150", "$400", "$600", "$6,000", "$120", "$700", "$100", "$250", "$500"]}))

# 11. Travel disruption
PATTERNS.append(P("travel_disruption", "travel", [
    ("Your {transport} is {disruption} {time}.", "You need to {goal}."),
    ("You find out {time} that your {transport} is {disruption}.", "You still need to {goal}."),
    ("My {transport} is {disruption} {time}.", "I still need to {goal}."),
], "travel_disruption", [
    {"slots": {"transport": "flight", "disruption": "canceled", "goal": "reach a meeting tomorrow"}, "best": ["Ask the airline to rebook you"]},
    {"slots": {"transport": "train", "disruption": "delayed by two hours", "goal": "make a dinner reservation"}, "best": ["Check alternatives and update the reservation"]},
    {"slots": {"transport": "checked bag", "disruption": "lost", "goal": "get medication"}, "best": ["File a baggage claim and ask for essentials"]},
    {"slots": {"transport": "connection", "disruption": "missed", "goal": "get to the final city tonight"}, "best": ["Go to the airline desk for the next connection"]},
    {"slots": {"transport": "hotel", "disruption": "overbooked", "goal": "find a place to sleep"}, "best": ["Ask the hotel for a comparable alternative"]},
    {"slots": {"transport": "rental car", "disruption": "unavailable", "goal": "drive to the client site"}, "best": ["Ask for another car or a partner agency"]},
    {"slots": {"transport": "passport", "disruption": "stolen", "goal": "get home safely"}, "best": ["Contact your embassy and report the theft"]},
    {"slots": {"transport": "flight", "disruption": "delayed by weather", "goal": "make a same-day event"}, "best": ["Check the airline app and rebook early"]},
    {"slots": {"transport": "train", "disruption": "canceled by a strike", "goal": "reach the conference"}, "best": ["Find a bus or alternate route"]},
    {"slots": {"transport": "flight", "disruption": "overbooked", "goal": "keep the plans"}, "best": ["Ask about compensation and the next flight"]},
    {"slots": {"transport": "baggage", "disruption": "delayed", "goal": "attend a wedding"}, "best": ["File a report and buy essentials"]},
    {"slots": {"transport": "ferry", "disruption": "canceled", "goal": "reach the island"}, "best": ["Ask about the next crossing or a replacement"]},
], slots={"goal": ["reach a meeting tomorrow", "make a dinner reservation", "get medication", "get to the final city tonight", "find a place to sleep", "drive to the client site", "get home safely", "make a same-day event", "reach the conference", "keep the plans", "attend a wedding", "reach the island"]}))

# 12. Travel planning
PATTERNS.append(P("travel_planning", "travel", [
    ("You're planning a trip at {place} {time}.", "{problem}"),
    ("At {place} {time}, you're preparing for a trip.", "{problem}"),
], "travel_planning", [
    {"slots": {"problem": "You're unsure about the visa rules."}, "best": ["Check the official embassy website"]},
    {"slots": {"problem": "You always overpack."}, "best": ["Make a short packing list by activity"]},
    {"slots": {"problem": "You need a reliable airport transfer."}, "best": ["Book a licensed transfer in advance"]},
    {"slots": {"problem": "You're worried about trip cancellation."}, "best": ["Buy travel insurance that covers it"]},
    {"slots": {"problem": "You don't know the real daily cost."}, "best": ["Set a daily budget with a buffer"]},
    {"slots": {"problem": "You need mobile data abroad."}, "best": ["Compare a local SIM and roaming plans"]},
    {"slots": {"problem": "You take daily medication."}, "best": ["Carry the prescription and extra doses"]},
    {"slots": {"problem": "You're traveling alone to a new city."}, "best": ["Share your itinerary and use licensed transport"]},
    {"slots": {"problem": "Your plans may change."}, "best": ["Choose refundable bookings when possible"]},
    {"slots": {"problem": "You're worried about losing documents."}, "best": ["Keep digital and paper copies separate"]},
], slots={"place": ["home", "a cafe", "the hotel lobby"], "problem": ["You're unsure about the visa rules.", "You always overpack.", "You need a reliable airport transfer.", "You're worried about trip cancellation.", "You don't know the real daily cost.", "You need mobile data abroad.", "You take daily medication.", "You're traveling alone to a new city.", "Your plans may change.", "You're worried about losing documents."]}))

# 13. Debugging
PATTERNS.append(P("debug", "learning", [
    ("You're {task} at {place} {time} and {problem}.", "You've already {attempt}."),
    ("At {place} {time}, you're {task}, but {problem}.", "You tried to {attempt} already."),
    ("I'm {task} at {place} {time} and {problem}.", "I've already {attempt}."),
], "learning_debug", [
    {"slots": {"task": "fixing a failing test", "problem": "the error is unclear", "attempt": "rerun it twice"}, "best": ["Read the full error and reproduce it"]},
    {"slots": {"task": "debugging a slow query", "problem": "the page times out", "attempt": "restarted the server"}, "best": ["Measure the query and check the indexes"]},
    {"slots": {"task": "resolving a merge conflict", "problem": "the diff is confusing", "attempt": "accepted one side"}, "best": ["Compare both changes against the base"]},
    {"slots": {"task": "fixing a broken build", "problem": "the dependency is missing", "attempt": "cleared the cache"}, "best": ["Check the lockfile and install the missing package"]},
    {"slots": {"task": "investigating an API error", "problem": "it only fails in production", "attempt": "added a retry"}, "best": ["Add logging around the failing call"]},
    {"slots": {"task": "fixing a CSS layout", "problem": "it breaks on mobile", "attempt": "changed the font size"}, "best": ["Inspect the responsive layout and box model"]},
    {"slots": {"task": "tracking a memory leak", "problem": "usage keeps rising", "attempt": "restarted the process"}, "best": ["Profile memory and find retained objects"]},
    {"slots": {"task": "resolving a dependency conflict", "problem": "two versions disagree", "attempt": "deleted node_modules"}, "best": ["Pin compatible versions and read the resolver output"]},
    {"slots": {"task": "undoing a bad commit", "problem": "it is already pushed", "attempt": "edited the file manually"}, "best": ["Revert the commit with a new commit"]},
    {"slots": {"task": "fixing a production bug", "problem": "users are affected", "attempt": "added a quick patch locally"}, "best": ["Roll back or hotfix, then verify"]},
    {"slots": {"task": "debugging a regex", "problem": "it matches too much", "attempt": "added more characters"}, "best": ["Test the pattern against small examples"]},
    {"slots": {"task": "fixing a flaky test", "problem": "it passes randomly", "attempt": "increased the timeout"}, "best": ["Find the shared state or timing issue"]},
], slots={"place": ['the office', 'home', 'the coworking space'], "task": ["fixing a failing test", "debugging a slow query", "resolving a merge conflict", "fixing a broken build", "investigating an API error", "fixing a CSS layout", "tracking a memory leak", "resolving a dependency conflict", "undoing a bad commit", "fixing a production bug", "debugging a regex", "fixing a flaky test"]}))

# 14. Study
PATTERNS.append(P("study", "learning", [
    ("You're studying {subject} at {place} {time}.", "{problem}"),
    ("At {place} {time}, you're trying to learn {subject}.", "{problem}"),
], "learning_study", [
    {"slots": {"subject": "for an exam in three days", "problem": "You don't know where to start."}, "best": ["Make a short plan and practice the hardest topics"]},
    {"slots": {"subject": "a difficult chapter", "problem": "You keep rereading the same page."}, "best": ["Summarize it and test yourself"]},
    {"slots": {"subject": "an online course", "problem": "You're falling behind."}, "best": ["Schedule short regular sessions"]},
    {"slots": {"subject": "a new language", "problem": "You forget vocabulary quickly."}, "best": ["Use spaced repetition and daily practice"]},
    {"slots": {"subject": "for a certification", "problem": "The material is overwhelming."}, "best": ["Follow the official objectives and take practice tests"]},
    {"slots": {"subject": "for a presentation", "problem": "You freeze when rehearsing."}, "best": ["Practice aloud in short sections"]},
    {"slots": {"subject": "math problems", "problem": "You can follow solutions but not solve alone."}, "best": ["Work problems without looking, then review"]},
    {"slots": {"subject": "a dense reading", "problem": "You can't remember the argument."}, "best": ["Take notes and explain it in your own words"]},
    {"slots": {"subject": "for a practical skill", "problem": "You only watch videos."}, "best": ["Practice the skill hands-on"]},
    {"slots": {"subject": "for a deadline", "problem": "You keep switching tasks."}, "best": ["Use short focused blocks with breaks"]},
], slots={"place": ['the library', 'home', 'a cafe', 'the office'], "subject": ["for an exam in three days", "a difficult chapter", "an online course", "a new language", "for a certification", "for a presentation", "math problems", "a dense reading", "for a practical skill", "for a deadline"]}))

# 15. Security
PATTERNS.append(P("security", "learning", [
    ("You get {message} from {name} {time}.", "You're at {place} and something feels off."),
    ("At {place} {time}, {name} sends you {message}.", "It asks you to act quickly."),
], "learning_security", [
    {"slots": {"message": "an email asking you to reset your password"}, "best": ["Report it and don't click the link"]},
    {"slots": {"message": "a login alert from a new country"}, "best": ["Change your password and revoke sessions"]},
    {"slots": {"message": "a message asking for your 2FA code"}, "best": ["Never share the code; verify the request"]},
    {"slots": {"message": "a USB drive in the parking lot"}, "best": ["Do not plug it in; hand it to security"]},
    {"slots": {"message": "an urgent software update notice"}, "best": ["Install updates through the official app"]},
    {"slots": {"message": "a public Wi-Fi login page"}, "best": ["Avoid sensitive logins or use a VPN"]},
    {"slots": {"message": "a fake invoice from a supplier"}, "best": ["Verify it through a known contact"]},
    {"slots": {"message": "a request for admin access"}, "best": ["Confirm the need and use least privilege"]},
    {"slots": {"message": "a password reset you didn't request"}, "best": ["Secure the account and check activity"]},
    {"slots": {"message": "a link to a shared document"}, "best": ["Check the sender and domain before opening"]},
], slots={"place": ['the office', 'home', 'a cafe', 'the airport'], "name": ["a colleague", "your bank", "a supplier", "an unknown sender", "your manager", "a delivery service", "the IT team", "a client"]}))

# 16. Meeting facilitation
PATTERNS.append(P("meeting", "work", [
    ("You're leading a meeting at {place} {time}.", "{problem}"),
    ("At {place} {time}, you're running a meeting.", "{problem}"),
], "work_conflict", [
    {"slots": {"problem": "Two people start arguing."}, "best": ["Interrupt and refocus on the agenda"]},
    {"slots": {"problem": "The meeting is running over."}, "best": ["Summarize decisions and take the rest offline"]},
    {"slots": {"problem": "There is no agenda."}, "best": ["Set a short agenda before continuing"]},
    {"slots": {"problem": "A remote participant is being ignored."}, "best": ["Invite them in and repeat key points"]},
    {"slots": {"problem": "The group is stuck on one decision."}, "best": ["Name the options and assign a decision owner"]},
    {"slots": {"problem": "One person is dominating."}, "best": ["Ask others for input and set a time limit"]},
    {"slots": {"problem": "Action items are unclear."}, "best": ["Assign owners and deadlines before ending"]},
    {"slots": {"problem": "A confidential topic comes up."}, "best": ["Pause and move it to a private discussion"]},
    {"slots": {"problem": "Someone's phone keeps ringing."}, "best": ["Ask people to mute devices"]},
    {"slots": {"problem": "A key attendee is late."}, "best": ["Start with the items that don't need them"]},
], slots={"place": ['the office', 'the conference room', 'the break room'], "problem": ["Two people start arguing.", "The meeting is running over.", "There is no agenda.", "A remote participant is being ignored.", "The group is stuck on one decision.", "One person is dominating.", "Action items are unclear.", "A confidential topic comes up.", "Someone's phone keeps ringing.", "A key attendee is late."]}))

# 17. Email
PATTERNS.append(P("email", "work", [
    ("You need to reply to {name} about {topic} {time}.", "You're at {place} and the thread is tense."),
    ("At {place} {time}, {name} emails you about {topic}.", "The message needs a careful response."),
], "work_communication", [
    {"slots": {"topic": "a missed deadline"}, "best": ["Apologize briefly and give a new timeline"]},
    {"slots": {"topic": "an angry complaint"}, "best": ["Acknowledge the issue and offer a concrete next step"]},
    {"slots": {"topic": "a request for a raise"}, "best": ["Acknowledge it and schedule a private discussion"]},
    {"slots": {"topic": "an unclear request"}, "best": ["Ask one focused clarifying question"]},
    {"slots": {"topic": "a sensitive document sent to the wrong person"}, "best": ["Ask them to delete it and notify the owner"]},
    {"slots": {"topic": "a meeting request"}, "best": ["Confirm the purpose and propose a time"]},
    {"slots": {"topic": "a follow-up you missed"}, "best": ["Reply with an update and a clear next step"]},
    {"slots": {"topic": "an apology you owe"}, "best": ["Apologize directly and explain the fix"]},
    {"slots": {"topic": "an invitation you can't accept"}, "best": ["Decline politely and suggest an alternative"]},
    {"slots": {"topic": "a request to work overtime"}, "best": ["Clarify priorities before agreeing"]},
], slots={"place": ['the office', 'home', 'the break room'], "name": ["a client", "your manager", "a teammate", "a supplier", "a customer", "a partner"],
          "topic": ["a missed deadline", "an angry complaint", "a request for a raise", "an unclear request",
                    "a sensitive document sent to the wrong person", "a meeting request", "a follow-up you missed",
                    "an apology you owe", "an invitation you can't accept", "a request to work overtime"]}))

# 18. Quality
PATTERNS.append(P("quality", "work", [
    ("You're reviewing {artifact} for {name} {time}.", "{problem}"),
    ("At {place} {time}, you're checking {artifact} before it goes out.", "{problem}"),
], "work_quality", [
    {"slots": {"artifact": "a release candidate", "problem": "You find a serious bug."}, "best": ["Block the release and report the bug"]},
    {"slots": {"artifact": "a code change", "problem": "The tests are missing."}, "best": ["Ask for tests before approving"]},
    {"slots": {"artifact": "a quarterly report", "problem": "One number looks wrong."}, "best": ["Verify the source before publishing"]},
    {"slots": {"artifact": "a contract", "problem": "There is a typo in the amount."}, "best": ["Flag it and get a corrected version"]},
    {"slots": {"artifact": "a test suite", "problem": "A failure is being ignored."}, "best": ["Investigate the failure before merging"]},
    {"slots": {"artifact": "a customer complaint", "problem": "The root cause is unclear."}, "best": ["Gather details and reproduce the issue"]},
    {"slots": {"artifact": "a data export", "problem": "The totals don't match."}, "best": ["Reconcile the data and fix the query"]},
    {"slots": {"artifact": "a product requirement", "problem": "A key case is missing."}, "best": ["Raise the gap before development starts"]},
], slots={"place": ['the office', 'the conference room', 'home'], "artifact": ["a release candidate", "a code change", "a quarterly report", "a contract", "a test suite", "a customer complaint", "a data export", "a product requirement"]}))

# 19. Tone
PATTERNS.append(P("tone", "communication", [
    ("Your {relation} {name} sent {message} {time}.", "You're at {place} and feel upset."),
    ("At {place} {time}, your {relation} {name} sends {message}.", "The tone is already tense."),
], "communication_tone", [
    {"slots": {"message": "a sarcastic message about your work"}, "best": ["Respond calmly and ask what they meant"]},
    {"slots": {"message": "an all-caps email about a mistake"}, "best": ["Acknowledge the issue and propose a fix"]},
    {"slots": {"message": "a passive-aggressive note"}, "best": ["Ask for a direct conversation"]},
    {"slots": {"message": "a late-night text about a disagreement"}, "best": ["Wait until morning and reply calmly"]},
    {"slots": {"message": "a public criticism in a group chat"}, "best": ["Move the discussion to a private channel"]},
    {"slots": {"message": "a confusing voice note"}, "best": ["Ask them to summarize it in writing"]},
    {"slots": {"message": "a joke about a sensitive topic"}, "best": ["Say it didn't land and explain why"]},
    {"slots": {"message": "a message that interrupts you repeatedly"}, "best": ["Ask to finish your point first"]},
    {"slots": {"message": "a blaming message"}, "best": ["Focus on facts and next steps"]},
    {"slots": {"message": "a gossipy message about a coworker"}, "best": ["Avoid spreading it and change the subject"]},
], slots={"place": ['the office', 'home', 'a cafe'], "relation": ["coworker", "friend", "manager", "teammate", "client"]}))

# 20. Conflict
PATTERNS.append(P("conflict", "communication", [
    ("Your {relation} {name} {behavior} at {place} {time}.", "Other people are watching."),
    ("At {place} {time}, your {relation} {name} {behavior}.", "You need to respond."),
], "communication_conflict", [
    {"slots": {"behavior": "takes credit for your idea in a meeting"}, "best": ["Speak to them privately afterward"]},
    {"slots": {"behavior": "cancels plans with you repeatedly"}, "best": ["Tell them how it affects you and set a boundary"]},
    {"slots": {"behavior": "keeps playing loud music"}, "best": ["Ask them politely to lower it"]},
    {"slots": {"behavior": "brings up an old argument at dinner"}, "best": ["Suggest discussing it calmly later"]},
    {"slots": {"behavior": "misses another deadline"}, "best": ["Talk through blockers and agree on a plan"]},
    {"slots": {"behavior": "speaks rudely to a server"}, "best": ["Address it privately and apologize to the server"]},
    {"slots": {"behavior": "criticizes your work in front of the team"}, "best": ["Ask for feedback in private next time"]},
    {"slots": {"behavior": "shares your private news"}, "best": ["Tell them it wasn't theirs to share"]},
    {"slots": {"behavior": "borrows your things without asking"}, "best": ["Set a clear rule about asking first"]},
    {"slots": {"behavior": "starts a heated group chat argument"}, "best": ["Move the conversation offline"]},
], slots={"place": ['the office', 'home', 'a restaurant', 'the break room'], "relation": ["coworker", "friend", "neighbor", "sibling", "teammate"]}))

# 21. Integrity
PATTERNS.append(P("integrity", "ethics", [
    ("You {situation} at {place} {time}.", "No one would know if you stayed quiet."),
    ("At {place} {time}, you {situation}.", "The easy option is dishonest."),
    ("I {situation_i} at {place} {time}.", "No one would know if I stayed quiet."),
], "ethics_integrity", [
    {"slots": {"situation": "find a wallet with cash and an ID"}, "best": ["Turn it in to lost and found"]},
    {"slots": {"situation": "get too much change from a cashier"}, "best": ["Return the extra change"]},
    {"slots": {"situation": "realize you caused a mistake at work"}, "best": ["Report it and help fix it"]},
    {"slots": {"situation": "are asked to cover for a friend's absence"}, "best": ["Refuse to lie and suggest an honest option"]},
    {"slots": {"situation": "notice an expense report is inflated"}, "best": ["Flag it and correct the amount"]},
    {"slots": {"situation": "see a coworker copy someone else's work"}, "best": ["Raise it with the appropriate person"]},
    {"slots": {"situation": "have a conflict of interest on a vendor choice"}, "best": ["Disclose it and step back"]},
    {"slots": {"situation": "find an error in your favor on a bill"}, "best": ["Report it and pay the correct amount"]},
    {"slots": {"situation": "are tempted to exaggerate your resume"}, "best": ["Keep it accurate and honest"]},
    {"slots": {"situation": "see data that doesn't support the project"}, "best": ["Share the data honestly"]},
    {"slots": {"situation": "are offered a refund you don't deserve"}, "best": ["Decline it and explain why"]},
    {"slots": {"situation": "find a lost item in a taxi"}, "best": ["Try to return it or hand it to the driver"]},
], slots={"place": ['the office', 'the grocery store', 'a cafe', 'the bank'], "situation": ["find a wallet with cash and an ID", "get too much change from a cashier", "realize you caused a mistake at work",
                         "are asked to cover for a friend's absence", "notice an expense report is inflated",
                         "see a coworker copy someone else's work", "have a conflict of interest on a vendor choice",
                         "find an error in your favor on a bill", "are tempted to exaggerate your resume",
                         "see data that doesn't support the project", "are offered a refund you don't deserve",
                         "find a lost item in a taxi"], "situation_i": ["find a wallet with cash and an ID",
                         "get too much change from a cashier", "realize I caused a mistake at work",
                         "get asked to cover for a friend's absence", "notice an expense report is inflated",
                         "see a coworker copy someone else's work", "have a conflict of interest on a vendor choice",
                         "find an error in my favor on a bill", "feel tempted to exaggerate my resume",
                         "see data that doesn't support the project", "get offered a refund I don't deserve",
                         "find a lost item in a taxi"]}))

# 22. Civic
PATTERNS.append(P("civic", "ethics", [
    ("You notice {problem} at {place} {time}.", "Other people are ignoring it."),
    ("At {place} {time}, you see {problem}.", "You're not sure whether to get involved."),
], "ethics_civic", [
    {"slots": {"problem": "a broken streetlight"}, "best": ["Report it to the city"]},
    {"slots": {"problem": "a neighbor's tree leaning over the road"}, "best": ["Talk to the neighbor and report the hazard"]},
    {"slots": {"problem": "litter blocking a drain"}, "best": ["Clear it safely or report it"]},
    {"slots": {"problem": "an unsafe crossing near a school"}, "best": ["Report it and warn other parents"]},
    {"slots": {"problem": "a loud late-night party"}, "best": ["Ask them politely to lower the noise"]},
    {"slots": {"problem": "vandalism in the park"}, "best": ["Report it and document the damage"]},
    {"slots": {"problem": "a lost dog running near traffic"}, "best": ["Keep it safe and call the owner or shelter"]},
    {"slots": {"problem": "a community fund with missing receipts"}, "best": ["Ask for transparency and documentation"]},
], slots={"place": ['the park', 'the sidewalk', 'the street corner', 'the bus stop'], "problem": ["a broken streetlight", "a neighbor's tree leaning over the road", "litter blocking a drain",
                     "an unsafe crossing near a school", "a loud late-night party", "vandalism in the park",
                     "a lost dog running near traffic", "a community fund with missing receipts"]}))

