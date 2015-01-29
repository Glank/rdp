all:
	latex name_matching
	-bibtex name_matching
	latex name_matching
	pdflatex name_matching

publish: all
	mv name_matching.pdf ../../name_matching.pdf

view: all
	xdg-open name_matching.pdf

clean:
	rm -f name_matching.aux
	rm -f name_matching.bbl
	rm -f name_matching.blg
	rm -f name_matching.dvi
	rm -f name_matching.log
	rm -f name_matching.pdf    
