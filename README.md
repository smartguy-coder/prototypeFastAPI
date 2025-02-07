# prototypeFastAPI

Перелік тасок
<details>
  <summary>Зміст</summary>

- [1-add-makefile-for-automation](#1-add-makefile-for-automation-and-env-setup)
- [2-setting-packages](#2-setting-packages)
- [3-install-linters-and-checkers](#3-install-linters-and-checkers)

</details>

## 1-add-makefile-for-automation-and-env-setup

make is a GNU command so the only way you can get it on Windows is installing a Windows version like the one provided by GNUWin32.
Anyway, there are several options for getting that:

- Directly download from [Make for Windows](https://gnuwin32.sourceforge.net/packages/make.htm)

- Using [Chocolatey](https://chocolatey.org/install). First you need to install this package manager.
Once installed you simply need to install make (you may need to run it in an elevated/admin command prompt) :
```commandline
choco install make
```

Other recommended option is installing a Windows Subsystem for Linux (WSL/WSL2), so you'll have a Linux distribution of your choice embedded in Windows 10 where you'll be able to install make, gccand all the tools you need to build C programs.

[https://makefiletutorial.com/](https://makefiletutorial.com/)
[https://python-poetry.org/docs/basic-usage/](https://python-poetry.org/docs/basic-usage/)

[UP](#prototypeFastAPI)


# 2-setting-packages
and minimal testing

```commandline
(master-backend-api-py3.12) PS C:...\master_backend_api> make install package=fastapi[all]

```

[UP](#prototypeFastAPI)


# 3-install-linters-and-checkers
```commandline
 make install package=flake8
 make install package=black
 make install package=isort
 make checks
```
[UP](#prototypeFastAPI)

# 4-dockerization
run from prototypeFastAPI
```commandline
docker build -t my-fastapi-app .
docker run -p 9000:9000 my-fastapi-app
```
-t my-fastapi-app — задає ім'я образу.

. — вказує поточну директорію як контекст збірки.

Пояснення:
Контекст збірки Docker: Коли ви запускаєте docker build, Docker використовує поточну директорію (або вказану директорію) як контекст збірки. Усі файли, які ви копіюєте за допомогою COPY, повинні знаходитися в цьому контексті.

Шляхи у COPY: Шляхи у команді COPY відносяться до контексту збірки.


[UP](#prototypeFastAPI)


# alembic
```commandline
docker compose run --rm master-backend-api bash
appuser@7a246ab7c518:/app$ alembic init migrations
```