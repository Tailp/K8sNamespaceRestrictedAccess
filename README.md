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

* python ConstructAccess.py

Provide the desired name of the namespace.
