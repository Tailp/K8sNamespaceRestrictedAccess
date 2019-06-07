
import subprocess
import sys # To do File input output operations
import os # for certain command for saving as file
from collections import OrderedDict ## For using Ordered dict
from ruamel.yaml import YAML #To create YAML File and Read YAML File

## Global variable
NAMESPACEINPUT = "";

## Global functions
# Execute command and get output as string
def ExecGetOutput(cmd,val=False):
	out = subprocess.Popen(cmd,
           stdout=subprocess.PIPE, 
           stderr=subprocess.STDOUT,shell=val)
	out.wait()
	stdout,stderr = out.communicate()
	return stdout

# Replace every string with name "stringtoreplace" in a file with input .
def ReplaceWithInput(filename,input,stringtoreplace):
	# Read in the file
	with open(filename, 'r') as file :
  		filedata = file.read()
	# Replace the target string
	filedata = filedata.replace(stringtoreplace, input)
	# Write the file out again
	with open(filename, 'w') as file:
	  file.write(filedata)

# Using ruamel library to edit the yaml file by element.
# Possible operations: update value, delete element, append element.
def EditYaml(filename,input,stringtoreplace):
	inp_fo = open(filename).read()  ## Read the Yaml File

	yaml = YAML() ## Load the yaml object

	code = yaml.load(inp_fo) #Load content of YAML file to yaml object
	#print(code['contexts'])
	#print(code)
	#code['notifications']['email']['recipients'] = [sys.argv[1]] #Update 
	## add new context example with ruamel.yaml.
	#code['contexts'].append({'context':{"cluster":"CLUSTER_NAME","namespace":"NAMESPACE_NAME","user":"NAMESPACE_USERNAME"},"name":"NAMESPACE_NAME"})
	#code['contexts']['context'].insert(0,"cluster","CLUSTER_NAME")
	#with file(filename, 'w') as f:
	#	yaml.dump(code, f) 

	#Yaml file with new parameter in object

	#inp_fo2 = open(filename,"w") #Open the file for Write

	#yaml.dump(code,inp_fo2) ##Write to file with new parameter

	#inp_fo2.close() ## close the file
	
# Merge yaml file together separating with ---, this is meant for constructing the access.yaml by merging
# sa.yaml, role.yaml and rolebinding.yaml
def Mergefiles(filenames,outfilename):
	with open(outfilename, 'w') as outfile:
		for fname in filenames:
			with open(fname) as infile:
				outfile.write("\n---\n")
				outfile.write(infile.read())
				outfile.write("\n")

# This will create a config file using the provided name of namespace and username of the service account.
def CreateConfig(NAMESPACENAME,NAMESPACE_USERNAME):
	# Get name of the secret format "mynamespace-user-token-xxxxx" of the created service account
	SECRETNAME = ExecGetOutput(["kubectl","get","sa",NAMESPACE_USERNAME,"-n",NAMESPACENAME,"-o","jsonpath='{.secrets[0].name}'"])
	#print(SECRETNAME)
	# Get service account token
	cmdTOKEN = "kubectl get secret " + SECRETNAME[1:len(SECRETNAME)-1] + " -n " + NAMESPACENAME +" -o 'jsonpath={.data.token}' | base64 -d"
	TOKEN = ExecGetOutput(cmdTOKEN,True)
	#print(TOKEN)
	# Get service account certificate 
	cmdCERT = "kubectl get secret " + SECRETNAME[1:len(SECRETNAME)-1] + " -n " + NAMESPACENAME +" -o \"jsonpath={.data['ca\\.crt']}\""
	CERTIFICATE = ExecGetOutput(cmdCERT,True)
	#print(CERTIFICATE)
	# Get IP address, NAME of the cluster, THIS MIGHT BE A PROBLEM IF THERE ARE MORE THAN ONE CLUSTER SO MAYBE THIS SHOULD BE SUPPLIED INSTEAD.
	KUBERNETES_API_ENDPOINT = ExecGetOutput(["kubectl","config","view","--minify","-o","jsonpath='{.clusters[0].cluster.server}'"])
	#print(KUBERNETES_API_ENDPOINT)
	CLUSTER_NAME = ExecGetOutput(["kubectl","config","view","--minify","-o","jsonpath='{.clusters[0].name}'"])
	#print(CLUSTER_NAME)

	# Insert provided value in kubeconfigform
	configfilename = NAMESPACE_USERNAME + "config"
	ExecGetOutput(["cp","./forms/kubeconfigform",configfilename])
	ReplaceWithInput(configfilename,NAMESPACENAME,"NAMESPACE_NAME")
	ReplaceWithInput(configfilename,NAMESPACE_USERNAME,"NAMESPACE_USERNAME")
	ReplaceWithInput(configfilename,TOKEN,"TOKEN")
	ReplaceWithInput(configfilename,CERTIFICATE,"CERTIFICATE")
	ReplaceWithInput(configfilename,KUBERNETES_API_ENDPOINT,"KUBERNETES_API_ENDPOINT")
	ReplaceWithInput(configfilename,CLUSTER_NAME,"CLUSTER_NAME")

	#Success message
	print("SYSTEM MESSAGE:")
	print("Config file for namespace " + NAMESPACENAME + " at cluster " + CLUSTER_NAME + " is created\n")

