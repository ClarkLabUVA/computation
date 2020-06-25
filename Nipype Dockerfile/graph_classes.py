import os
import requests
import json
ORS_URL = os.environ.get("ORS_URL","http://mds.ors/")
JOBID = os.environ.get("JOBID","testestest")
class Output:

    def __init__(self, name, location,node):

        self.name = name
        self.node = node
        self.inputs = node.ids
        self.location = location
        self.id = None


    def mint_and_upload(self):

        computation_meta = {
            'eg:usedDataset':[],
            'eg:usedSoftware':self.node.id
        }
        for input in self.inputs:
            computation_meta['eg:usedDataset'].append({'@id':input})
        comp_id = mint(computation_meta)

        meta = {
            'name':self.name,
            "eg:generatedBy":{'@id':comp_id},
            "folder":JOBID
        }

        self.id = transfer(meta,self.location)

        return self.id

class Node:

    def __init__(self, node):

        self.node = node

        input_dict = node.result.inputs
        outputs = node.result.outputs

        self.input_files, self.node_parameters = parse_inputs(input_dict)
        self.parameters_id = mint(self.node_parameters)
        self.output_files = gather_output_files(outputs)
        self.ids = []

        self.meta = {
            "name":node.name,
            "interface":str(node.interface),
            "parameters":self.parameters_id
        }
        self.id = mint(self.meta)

def transfer(metadata,location):
    files = {
        'files':open(location,'rb'),
        'metadata':json.dumps(metadata),
    }
    url = 'http://transfer-service/data/'
    r = requests.post(url,files=files)
    data_id = r.json()['Minted Identifiers'][0]
    return data_id

def mint(meta):
    url = ORS_URL + "shoulder/ark:99999"

    r = requests.post(url, data=json.dumps(meta))
    returned = r.json()

    if 'created' in returned:

        return returned['created']
    else:
        return 'error'


def gather_output_files(outputs):
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

        sample[name] = result

    return sample

def parse_inputs(input_dict):

    input_files = {}
    parameters = {'@type':"CompuationParameters"}

    for key in input_dict:
        #Inputs that are dicts parse and add sub keys
        if isinstance(input_dict[key],dict):
            sub_inputs, sub_parameters = parse_inputs(input_dict[key])
            for sub_key in sub_inputs:
                input_files[key + '_' + sub_key] = sub_inputs[sub_key]
            for sub_key in sub_parameters:
                parameters[key + '_' + sub_key] = sub_parameters[sub_key]

        elif isinstance(input_dict[key],list):
            i = 0
            for input in input_dict[key]:

                if isinstance(input,dict):
                    sub_inputs, sub_parameters = parse_inputs(input)
                    for sub_key in sub_inputs:
                        input_files[key + '_' + sub_key + '_' + str(i)] = sub_inputs[sub_key]
                    for sub_key in sub_parameters:
                        parameters[key + '_' + sub_key+ '_' + str(i)] = sub_parameters[sub_key]

                elif isinstance(input,list):
                    #Don't want to deal with lists of lists yet
                    continue

                elif isinstance(input,str) or isinstance(input,float) or isinstance(input,int):
                    if isinstance(input,str):
                        if os.path.isfile(input):
                            input_files[key + '_' + str(i)] = input
                    else:
                        parameters[key + '_' + str(i)] = input
                i = i + 1

        elif isinstance(input_dict[key],str):
            if os.path.isfile(input_dict[key]):
                input_files[key] = input_dict[key]
            else:
                parameters[key] = input_dict[key]

        else:
            parameters[key] = input_dict[key]

    return input_files,parameters
