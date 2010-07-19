import icalendar
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.ext.webapp import template
import os, time, logging
import itertools
try:
    import json
except ImportError:
    from django.utils import simplejson as json

def render_template(self, end_point, template_values):
    path = os.path.join(os.path.dirname(__file__), "templates/" + end_point)
    self.response.out.write(template.render(path, template_values))

class Event(db.Model):
    id = db.StringProperty()
    start_time = db.DateTimeProperty()
    duration = db.IntegerProperty() #In Minutes
    location = db.StringProperty()
    speaker = db.StringProperty()
    title = db.StringProperty()
    
    def to_dict(self):
        return {
        'id':self.id,
        'start_time':long(time.mktime(self.start_time.timetuple())*1000),
        'duration':self.duration,
        'location':self.location,
        'speaker':self.speaker,
        'title':self.title,
        }
    

def fetch_ics_file():
    response = urlfetch.fetch('http://www.europython.eu/talks/timetable/timetable.ics')
    # logging.info(response.headers)
    # logging.info(response.content)
    return response.content
    
def get_local_ics_file():
    return ''.join(file('timetable.ics').readlines())
    
def get_events_list(icsfile):
    return icalendar.Calendar.from_string(icsfile).walk('vevent')
    
def get_speaker_and_title(event):
    t = event['summary'].split(':')
    if len(t) > 1:
        return t[0],":".join(t[1:])
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
    for event in events:
        speaker, title = get_speaker_and_title(event)
        e = Event()
        e.id = get_id(event)
        e.speaker, e.title = get_speaker_and_title(event)
        e.duration = get_duration(event)
        e.location = str(get_location(event))
        e.start_time = get_start_time(event)
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
        # for c in content:         
        #     self.response.out.write(get_start_time(c))
        #     self.response.out.write("\t")
        #     self.response.out.write(get_id(c))
        #     self.response.out.write("\t")
        #     self.response.out.write(get_location(c))
        #     self.response.out.write("\t")
        #     self.response.out.write(get_duration(c))
        #     self.response.out.write("\t")
        #     self.response.out.write(get_speaker_and_title(c))
        #     self.response.out.write("\n")
        
class AllEvents(webapp.RequestHandler):
    def get(self):
        all_events = Event.all().order('start_time')
        events = []
        event_days = set()
        for e in all_events:
            events.append(e.to_dict())
            event_days.add(str(e.start_time.date()))
        render_template(self, 'front.html', {'events':events, 'event_days':sorted(event_days)})

class AllEventsJson(webapp.RequestHandler):
    def get(self):
        prefix = ""
        postfix = ""
        if self.request.get('callback'):
            prefix = "%s(" % self.request.get('callback')
            postfix = ");"
        all_events = Event.all().order('start_time')
        events = [e.to_dict() for e in all_events]
        self.response.out.write(prefix+json.dumps(events)+postfix)

application = webapp.WSGIApplication([
            ('/services/fetch_ics', FetchIcs),
            ('/services/fetch_local', FetchLocalIcs),
            ('/', AllEvents),
            ('/json', AllEventsJson),
                                        ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()