# This create namespace, service account, role , rolebindings and create a config file based on those infos.
def GenenerateNewConfig(NAMESPACENAME,NAMESPACE_USERNAME,action="create"):
	#NAMESPACENAME = raw_input("Name for namespace:\n")
	#KUBERNETES_API_ENDPOINT = raw_input("Ip address of the preferred cluster, also known as API endpoint(check k8s config file, default path: ~/.kube/config, check for 'cluster' then 'server', example format: https://31.230.155.182):\n")
	#CLUSTER_NAME = raw_input("Name of the preferred cluster(ch 	eck k8s config file, default path: ~/.kube/config, check for 'cluster' then 'name'):\n")
	## Might be edited with ruamel.yam first and merge the file to access.yaml.
	Mergefiles(['./forms/sa.yaml', './forms/role.yaml', './forms/rolebinding.yaml'],"access.yaml")
	## Replace NAMESPACENAME in access.yaml with input provided.
	ReplaceWithInput("access.yaml",NAMESPACENAME,"NAMESPACE_NAME")
	ReplaceWithInput("access.yaml",NAMESPACE_USERNAME,"NAMESPACE_USERNAME")
	## Create namespace and then apply the access.yaml file 
	## to create a service account bound to that namespace
	if(action!="createExisted"):
		print(ExecGetOutput(["kubectl","create","namespace",NAMESPACENAME]))
	print(ExecGetOutput(["kubectl","create","-f","access.yaml"]))
	
	CreateConfig(NAMESPACENAME,NAMESPACE_USERNAME)

	# Cleaning up 
	ExecGetOutput(["rm","-rf","access.yaml"])


def MergeConfigs(files):
	cmd = "export KUBECONFIG=mergedconfig"
	for name in files:
		cmd = cmd + ":" + name
	os.environ["KUBECONFIG"] = cmd
	cmd = "kubectl config view --flatten  > mergedconfig"
	ExecGetOutput(cmd,True)
	os.environ["KUBECONFIG"] = "$HOME/.kube/config"


# IMPORTANT: this function is used for automate the procedure of deleting an user created for an 
# already existed namespace by the method in this script
# What it will remove is serviceaccount,role,rolebindings.
def DeleteCreated(NAMESPACENAME,NAMESPACE_USERNAME):
	ExecGetOutput(["kubectl","delete","sa", NAMESPACE_USERNAME])
	ExecGetOutput(["kubectl","delete","role",NAMESPACE_USERNAME + "-full-access"])
	ExecGetOutput(["kubectl", "delete", "rolebindings", NAMESPACE_USERNAME + "-view"])



if __name__ == '__main__':
	if sys.argv[1]=="merge":
		MergeConfigs(list(sys.argv[2:]))
	elif sys.argv[1]=="create":
		for elem in sys.argv[2:]:
			NAMESPACE_USERNAME = elem + "-user"
			GenenerateNewConfig(elem,NAMESPACE_USERNAME)
	elif sys.argv[1]=="createExisted":
		for elem in sys.argv[3:]:
			GenenerateNewConfig(sys.argv[2],elem,sys.argv[1])
	elif sys.argv[1]=="recreate":
		CreateConfig(sys.argv[2],sys.argv[3])
	elif sys.argv[1]=="deleteCreated":
		DeleteCreated(sys.argv[2],sys.argv[3])



	



