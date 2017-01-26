
MAN = ubench.1 ubench-fetch.1 ubench-list.1 ubench-log.1 ubench-result.1  ubench-listparams.1 ubench-report.1 ubench-run.1
MAINDOC = user_guide.html developer_guide.html

all: $(MAN) ${MAINDOC}
clean:
	rm -f man/*.1 *.pdf *.html

%.1: source/%.md
	pandoc -f markdown -s -t man $< -o man/$@

%.html: source/%.asc
	asciidoctor -a stylesheet=source/user_guide.css $< -o $@

