# Introduction
This is a script with several functions for easily managing Kubernetes config files such as: 

* Generating config files for multiple user within different namespaces, 
* Generating config files for several users within already existed namespaces(so we won't need to create a new namespace) 
* Deleting users if not needed anymore(Namespace itself need to be deleted manually since I don't want my script to accidentally deleting your entire namespace, so only the user will be removed)
* Merging config files for the same user to access to several different namespace in the same or different clusters.

# Important to know before reading more

Q: How to set config files ?

A:In bash terminal (Note that you have to cd into the same folder as the config file)
The safest way is to replace directly your config file with the config file in $HOME/.kube/config with this new file(Do keep a copy of the old one first in this case)

There is also this other way with export KUBECONFIG="configfilename", but the variable rather being updated or expired too quickly so you will get an anonymous authentication error as if the configfilename has been unloaded.

Q: How to re-set the origin config files?

A:In bash terminal, Assumingly you have not move aroung you .kube folder or using a entirely different system than linux-based, the default path for your original config file should always be at $HOME/.kube/config
* export KUBECONFIG="$HOME/.kube/config"

Q: How to switch namespace or cluster, also know as switching context ?

A: In bash terminal 
* kubectl config get-contexts 

This will give you all available contexts for your config file to switch to. Note that only "those" contexts in your config file so if you want to access a cluster or a namespace not in your config file you have to acquire the config file containing that context(ask the guy who can give you the config file).

* kubectl config set-context contextname

contextname can be gotten from the previous command, check name column


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

IMPORTANT: When you use these command it will create the namespaces associated with the current cluster context. So if you have cluster1, cluster2, cluster3 and your namespace is on cluster1 then the functions will take the information from cluster1. So If you want to create a namespace on cluster2 you have to switch context to cluster2 first, then do these commands below.

Accesskind:
* "full-access" the user will be able to do anything excluding security stuffs like creating new namespaces, creating roles, service accounts. 
* "read-only" Like full access but here the user can only get,watch or list. 

Also here I assume that it's constrained RABAC, meaning that we cannot have a situation like one person have both read-only and full-access since there is no point. If the user want to elevate themselves then full-access is enough.

## Generating multiple config files for multiple namespaces with a particular accesskind within the namespaces

* python ConstructAccess.py create accesskind namespace1 namespace2 namespace3 .. namespaceN

This will create N config files for N different namespaces to be used. Also, the usernames created by this method is according to the format "namespaceN-user", so if your namespace is called tailp, then it will be "tailp-user" as username. 

## Generating multiple users configs for an already existed namespace

* python ConstructAccess.py createExisted EXISTED_NAMESPACE_NAME accesskind username1 username2 username3 .. usernameN

This will create N config files for N different users within the EXISTED_NAMESPACE_NAME with the specified accesskind. Note that each username should be unique and not the same as other already existed. 

You can check if your username is unique by looking up 
* kubectl get sa 

If any of your usernames match with one of these then you have to pick another one. Also you can check your EXISTED_NAMESPACE_NAME with

* kubectl get namespaces

This will list all the existed namespaces within your current cluster with your current-context privilege.

## Deleting user
So this will be deleting service accounts together with their role and rolebinding in that namespace created previously by the generating methods above.
* python ConstructAccess.py delete EXISTED_NAMESPACE_NAME accesskind username1 username2 ... usernameN

check for EXISTED_NAMESPACE_NAME with 

* kubectl get namespaces

## Merge config files

Let say that you want someone to access multiple different namespaces on the same or different clusters. This script also has that function where you can merge multiple files.

Note: Here I assume that you only want to generate the merged config file with the provided config files and not the one you are using right now. Otherwise you can just take the merged one and replace it with your current in $HOME/.kube/config (The default path of K8s config file) if you want to use the merged file.

Place all the config files you want to merge in this repo, also known as "K8sNamespaceRestrictedAccess" folder after cloning, then run

* python ConstructAccess.py merge configfile_1 configfile_2 .... configfile_N

It will generate a file called "mergedconfig" to use. Now the user can switching contexts and moving to different namespaces after setting the config file.

## Refetch config files

This is neccessary since the token for the service account will be expired after some time so, Kubernetes will automatically refresh this or maybe you lost the config file and want to re-aquire it. Therefore this also has a function which re-fetch the config file for you (with the updated token and other updated informations ofcourse).

* python ConstructAccess.py recreate NAMSPACE_NAME username

NAMESPACE_NAME can be found with 
* kubectl get namespaces

username depends on which method you use. If it's the "create" method then it will be "NAMESPACE_NAME-user" otherwise if it's the "createExisted" then in the right namespace the service account is in(you have to , it can be found with
* kubectl get sa














