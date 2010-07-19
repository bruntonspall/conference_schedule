from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from BeautifulSoup import BeautifulSoup
from google.appengine.ext import webapp
from google.appengine.ext import db
from model import Event
import icalendar

talk_abstracts_url = 'http://www.europython.eu/talks/talk_abstracts/index.html'

def fetch_ics_file():
    response = urlfetch.fetch('http://www.europython.eu/talks/timetable/timetable.ics')
    return response.content
    
def get_local_ics_file():
    return ''.join(file('timetable.ics').readlines())
    
def get_events_list(icsfile):
    return icalendar.Calendar.from_string(icsfile).walk('vevent')
    
def get_speaker_and_title(event):
    t = event['summary'].split(':')
    if len(t) > 1:
        return t[0].strip(), ":".join(t[1:]).strip()
    else:
        return None, t[0]

def get_duration(event):
    try: 
        return event['duration'].dt.seconds / 60
    except KeyError:
        return 0

def get_location(event):
    try: 
        return event['location']
    except KeyError:
        return "Unknown"
    
def get_id(event):
    return event['uid'].split('@')[0]
    
def get_start_time(event):
    return event['dtstart'].dt
    
def persist_events(events):
    db.delete(Event.all())
    talk_abstracts_soup = BeautifulSoup(urlfetch.fetch(talk_abstracts_url).content)
    for event in events:
        speaker, title = get_speaker_and_title(event)
        e = Event()
        e.id = get_id(event)
        e.speaker, e.title = get_speaker_and_title(event)
        e.duration = get_duration(event)
        e.location = str(get_location(event))
        e.start_time = get_start_time(event)
        e.day = e.start_time.date()
        e.abstract = ''
        element = talk_abstracts_soup.find(text=title)
        if element:
            element = element.parent.parent.nextSibling
            while not unicode(element).startswith('<hr'):
                e.abstract += unicode(element)
                element = element.nextSibling
        e.put()

class FetchLocalIcs(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		content = get_events_list(get_local_ics_file())
		persist_events(content)

class FetchIcs(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		content = get_events_list(fetch_ics_file())
		persist_events(content)

application = webapp.WSGIApplication([
            ('/services/fetch_ics', FetchIcs),
            ('/services/fetch_local', FetchLocalIcs),
                                        ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()