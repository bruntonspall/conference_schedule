import icalendar
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from google.appengine.ext import db

class Event(db.Model):
    id = db.StringProperty()
    start_time = db.DateTimeProperty()
    duration = db.IntegerProperty() #In Minutes
    location = db.StringProperty()
    speaker = db.StringProperty()
    title = db.StringProperty()
    

def fetch_ics_file():
    response = urlfetch.fetch('http://www.europython.com/talks/timetable/timetable.ics')
    return response.content
    
def get_local_ics_file():
    return ''.join(file('timetable.ics').readlines())
    
def get_events_list(icsfile):
    return icalendar.Calendar.from_string(icsfile).walk('vevent')
    
def get_speaker_and_title(event):
    t = event.split(':')
    if len(t) > 1:
        return t
    else
        return None, t[0]
    
def persist_events(events):
    for event in events:
        speaker, title = get_speaker_and_title(event)
        e = Event()
        

class FetchIcs(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		content = get_events_list(get_local_ics_file())
		self.response.out.write([c for c in content])

application = webapp.WSGIApplication([('/services/fetch_ics', FetchIcs)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()