# K8sNamespaceRestrictedAccess
This is a script for generating service account limited within the given namespace.

# Dependencies
This requires the following to work. 

* Gcloud
* Kubectl
* A working K8s cluster
* ruamel.yaml API

## Install ruamel.yaml
[Link](https://yaml.readthedocs.io/en/latest/install.html) to doc.

* pip install -U pip setuptools wheel
* pip install ruamel.yaml

# How to run

In Bash terminal 

* python ConstructAccess.py create namespace1 namespace2 namespace3 .. namespaceN

This will create N config files to be used.


# How to merge config files

Let say that you want someone to access multiple different namespaces on the same or different cluster. This script also has that function where you can merge multiple files.

Note: Here I assume that you only want to generate the merged config file with the provided config files and not the one you are using right now. Otherwise you can just take the merged one and replace it with your current in $HOME/.kube/config (The default path of K8s config file) if you want to use the merged file.

* python ConstructAccess.py 



