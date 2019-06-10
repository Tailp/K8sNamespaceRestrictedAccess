
import subprocess
import sys # To do File input output operations
import os # for certain command for saving as file
from collections import OrderedDict # For using Ordered dict
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
	
# Merge yaml file together separating with ---, this is meant for constructing the access-nsname-username-accesskind.yaml by merging
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
# accesskind is either admin, user or viewer (check repo for more detailed what they do)
def GenenerateNewConfig(NAMESPACENAME,NAMESPACE_USERNAME,action,accesskind="",rolefilepath="",resourcelimitfilepath=""):
	# copy from the forms then replace the name of role referred in rolebinding.yaml.
	ExecGetOutput(["cp","./forms/rolebinding.yaml","./"])

	# use ruamel.yaml to take the name field from role.yaml to rolebindings
	if rolefilepath=="":
		rolefilepath = './forms/role-' + accesskind +'.yaml'  ## Read the Yaml File
		accessfilename = "access-" + NAMESPACENAME + "-" + NAMESPACE_USERNAME + "-" + accesskind +".yaml"
	else:
		accessfilename = "access-" + NAMESPACENAME + "-" + NAMESPACE_USERNAME + "-Custom"  +".yaml"
	file1 = open(rolefilepath).read()
	yaml = YAML() ## Load the yaml object

	code1 = yaml.load(file1) #Load content of YAML file to yaml object

	file2 = open("rolebinding.yaml").read()  ## Read the Yaml File

	yaml = YAML() ## Load the yaml object

	code2 = yaml.load(file2) #Load content of YAML file to yaml object

	code2["roleRef"]["name"] = code1["metadata"]["name"]

	writefile = open("rolebinding.yaml", "w")
	yaml.dump(code2,writefile)
	writefile.close()

	# After editing with ruamel.yaml merge everything to a single file and apply.
	Mergefiles(['./forms/sa.yaml', rolefilepath, 'rolebinding.yaml'],accessfilename)

	## Replace NAMESPACENAME in access.yaml with input provided.
	ReplaceWithInput(accessfilename,NAMESPACENAME,"NAMESPACE_NAME")
	ReplaceWithInput(accessfilename,NAMESPACE_USERNAME,"NAMESPACE_USERNAME")


	## Create namespace and then apply the access.yaml file 
	## to create a service account bound to that namespace
	actioncheck = ["createEx","createExCustomRole"]
	if(action not in actioncheck):
		print(ExecGetOutput(["kubectl","create","namespace",NAMESPACENAME]))
	print(ExecGetOutput(["kubectl","create","-f",accessfilename]))

	# We'll now make a directory to contain all access-file for the namespace.
	# If the folder does not already exist then we create one and then move the accessfile inside.
	if(ExecGetOutput('[ -d "/path/to/dir" ] && echo "exist"',True)!="exist"):
		ExecGetOutput("mkdir " + NAMESPACENAME,True)
	ExecGetOutput("mv " + accessfilename + " ./" + NAMESPACENAME,True)

	CreateConfig(NAMESPACENAME,NAMESPACE_USERNAME)
	# Cleaning up 
	ExecGetOutput(["rm","-rf","sa.yaml", "role.yaml", "rolebinding.yaml"])

# Given the config files this will merge everything and output it to "KUBECONFIG"
def MergeConfigs(files):
	cmd = "export KUBECONFIG=mergedconfig"
	for name in files:
		cmd = cmd + ":" + name
	os.environ["KUBECONFIG"] = cmd
	cmd = "kubectl config view --flatten  > mergedconfig"
	ExecGetOutput(cmd,True)
	os.environ["KUBECONFIG"] = "$HOME/.kube/config"

def LimitResources(resourcelimitfilepath,namespacename):
	print(ExecGetOutput("kubectl apply -f " + resourcelimitfilepath + " -n " + namespacename,True))
	ExecGetOutput("cp " + resourcelimitfilepath + " ./" + namespacename,True)


# This is because we want to avoid a list of if , elif and else.
# Syntax "python ConstructAccess.py merge file1 file2 file3"
def Case1():
	MergeConfigs(list(sys.argv[2:]))
# Syntax "python ConstructAccess.py create accesskind namespace1 namespace2 ... namespaceN"
def Case2():
	for elem in sys.argv[3:]:
		NAMESPACE_USERNAME = elem + "-user"
		GenenerateNewConfig(elem,NAMESPACE_USERNAME,sys.argv[1],sys.argv[2])
# Syntax "python ConstructAccess.py createEx namespacename accesskind username1 username2 ... usernameN"
def Case3():
	for elem in sys.argv[4:]:
		GenenerateNewConfig(sys.argv[2],elem,sys.argv[1],sys.argv[3])
# Syntax "python ConstructAccess.py createCustomRole <path to file role.yaml> namespace1 namespace2 .. namespaceN"
def Case4():
	for elem in sys.argv[3:]:
		NAMESPACE_USERNAME = elem + "-user"
		GenenerateNewConfig(elem,NAMESPACE_USERNAME,sys.argv[1],rolefilepath=sys.argv[2])
# Syntax "python ConstructAccess.py createExCustomRole namespacename <path to file role.yaml> username1 username2 ... usernameN"
def Case5():
	for elem in sys.argv[4:]:
		GenenerateNewConfig(sys.argv[2],elem,sys.argv[1],rolefilepath=sys.argv[3])
# Syntax "python ConstructAccess.py recreate NAMSPACE_NAME username1 username2 username3 ... usernameN"
def Case6():
	for elem in sys.argv[3:]:
		CreateConfig(sys.argv[2],elem)
# Syntax "python ConstructAccess.py delete NAMESPACE"
def Case7():
	for elem in sys.argv[4:]:
		DeleteCreated(sys.argv[2],elem,sys.argv[3])
# Syntax "python ConstructAccess.py limitRes ResourceQuotafilepath namespace1 namespace2 namespace3 ... namespaceN"
def Case8():
	print(sys.argv[2])
	for elem in sys.argv[3:]:
		LimitResources(sys.argv[2],elem)


if __name__ == '__main__':
	Cases = {"merge":Case1,"create":Case2,"createEx":Case3,"createCustomRole":Case4,
	"createExCustomRole":Case5,"recreate":Case6,"delete":Case7,"limitRes":Case8}
	Cases[sys.argv[1]]()



	



