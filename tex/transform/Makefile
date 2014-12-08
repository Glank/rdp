all:
	latex transform
	-bibtex transform
	latex transform
	pdflatex transform

publish: all
	mv transform.pdf ../../transform.pdf

view: all
	xdg-open transform.pdf

clean:
	rm -f transform.aux
	rm -f transform.bbl
	rm -f transform.blg
	rm -f transform.dvi
	rm -f transform.log
	rm -f transform.pdf    
