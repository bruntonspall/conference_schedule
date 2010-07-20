from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.ext import webapp
import os, time, datetime, logging
import itertools
import collections

try:
    import json
except ImportError:
    from django.utils import simplejson as json
    
from model import Event


def render_template(self, end_point, template_values):
    path = os.path.join(os.path.dirname(__file__), "templates/" + end_point)
    self.response.out.write(template.render(path, template_values))
        
class AllEvents(webapp.RequestHandler):
    def get(self):
        all_events = Event.all().order('start_time')
        events = []
        event_days = set()
        for e in all_events:
            events.append(e.to_dict())
            event_days.add(e.start_time.date())
        render_template(self, 'front.html', {'events':events, 'event_days':sorted(event_days)})

class EventsOnDay(webapp.RequestHandler):
    def get(self, target_date):
        all_events = Event.all().filter('day =',datetime.date.fromordinal(int(target_date))).order('start_time')
        events = []
        event_slots = set()
        for e in all_events:
            events.append(e.to_dict())
            event_slots.add(e.start_time)
        render_template(self, 'day.html', {'event_slots':sorted(event_slots)})

class EventsAtTime(webapp.RequestHandler):
    def get(self, target_time):
        all_events = Event.all().filter('start_time =',datetime.datetime.fromtimestamp(int(target_time))).order('start_time')
        events = []
        event_days = set()
        for e in all_events:
            events.append(e.to_dict())
        render_template(self, 'time.html', {'events':events})

class AllEventsJson(webapp.RequestHandler):
    def get(self):
        data = memcache.get('json')
        if data is None:            
            prefix = ""
            postfix = ""
            if self.request.get('callback'):
                prefix = "%s(" % self.request.get('callback')
                postfix = ");"
            all_events = Event.all().order('start_time')
            events = [e.to_dict() for e in all_events]
            data = prefix+json.dumps(events)+postfix
            memcache.add('json', data, 300)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(data)

class NewJson(webapp.RequestHandler):
    def get(self):
        data = memcache.get('newjson')
        if data is None:            
            prefix = ""
            postfix = ""
            if self.request.get('callback'):
                prefix = "%s(" % self.request.get('callback')
                postfix = ");"
            all_events = Event.all().order('start_time')
            days = collections.defaultdict(list)
            slots = collections.defaultdict(list)
            events = []
            for e in all_events:
                days[e.day.toordinal()] = e.day.strftime("%A, %d %b")
                slots[int(time.mktime(e.start_time.timetuple())*1000)]={'day':e.day.toordinal(),'text':e.start_time.strftime('%H:%M')}
                events.append(e.to_dict())
            d = {
            'days':days,
            'slots':slots,
            'events': events,
            }
            data = prefix+json.dumps(d)+postfix
            memcache.add('newjson', data, 5)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(data)

class FrontPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        render_template(self, 'front.html', {})


class HomePage(webapp.RequestHandler):
    def get(self):
        self.redirect('/a/index.html')

class Manifest(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/cache-manifest'
        render_template(self, 'manifest.txt', {})
        
class Test(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        render_template(self, 'test.html', {})

application = webapp.WSGIApplication([
            ('/time/(\d+)', EventsAtTime),
            ('/(\d+)', EventsOnDay),
            ('/json', AllEventsJson),
            ('/newjson', NewJson),
            ('/manifest', Manifest),
            ('/test', Test),
            ('/b', FrontPage),
            ('/', HomePage),
                                        ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()