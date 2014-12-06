all:
	latex parse
	-bibtex parse
	latex parse
	pdflatex parse

publish: all
	mv parse.pdf ../../parse.pdf

view: all
	xdg-open parse.pdf

clean:
	rm -f parse.aux
	rm -f parse.bbl
	rm -f parse.blg
	rm -f parse.dvi
	rm -f parse.log
	rm -f parse.pdf    
