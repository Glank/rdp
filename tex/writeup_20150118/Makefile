all:
	latex writeup_20150118
	-bibtex writeup_20150118
	latex writeup_20150118
	pdflatex writeup_20150118

publish: all
	mv writeup_20150118.pdf ../../writeup_20150118.pdf

view: all
	xdg-open writeup_20150118.pdf

clean:
	rm -f writeup_20150118.aux
	rm -f writeup_20150118.bbl
	rm -f writeup_20150118.blg
	rm -f writeup_20150118.dvi
	rm -f writeup_20150118.log
	rm -f writeup_20150118.pdf    
