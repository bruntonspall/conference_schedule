import datetime, time
from collections import defaultdict
events = []
# event = {
# 'uri':'uri'
# "title",
# "abstract"
# "start": 123678,
# "room",
# "difficulty":
# "speaker_name":
# "technology":
# "track":
# }

def scrape_timetable():
    return file('/Users/mbs/Downloads/timetable.ics').readlines()

def convert_ics_to_json():
	event = {}
	ignore = False
	for line in scrape_timetable():
		line = line.strip()
		if line.startswith('END:VTIMEZONE'):
			ignore = False
		if line.startswith('BEGIN:VTIMEZONE'):
			ignore = True
		if ignore:
			continue
		if line.startswith('BEGIN:VEVENT'):
			event = defaultdict(unicode)
		if line.startswith('LOCATION'):
			event['room'] = line.split(':')[1]
		if line.startswith('UID'):
			event['id'] = "session_"+line.split(':')[1].split('@')[0]
		if line.startswith('SUMMARY'):
			details = line.split(':')
			if len(details) > 2:
				event['title'] = details[2]
				event['speaker'] = details[1]
			else:
				event['title'] = details[1]
		if line.startswith('DTSTART'):
			stim = line.split(':')[1]
			tim = datetime.datetime.strptime(stim, "%Y%m%dT%H%M%S")
			event['start'] = time.mktime(tim.timetuple()) * 1000		
		if line.startswith('END:VEVENT'):
			events.append(event)
	return events

def main():
    print "(function() {var s= [];"
    for event in convert_ics_to_json():
        print 's.push(new Session({id:"%(id)s", title:"%(title)s", speaker:"%(speaker)s", start:new Date(%(start)d), room:"%(room)s", difficulty:"N/A", technology:"Awesome", track:"Ruby", abstract:"N/A"}));' % event
    print "window.sessions = s; })();"
if __name__ == "__main__":
    main()
