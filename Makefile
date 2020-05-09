APPNAME=rambo
PYTHONVERSION = 3.6.9

help:
	@echo "usage: make [command]"

download_python_environment_manager:
	@if test ! -d ".tmp/python-environment-manager-master";then \
		sudo su -m $(SUDO_USER) -c "mkdir -p .tmp"; \
		sudo su -m $(SUDO_USER) -c "cd .tmp; wget https://github.com/terminal-labs/python-environment-manager/archive/master.zip"; \
		sudo su -m $(SUDO_USER) -c "cd .tmp; unzip master.zip"; \
	fi

vagrant: download_python_environment_manager
	@sudo bash .tmp/python-environment-manager-master/makefile_resources/scripts_python/conda/build.sh $(APPNAME) $(SUDO_USER) vagrant

mac: download_python_environment_manager
	@sudo bash .tmp/python-environment-manager-master/makefile_resources/scripts_python/conda/build.sh $(APPNAME) $(SUDO_USER) mac
	@sudo bash .tmp/python-environment-manager-master/makefile_resources/scripts_python/conda/emit_activation_script.sh $(APPNAME) $(SUDO_USER) mac

linux: download_python_environment_manager
	@sudo bash .tmp/python-environment-manager-master/makefile_resources/scripts_python/conda/build.sh $(APPNAME) $(SUDO_USER) linux
	@sudo bash .tmp/python-environment-manager-master/makefile_resources/scripts_python/conda/emit_activation_script.sh $(APPNAME) $(SUDO_USER) linux
