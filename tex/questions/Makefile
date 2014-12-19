all:
	latex questions
	-bibtex questions
	latex questions
	pdflatex questions

publish: all
	mv questions.pdf ../../questions.pdf

view: all
	xdg-open questions.pdf

clean:
	rm -f questions.aux
	rm -f questions.bbl
	rm -f questions.blg
	rm -f questions.dvi
	rm -f questions.log
	rm -f questions.pdf    
