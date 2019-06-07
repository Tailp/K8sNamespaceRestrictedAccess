# Introduction
This is a script with several functions for easily managing Kubernetes config files such as: 

* Generating config files for multiple user within different namespace, 
* Generating config files for several users within the "Same" already existed namespace 
* Deleting users if not needed anymore(Namespace itself need to be deleted manually since I don't want my script to accidentally deleting your entire namespace, so only the user will be removed)
* Merging config files for the same user to access to several different namespace in the same or different clusters.

# Important to know before reading more

How to set config files ?

In bash terminal (Note that you have to cd into the same folder as the config file)
* export KUBECONFIG="<configfile>"

How to switch namespace or cluster, also know as switching context ?

In bash terminal 
* kubectl config get-contexts 

This will give you all available contexts for your config file to switch to. Note that only "those" contexts in your config file so if you want to access a cluster or a namespace not in your config file you have to acquire the config file containing that context(ask the guy who can give you the config file).

* kubectl config set-context <context name> 

Context name can be gotten from the previous command, check name column


# Dependencies
This requires the following to work. 

* Gcloud
* Kubectl
* A working K8s cluster
* ruamel.yaml API

## Install ruamel.yaml
[Link](https://yaml.readthedocs.io/en/latest/install.html) to doc. This tool is used for easily editing yaml file since almost everying things in K8s system can be output as a yaml file.

* pip install -U pip setuptools wheel
* pip install ruamel.yaml



# User manual

In Bash terminal 

## Creating multiple namespace with full access within the namespace

* python ConstructAccess.py create namespace1 namespace2 namespace3 .. namespaceN

This will create N config files for N different namespaces to be used.

## Merge config files

Let say that you want someone to access multiple different namespaces on the same or different cluster. This script also has that function where you can merge multiple files.

Note: Here I assume that you only want to generate the merged config file with the provided config files and not the one you are using right now. Otherwise you can just take the merged one and replace it with your current in $HOME/.kube/config (The default path of K8s config file) if you want to use the merged file.

Place all the config files you want to merge in this repo, also known as "K8sNamespaceRestrictedAccess" folder after cloning, then run

* python ConstructAccess.py merge <config file 1> <config file 2> .... <config file N>

It will generate a file called "mergedconfig" to use. Now the user 







