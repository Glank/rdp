all:
	latex notes
	bibtex notes
	latex notes
	pdflatex notes

publish: all
	mv notes.pdf ../notes.pdf

view: all
	xdg-open notes.pdf

clean:
	rm notes.aux
	rm notes.bbl
	rm notes.blg
	rm notes.dvi
	rm notes.log
	rm notes.pdf    
