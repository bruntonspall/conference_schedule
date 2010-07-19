function Searcher(sessions)
{

  var stopwords = "and or not the is a this but".split(" ");

  this.filter = function(keywords)
  {
    var result = [];

    if (keywords.length < 3) { return []; }

    keywords = prepareKeywords(keywords);

    for (i in sessions) {
      var session = sessions[i];
      if (sessionMatches(session, keywords)) {
        result.push(session);
      }
    }

    return result;
  }

  this.prepareKeywords = prepareKeywords;


  function sessionMatches(session, keywords)
  {
    return titleMatches(session, keywords) || speakerMatches(session, keywords);
  }


  function titleMatches(session, keywords)
  {
    var found = 0;
    var title = session.title.toLowerCase();
    for (i in keywords) {
      if (title.indexOf(keywords[i]) >= 0) {
        found++;
      }
    }
    return found == keywords.length;
  }

  function speakerMatches(session, keywords)
  {
    var found = 0;
    var speaker = session.speaker.toLowerCase();
    for (i in keywords) {
      if (speaker.indexOf(keywords[i]) >= 0) { found ++; }
    }
    return found == keywords.length;
  }


  function prepareKeywords(keywords)
  {
    var stripThese = /[^A-z0-9\s]/g;
    var words = [];
    words = keywords.toLowerCase().
      replace(stripThese, '').
      replace(/\s+/g, ' ').
      split(" ");
    words = removeStopwords(words);
    return words;
  }


  function removeStopwords(words)
  {
    var result = [];
    for (i in words) {
      var word = words[i];
      if (!isStopword(word)) result.push(word);
    }
    return result;
  }


  function isStopword(word)
  {
    for (i in stopwords) {
      if (stopwords[i] == word) return true;
    }
    return false;
  }

}

