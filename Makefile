test:
	find ./umatobi/test -name '*.py' -exec python3 {} \;
	python3 ./umatobi/tools/cat.py watson.log
	python3 ./umatobi/tools/select.py simulation.db simulation
	python3 ./umatobi/tools/select.py client.1.db growings
	python3 ./umatobi/tools/make_simulation_db.py
