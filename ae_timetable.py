import icalendar
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.ext.webapp import template
import os

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
    

def fetch_ics_file():
    response = urlfetch.fetch('http://www.europython.com/talks/timetable/timetable.ics')
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

class FetchIcs(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		content = get_events_list(get_local_ics_file())
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
        render_template(self, 'front.html', {'events':Event.all().order('start_time')})

application = webapp.WSGIApplication([
            ('/services/fetch_ics', FetchIcs),
            ('/', AllEvents),
                                        ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()