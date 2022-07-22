.PHONY: default format mypy build push


IMAGE_NAME := clpy9793/oauth-playground

default: format build push

format: refactor pre-commit

refactor:
	@yapf -r -i . 
	@isort . 
	@pycln -a .

pre-commit:
	@pre-commit run --all-file

mypy:
	@mypy .

build:
	docker build --platform linux/amd64 -t $(IMAGE_NAME) .

push:
	docker push $(IMAGE_NAME)
	curl https://api.day.app/W8sgxw7Nti7js3y6LF2SLY/oauth-playground%20push%20success