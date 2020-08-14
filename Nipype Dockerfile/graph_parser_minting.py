#© 2020 By The Rector And Visitors Of The University Of Virginia

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from new_classes import *
import networkx as nx
import os

with open('/meta/inputs.json') as json_file:
    LOCATION_ID = json.load(json_file)
OUTPUT_ID = {}

def parse(wf):

    #Since nipype node inputs file locations aren't consistient
    #need two dicts one with output of nodes and associated ids
    #second tying file paths to ids


    adj = wf.__dict__['_adj']
    nodes = list(nx.topological_sort(wf))
    str_node_names = str(nodes).replace('[','').replace(']','').replace(' ','').split(',')
    index = 0

    for node in nodes:

        node_name = str_node_names[index]

        #New init won't get inputs
        #Will just create neccesary variables (name,node,ids,inputs)
        c_node = Node(node,node_name)

        #This method will create list of files and outputs from other
        #nodes
        c_node.gather_input_files(adj,OUTPUT_ID)

        for input in c_node.inputs:
            if input in OUTPUT_ID.keys():
                #Outputs from nodes can be lists of files
                if isinstance(OUTPUT_ID[input],list):
                    c_node.ids.extend(OUTPUT_ID[input])
                else:
                    c_node.ids.append(OUTPUT_ID[input])
            elif input in LOCATION_ID.keys():
                c_node.ids.append(LOCATION_ID[input])
            else:
                print('\nNo associated ID for input: ' + input + '\n\n')

        #will create id for node
        node_id = c_node.mint_software()
        #Will create c_node.comp_id
        comp_id = c_node.mint_comp_id()
        #Will create list of Output Objects
        #Output Object will need:
        #   - file_path
        #   - output_name (should be nodename_outputname)
        #   - comp_id
        node_outputs = c_node.collect_outputs()

        for output in node_outputs:

            #Should only happen for input data
            if output.file_path in LOCATION_ID.keys():
                OUTPUT_ID[output.output_name] = LOCATION_ID[output.file_path]
                continue

            out_id = output.mint_and_upload()

            if output.file_path != 'Not A File':
                LOCATION_ID[output.file_path] = out_id
            if output.output_name in OUTPUT_ID.keys():
                if isinstance(OUTPUT_ID[output.output_name],str):
                    OUTPUT_ID[output.output_name] = [OUTPUT_ID[output.output_name],out_id]
                else:
                    OUTPUT_ID[output.output_name].append(out_id)
            else:
                OUTPUT_ID[output.output_name] = out_id

            update_id_file(LOCATION_ID,'/meta/inputs.json')
            update_id_file(OUTPUT_ID,'/meta/output_ids.json')

        index = index + 1

    return OUTPUT_ID
