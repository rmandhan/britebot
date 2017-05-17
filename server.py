from flask import Flask, request
from firebase import firebase
import json
import requests

app = Flask(__name__)
firebase = firebase.FirebaseApplication('XXXXXXX', None)

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
PAT = ''
TOKEN = ''

@app.route('/', methods=['GET'])
def handle_verification():
  print "Handling Verification."
  if request.args.get('hub.verify_token', '') == TOKEN:
    print "Verification successful!"
    return request.args.get('hub.challenge', '')
  else:
    print "Verification failed!"
    return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages():
  # Get Payload
  print "Handling Messages"
  payload = request.get_data()
  print payload
  for sender, message in messaging_events(payload):
    print "Sending %s: %s" % (sender, message)
    send_message(PAT, sender, message)
  return "ok"

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload."""
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    add_id_to_firebase(event["sender"]["id"])
    if "postback" in event:
      command = event["postback"]["payload"]
      if command == "SEARCH_EVENTS":
        search_events()
      else:
          yield event["sender"]["id"], "Gimme a sec!"
    elif "message" in event and "text" in event["message"]:
      yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't echo this"

def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient."""
  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": text.decode('unicode_escape')}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

def search_events():
  print "Searching Events"
  r1 = requests.get(
      'https://www.eventbriteapi.com/v3/events/search/?sort_by=best&location.latitude=37.774929&location.longitude=-122.419416&token=CG5YAYXYIV6SWNWAN7CV',
      params={})
  eventsData = r1.json()
  print eventsData

  eventsList = []

  if "events" in eventsData:
    events = eventsData["events"]
    for i in range (0, 5):
        event = events[i]
        print event
        eventName = event["name"]["text"]
        eventId = event["id"]
        eventURL = event["url"]
        if "logo" in event and "url" in event["logo"]:
          eventImageURL = event["logo"]["url"]
        else:
          eventImageURL = ""
        eventVenueID = event["venue_id"]

        r2 = requests.get('https://www.eventbriteapi.com/v3/venues/%s/?token=CG5YAYXYIV6SWNWAN7CV' % eventVenueID)
        venueData = r2.json()
        print venueData
        eventAddress = venueData["address"]["localized_address_display"]

        eventsList.append([eventName, eventId, eventImageURL, eventURL, eventAddress])
        # print eventName
        # print eventId
        # print eventImageURL
  else:
    print "No event data"
    return

  print eventsList
  send_events(eventsList)

# [0] = eventName
# [1] = eventId
# [2] = eventImageURL
# [3] = eventURL
# [4] = eventAddress
def send_events(events):
    messageData = json.dumps({
        "recipient": {
            "id": "1094580953965432"
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [{
                        "title": events[0][0],
                        "subtitle": events[0][4],
                        "item_url": events[0][3] ,
                        "image_url": events[0][2],
                        "buttons": [{
                            "type": "postback",
                            "title": "Tell Me More!",
                            "payload": "TELL_ME_MORE %s" % events[0][1]
                        }, {
                            "type": "postback",
                            "title": "Bookmark Event",
                            "payload": "BOOKMARK_EVENT %s" % events[0][1]
                        }],
                    }, {
                        "title": events[1][0],
                        "subtitle": events[1][4],
                        "item_url": events[1][3] ,
                        "image_url": events[1][2],
                        "buttons": [{
                            "type": "postback",
                            "title": "Tell Me More!",
                            "payload": "TELL_ME_MORE %s" % events[1][1]
                        }, {
                            "type": "postback",
                            "title": "Bookmark Event",
                            "payload": "BOOKMARK_EVENT %s" % events[1][1]
                        }],
                    }, {
                        "title": events[2][0],
                        "subtitle": events[2][4],
                        "item_url": events[2][3],
                        "image_url": events[2][2],
                        "buttons": [{
                            "type": "postback",
                            "title": "Tell Me More!",
                            "payload": "TELL_ME_MORE %s" % events[2][1]
                        }, {
                            "type": "postback",
                            "title": "Bookmark Event",
                            "payload": "BOOKMARK_EVENT %s" % events[2][1]
                        }],
                    }, {
                        "title": events[3][0],
                        "subtitle": events[3][4],
                        "item_url": events[3][3],
                        "image_url": events[3][2],
                        "buttons": [{
                            "type": "postback",
                            "title": "Tell Me More!",
                            "payload": "TELL_ME_MORE %s" % events[3][1]
                        }, {
                            "type": "postback",
                            "title": "Bookmark Event",
                            "payload": "BOOKMARK_EVENT %s" % events[3][1]
                        }],
                    }, {
                        "title": events[4][0],
                        "subtitle": events[4][4],
                        "item_url": events[4][3],
                        "image_url": events[4][2],
                        "buttons": [{
                            "type": "postback",
                            "title": "Tell Me More!",
                            "payload": "TELL_ME_MORE %s" % events[4][1]
                        }, {
                            "type": "postback",
                            "title": "Bookmark Event",
                            "payload": "BOOKMARK_EVENT %s" % events[4][1]
                        }],
                    }, {
                        "title": events[4][0],
                        "subtitle": events[4][4],
                        "item_url": events[4][3],
                        "image_url": events[4][2],
                        "buttons": [{
                            "type": "postback",
                            "title": "Tell Me More!",
                            "payload": "TELL_ME_MORE %s" % events[4][1]
                        }, {
                            "type": "postback",
                            "title": "Bookmark Event",
                            "payload": "BOOKMARK_EVENT %s" % events[4][1]
                        }],
                    }]
                }
            }
        }
    })

    print messageData

    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params={"access_token": PAT},
                      data=messageData,
                      headers={'Content-type': 'application/json'})

    if r.status_code != requests.codes.ok:
        print r.text

def add_id_to_firebase(id):
  print "Adding ID to firebase"
  result = firebase.put('/users', name=id, data='')
  print result

if __name__ == '__main__':
  app.run()