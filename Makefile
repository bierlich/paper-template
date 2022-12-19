.PHONY : all paper.aux test-bib clean 

# Compile the paper.
all :
	pdflatex main.tex

# Compile paper and bibliography.
bib : bibliography.bib
	pdflatex main.tex
	bibtex main
	pdflatex main.tex
	pdflatex main.tex

# CI test for fetching bibliography
test-bib : 
	if [ -a bibliography.bib ] ; \
	then \
		cp bibliography.bib old-bibliography.bib ; \
	fi;
	pdflatex main.tex
	python3 citations.py --noempty
	bibtex main
	pdflatex main.tex
	pdflatex main.tex
	

# Fetch bibliography from inspire.
bibliography.bib : main.aux
	if [ -a bibliography.bib ] ; \
	then \
		cp bibliography.bib old-bibliography.bib ; \
	fi;
	python3 citations.py --auxfile=main.aux

main.aux : all

clean :
	rm -f *.idx *.ilg *.ind *.aux *.toc *.log *.bbl *.blg *.out main.pdf 
