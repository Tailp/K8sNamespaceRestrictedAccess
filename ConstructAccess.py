
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


if __name__ == '__main__':
	NAMESPACENAME = raw_input("Name for namespace:\n")
	KUBERNETES_API_ENDPOINT = raw_input("Ip address of the preferred cluster, also known as API endpoint(check k8s config file, default path: ~/.kube/config, check for 'cluster' then 'server', example format: https://31.230.155.182):\n")
	CLUSTER_NAME = raw_input("Name of the preferred cluster(check k8s config file, default path: ~/.kube/config, check for 'cluster' then 'name'):\n")
	## Edit with ruamel.yam and merge the file to access.yaml.
	Mergefiles(['./forms/sa.yaml', './forms/role.yaml', './forms/rolebinding.yaml'],"access.yaml")
	## Replace NAMESPACENAME in access.yaml with input provided.
	ReplaceWithInput("access.yaml",NAMESPACENAME,"NAMESPACE_NAME")
	## Create namespace and then apply the access.yaml file 
	## to create a service account bound to that namespace
	print(ExecGetOutput(["kubectl","create","namespace",NAMESPACENAME]))
	print(ExecGetOutput(["kubectl","create","-f","access.yaml"]))

	## Collect data
	# Get name of the secret format "mynamespace-user-token-xxxxx" of the created service account
	NAMESPACE_USERNAME = NAMESPACENAME + "-user"
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
	#KUBERNETES_API_ENDPOINT = ExecGetOutput(["kubectl","config","view","--minify","-o","jsonpath='{.clusters[0].cluster.server}'"])
	#print(KUBERNETES_API_ENDPOINT)
	#CLUSTER_NAME = ExecGetOutput(["kubectl","config","view","--minify","-o","jsonpath='{.clusters[0].name}'"])
	#print(CLUSTER_NAME)

	# Insert provided value in kubeconfigform
	ExecGetOutput(["cp","./forms/kubeconfigform","kubeconfig"])
	ReplaceWithInput("kubeconfig",NAMESPACENAME,"NAMESPACE_NAME")
	ReplaceWithInput("kubeconfig",NAMESPACE_USERNAME,"NAMESPACE_USERNAME")
	ReplaceWithInput("kubeconfig",TOKEN,"TOKEN")
	ReplaceWithInput("kubeconfig",CERTIFICATE,"CERTIFICATE")
	ReplaceWithInput("kubeconfig",KUBERNETES_API_ENDPOINT,"KUBERNETES_API_ENDPOINT")
	ReplaceWithInput("kubeconfig",CLUSTER_NAME,"CLUSTER_NAME")

	# Cleaning up 
	ExecGetOutput(["rm","-rf","access.yaml"])



