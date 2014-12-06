rdp
===

A versatile parser writen in python.

See `notes.pdf` and `parse.pdf` for more info.

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

Actor Identification
---
The example script 'actor_ident.py' should run without needing to install any extra software.
It figures out the RDF URI of an actor that corresponds to a given (possibly mangled) name.
It uses a cached SPARQL query result file and some simple user feedback; it runs in O(n) time.

    Identifying 'David Blane'...
    (u'David Blaine', u'http://data.linkedmdb.org/resource/actor/29856')

    Identifying 'Swartzeneger'...
    By 'Swartzeneger' did you mean:
    1)  Arnold Schwarzenegger
    2)  RenÃ©e Zellweger
    3)  John Ratzenberger
    4)  Pete Seeger
    5)  None of the above.
    1
    (u'Arnold Schwarzenegger', u'http://data.linkedmdb.org/resource/actor/29369')

    Identifying 'Jacky Chan'...
    (u'Jackie Chan', u'http://data.linkedmdb.org/resource/actor/30334')

    Identifying 'Notaname'...
    By 'Notaname' did you mean:
    1)  Nona Gaye
    2)  Noah Wyle
    3)  Stan Lee
    4)  Jim Rome
    5)  Ted Demme
    6)  None of the above.
    6
    None
