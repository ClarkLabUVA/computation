from graph_classes import *
import networkx as nx
import os
ORS_URL = os.environ.get("ORS_URL","http://mds.ors/")
def parse(wf):

    with open('/meta/inputs.json') as json_file:
        id_dict = json.load(json_file)

    nodes =list(nx.topological_sort(wf))
    for node in nodes:

        #converts Nipype node into simpler interpretation simply to parse
        #inputs and outputs
        current_node = Node(node)


        for input_name,input in current_node.input_files.items():
            try:
                current_node.ids.append(id_dict[input])
            except:
                print('\n\n\n\n\n' + input + " unrecongized\n\n\n\n" )
                continue

        node_outputs = []
        for output in current_node.output_files:

            if isinstance(current_node.output_files[output],str):
                #print(current_node.output_files[output])
                file_path = current_node.output_files[output]
                if file_path in id_dict.keys():
                    continue
                file_name = file_path.split('/')[-1]
                node_outputs.append(Output(file_name,file_path,current_node))

            else:

                for file_path in current_node.output_files[output]:
                    #print(file_path)
                    if file_path in id_dict.keys():
                        continue
                    file_name = file_path.split('/')[-1]
                    node_outputs.append(Output(file_name,file_path,current_node))


        for output in node_outputs:
            id_dict[output.location] = output.mint_and_upload()

    with open('/meta/inputs.json', 'w') as outfile:
        json.dump(id_dict, outfile)

    return id_dict
