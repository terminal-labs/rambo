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

vagrant-pyenv: download_python_environment_manager
	@sudo bash .tmp/python-environment-manager-master/makefile_resources/scripts_python/pyenv/build.sh $(APPNAME) $(SUDO_USER) vagrant

vagrant-conda: download_python_environment_manager
	@sudo bash .tmp/python-environment-manager-master/makefile_resources/scripts_python/conda/build.sh $(APPNAME) $(SUDO_USER) vagrant

mac-pyenv: download_python_environment_manager
	@sudo bash .tmp/python-environment-manager-master/makefile_resources/scripts_python/pyenv/build.sh $(APPNAME) $(SUDO_USER) mac
	@sudo bash .tmp/python-environment-manager-master/makefile_resources/scripts_python/pyenv/emit_activation_script.sh $(APPNAME) $(SUDO_USER) mac

mac-conda: download_python_environment_manager
	@sudo bash .tmp/python-environment-manager-master/makefile_resources/scripts_python/conda/build.sh $(APPNAME) $(SUDO_USER) mac
	@sudo bash .tmp/python-environment-manager-master/makefile_resources/scripts_python/conda/emit_activation_script.sh $(APPNAME) $(SUDO_USER) mac

linux-pyenv: download_python_environment_manager
	@sudo bash .tmp/python-environment-manager-master/makefile_resources/scripts_python/pyenv/build.sh $(APPNAME) $(SUDO_USER) linux
	@sudo bash .tmp/python-environment-manager-master/makefile_resources/scripts_python/pyenv/emit_activation_script.sh $(APPNAME) $(SUDO_USER) linux

linux-conda: download_python_environment_manager
	@sudo bash .tmp/python-environment-manager-master/makefile_resources/scripts_python/conda/build.sh $(APPNAME) $(SUDO_USER) linux
	@sudo bash .tmp/python-environment-manager-master/makefile_resources/scripts_python/conda/emit_activation_script.sh $(APPNAME) $(SUDO_USER) linux

mac-docs: mac-conda
	@sudo bash .tmp/python-environment-manager-master/makefile_resources/scripts_python/conda/docs.sh $(APPNAME) $(SUDO_USER) mac

linux-docs: linux-conda
	@sudo bash .tmp/python-environment-manager-master/makefile_resources/scripts_python/conda/docs.sh $(APPNAME) $(SUDO_USER) linux
