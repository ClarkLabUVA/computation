import os
import requests
import json
ORS_URL = os.environ.get("ORS_URL","http://mds.ors/")
JOBID = os.environ.get("JOBID","testestest")

class Output:
    '''
    Output class
        Output only contains 3 things:
            - name which is node_name.output_name
            - file path in contiainer
            - compute id linking to the computation that created it

        Only method mint and upload
    '''
    def __init__(self,name,path,comp_id):

        self.file_path = path
        self.output_name = name
        self.comp_id = comp_id

    def mint_and_upload(self):
        '''
        Mint and upload output
        '''

        meta = {
            'name':self.output_name,
            "@type":"Dataset",
            "eg:generatedBy":{'@id':self.comp_id},
            "folder":JOBID
        }

        if self.file_path == 'Not A File':
            self.id = mint(meta)
            return self.id

        self.id = transfer(meta,self.file_path)

        return self.id

class Node:
    '''
    Node Object
        - node: nipype node object
        - name: name of node with ending to determine with
                multiple options existed
        - input_dict: dict from nipype node object
        - output_files: dict containing output names and file paths
            {
                'outfile':/path/example
            }

    '''
    def __init__(self, node,node_name):

        self.node = node
        self.name = node_name
        self.input_dict = node.result.inputs
        outputs = node.result.outputs
        self.output_files = gather_output_files(outputs)
        self.outputs = []
        #self.input_files, self.node_parameters = parse_inputs(input_dict)
        #self.parameters_id = mint(self.node_parameters)

        self.ids = []
        self.inputs = []

    def collect_outputs(self):
        '''
        Goes through node.result.outputs
        collects all files created by the node
        for each file creates an Output Object
        '''

        for output in self.output_files:
            if isinstance(self.output_files[output],list):
                for sub in self.output_files[output]:
                    out_name = self.name + '.' + output
                    out_path = sub
                    self.outputs.append(Output(out_name,out_path,self.comp_id))
            else:
                out_name = self.name + '.' + output
                out_path = self.output_files[output]
                self.outputs.append(Output(out_name,out_path,self.comp_id))

        return self.outputs



    def gather_input_files(self,adj,OUTPUT_ID):
        '''
        First looks at adjacency matrix finds known inputs (already minted outputs)
        Looks at remaining inputs to see if any are of already minted files
        '''

        matched, node_inputs = inputs_from_adj_matrix(self.node,adj,OUTPUT_ID)
        input_files, node_parameters = parse_inputs(self.input_dict,matched)

        node_inputs.extend(input_files)
        self.inputs = node_inputs
        self.parameters = node_parameters
        return node_inputs

    def mint_software(self):

        self.parameters_id = mint(self.parameters)

        self.meta = {
            "name":self.name,
            "@type":"SoftwareSourceCode",
            "interface":str(self.node.interface),
            "parameters":self.parameters_id
        }

        self.id = mint(self.meta)

        return self.id

    def mint_comp_id(self):

        data_used = []
        for id in self.ids:
            data_used.append({'@id':id})

        computation_meta = {
            "@type":"eg:Computation",
            "name":"Computation " + str(self.name),
            'eg:usedDataset':data_used,
            'eg:usedSoftware':self.id
        }

        self.comp_id = mint(computation_meta)

        return self.comp_id

def mint(meta):
    url = ORS_URL + "shoulder/ark:99999"

    r = requests.post(url, data=json.dumps(meta))
    returned = r.json()

    if 'created' in returned:

        return returned['created']
    else:
        return 'error'

def transfer(metadata,location):
    files = {
        'files':open(location,'rb'),
        'metadata':json.dumps(metadata),
    }
    url = 'http://transfer-service/data/'
    r = requests.post(url,files=files)
    data_id = r.json()['Minted Identifiers'][0]
    return data_id

def inputs_from_adj_matrix(target,adj,OUTPUT_ID):

    #Node names have str() but that drops important info at end
    #Below is ugly but keeps full name
    str_node_names = str(list(adj.keys())).replace('[','').replace(']','').replace(' ','').split(',')
    nodes = list(adj.keys())

    found = []
    inputs = []

    for i in range(len(nodes)):

        node = nodes[i]
        node_name = str_node_names[i]

        if node == target:
            continue

        for sub_node in adj[node]:

            if sub_node == target:
                connections = adj[node][target]['connect']
                for conn in connections:
                    if isinstance(conn[0],tuple):
                        out = node_name + '.' + conn[0][0]
                    else:
                        out = node_name + '.' + conn[0]

                    inp = conn[1]

                    if out in OUTPUT_ID.keys():
                        found.append(inp)
                        inputs.append(out)

    return found,inputs




def gather_output_files(outputs):
    '''
    Returns dict of output name:file path
    {
        'outfile':/path/tofile,
        'other_out':[/list/of,/file/paths]
    }
    '''
    sample = {}

    for output in str(outputs).split('\n'):
        #Go through all outputs
        try:
            name,result = output.split('=')
            name = name.rstrip()
            result = result.lstrip()
            #if file is list parse into elements
            if result[0] == '[' and result[-1] == ']':
                result = result.strip('][').replace("'",'').split(', ')
                #Can be list of ints so only keep track of files
                files = []
                for test in result:
                    if not os.path.isfile(test):
                        continue
                    else:
                        files.append(test)
                result = files
        except:
            continue

        if result == '<undefined>':
            continue
        if result == []:
            result = "Not A File"
        sample[name] = result

    return sample

def update_id_file(id_dict,file_path):
    with open(file_path,'w') as outfile:
        json.dump(id_dict, outfile)
    return

def parse_inputs(input_dict,already_found):
    '''
    Goal is to parse all inputs into a node. Return a dictionary of all inputs
    that are files and dictionary of parameters.
    e.g.
    Returns something like
    files = ['/path/to/file','/more/paths/to/file']
    parameters = {
        'x':15,
        'y':27,
        'OUTPUTFILETYPE':'NIGZ'
    }
    '''

    input_files = []
    parameters = {'@type':"CompuationParameters"}

    for key in input_dict:

        if key in already_found:
            continue

        #Inputs that are dicts parse and add sub keys
        if isinstance(input_dict[key],dict):
            sub_inputs, sub_parameters = parse_inputs(input_dict[key],already_found)
            for sub_input in sub_inputs:
                input_files.append(sub_input)
            for sub_key in sub_parameters:
                parameters[key + '_' + sub_key] = sub_parameters[sub_key]

        elif isinstance(input_dict[key],list):
            i = 0
            for input in input_dict[key]:

                if isinstance(input,dict):
                    sub_inputs, sub_parameters = parse_inputs(input,already_found)
                    for sub_input in sub_inputs:
                        input_files.append(sub_input)
                    for sub_key in sub_parameters:
                        parameters[key + '_' + sub_key+ '_' + str(i)] = sub_parameters[sub_key]

                elif isinstance(input,list):
                    #Don't want to deal with lists of lists yet
                    continue

                elif isinstance(input,str) or isinstance(input,float) or isinstance(input,int):
                    if isinstance(input,str):
                        if os.path.isfile(input):
                            input_files.append(input)
                    else:
                        parameters[key + '_' + str(i)] = input
                i = i + 1

        elif isinstance(input_dict[key],str):
            if os.path.isfile(input_dict[key]):
                input_files.append(input_dict[key])
            else:
                parameters[key] = input_dict[key]

        else:
            parameters[key] = input_dict[key]

    return input_files,parameters
