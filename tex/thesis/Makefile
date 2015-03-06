all:
	latex thesis
	bibtex thesis
	latex thesis
	pdflatex thesis

publish: all
	mv thesis.pdf ../../thesis.pdf

view: all
	xdg-open thesis.pdf

check:
	aspell -c thesis.tex

clean:
	rm -f thesis.aux
	rm -f thesis.bbl
	rm -f thesis.blg
	rm -f thesis.dvi
	rm -f thesis.log
	rm -f thesis.toc
	rm -f thesis.tex.bak

clean_all: clean
	rm -f thesis.pdf
