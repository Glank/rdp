rdp
===

A versatile parser writen in python.

See `notes.pdf` for more info.

Setup
---

For a few examples, you might need to install the following packages:

    nltk (for synsets)
    numpy (a little bit of stats)
    cluster (for clustering)
    pybloom (for bloom filters)
    coverage (for testing)

After installing `nltk` you'll also need to download the 'wordnet' corpus.
Just run the command:

    python -c "import nltk; nltk.download()"

And enter 'wordnet', then 'q' to quit.

Buffalo Example
---

One thorough example of this parser's capabilities is the 'buffalo.py' script.
In it, the classic confusing gramatical sentence
"BUFFALO BUFFALO BUFFALO BUFFALO BUFFALO BUFFALO BUFFALO BUFFALO"
is parsed into it's two possible interpretations.
(Yes, that's a [valid english sentence](http://en.wikipedia.org/wiki/Buffalo_buffalo_Buffalo_buffalo_buffalo_buffalo_Buffalo_buffalo).)
Here's the important part of the output:

    S
      NP
        PN
          'BUFFALO':['BUFFALO']
        N
          'BUFFALO':['BUFFALO']
      VP
        V
          'BUFFALO':['BUFFALO']
        NP
          NP
            PN
              'BUFFALO':['BUFFALO']
            N
              'BUFFALO':['BUFFALO']
          RC
            NP
              PN
                'BUFFALO':['BUFFALO']
              N
                'BUFFALO':['BUFFALO']
            V
              'BUFFALO':['BUFFALO']
    **********************************************************************
    S
      NP
        NP
          PN
            'BUFFALO':['BUFFALO']
          N
            'BUFFALO':['BUFFALO']
        RC
          NP
            PN
              'BUFFALO':['BUFFALO']
            N
              'BUFFALO':['BUFFALO']
          V
            'BUFFALO':['BUFFALO']
      VP
        V
          'BUFFALO':['BUFFALO']
        NP
          PN
            'BUFFALO':['BUFFALO']
          N
            'BUFFALO':['BUFFALO']

Actors Example
---

Another simple example is the 'actors_example.py' script.
It request's input from the user, who is supposed to enter questions
about the presence of an actor or actors in some movie.
Here's a sample of it's input/output:

    Is will smith or tom jones in Independence Day?
    **********************************************************************
    S
      'IS':['IS']
      actor_or
        'actor':['WILL', 'SMITH']
        actor_or
          'OR':['OR']
          'actor':['TOM', 'JONES']
      'IN':['IN']
      'film':['INDEPENDENCE', 'DAY']
    **********************************************************************
    Are tom hanks, will smith, and arnold schwarzenegger in the longest yard?
    **********************************************************************
    S
      'ARE':['ARE']
      actor_and
        'actor':['TOM', 'HANKS']
        actor_and
          'actor':['WILL', 'SMITH']
          actor_and
            'AND':['AND']
            'actor':['ARNOLD', 'SCHWARZENEGGER']
      'IN':['IN']
      'film':['THE', 'LONGEST', 'YARD']
    **********************************************************************

This works by using sample data from the [Linked Movie Database](http://linkedmdb.org/).
From query result on that database, I was able to extract all of it's know
actor names and movie names. Those names were then compiled into statistical
models which can then determine if arbitrary strings are possibly members
of those sets. From there, the models are entered as terminal symbles in
a grammar which is compiled and used by the parser. It does an 'ok' job
at the moment - it still needs some tweeks.
