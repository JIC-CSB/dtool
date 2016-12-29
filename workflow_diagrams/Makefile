all: arctool_workflow.png arctool_workflow.pdf

arctool_workflow.png: arctool.gv
	dot -Tpng arctool.gv -o arctool_workflow.png	

arctool_workflow.pdf: arctool.gv
	dot -Tpdf arctool.gv -o arctool_workflow.pdf	

clean:
	rm arctool_workflow.*
