# sigma.deploy
Aplicação padrão da SIGMA para deploy via fabric

para testar localmente,

escolha uma das versões do vagrant file e renomei-o para Vagrantfile

vagrant up
vagrant ssh-config

copie o resultado do comando em: ~/.ssh/config

então execute os comando abaixo com o usuário vagrant e senha vagrant

e inclua a porta: 
``` shell
  fab -H 127.0.0.1 --port=2222 -u vagrant -p vagrant 
```

## install_all sem clonar repo

On your root project folder:

``` shell
  fab -H <host> -u <user> -p <password> install_all --set virtualenv_name=<name>,virtualenv_path=<root_folder_of_virtualenv>,virtualenvs_path=<folder_of_virtualenv>,clone=False

```


exemplo: 

``` shell
  fab -H 127.0.0.1 --port=2222 -u vagrant -p vagrant install_all --set virtualenv_name=ares,virtualenv_path=/opt/apps/.virtualenv/ares,virtualenvs_path=/opt/apps/.virtualenv,clone=true,app_root=/opt/apps/ares,git_url=<git_https_url>
```

