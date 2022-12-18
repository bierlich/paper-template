.PHONY : all paper.aux test-bib clean 

# Compile the paper.
all :
	pdflatex paper.tex

# Compile paper and bibliography.
bib : bibliography.bib
	pdflatex paper.tex
	bibtex paper
	pdflatex paper.tex
	pdflatex paper.tex

# CI test for fetching bibliography
test-bib : 
	if [ -a bibliography.bib ] ; \
	then \
		cp bibliography.bib old-bibliography.bib ; \
	fi;
	pdflatex paper.tex
	python3 citations.py --noempty
	bibtex paper
	pdflatex paper.tex
	pdflatex paper.tex
	

# Fetch bibliography from inspire.
bibliography.bib : paper.aux
	if [ -a bibliography.bib ] ; \
	then \
		cp bibliography.bib old-bibliography.bib ; \
	fi;
	python3 citations.py

paper.aux : all

clean :
	rm -f *.idx *.ilg *.ind *.aux *.toc *.log *.bbl *.blg *.out paper.pdf 
