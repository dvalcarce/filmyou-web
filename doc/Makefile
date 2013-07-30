MANAGE=../src/manage.py
OUTPUT=diagram

uml-png:
	python $(MANAGE) graph_models -a -e -g -o $(OUTPUT).png

uml-dot:
	python $(MANAGE) graph_models -a -e -g -o $(OUTPUT).dot

