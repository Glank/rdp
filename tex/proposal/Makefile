all:
	latex proposal
	-bibtex proposal
	latex proposal
	pdflatex proposal

publish: all
	mv proposal.pdf ../../proposal.pdf

view: all
	xdg-open proposal.pdf

clean:
	rm -f proposal.aux
	rm -f proposal.bbl
	rm -f proposal.blg
	rm -f proposal.dvi
	rm -f proposal.log
	rm -f proposal.pdf    
