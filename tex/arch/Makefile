all:
	latex arch
	bibtex arch
	latex arch
	pdflatex arch

publish: all
	mv arch.pdf ../../arch.pdf

view: all
	xdg-open arch.pdf

clean:
	rm -f arch.aux
	rm -f arch.bbl
	rm -f arch.blg
	rm -f arch.dvi
	rm -f arch.log
	rm -f arch.pdf    
