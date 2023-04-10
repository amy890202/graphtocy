import argparse
import datetime
import json
eid_dict = {"FileWrite":1,"Launch":1,"DnsQuery":1,"Terminate":1,"RegistryModify":1}
def readfile(path):
    with open(path,'r',encoding='utf-8-sig') as f:
        input_json = json.load(f)
    return input_json
# def find_ancestor_node(edges):
#     # Create a dictionary to keep track of incoming edges for each node
#     incoming_edges = {}
#     # Iterate through the list of edges to populate the incoming edges dictionary
#     for edge in edges:
#         initiator_id = edge["initiator_id"]#start
#         receiver_id = edge["receiver_id"]#end
#         if receiver_id not in incoming_edges:
#             incoming_edges[receiver_id] = []
#         incoming_edges[receiver_id].append(initiator_id)
    
#     # Find the root node, which is a node that does not have any incoming edges
#     root_node = None
#     for edge in edges:
#         initiator_id = edge["initiator_id"]
#         if initiator_id not in incoming_edges:
#             root_node = initiator_id
#             break
#     return root_node
def find_ancestor_node(edges):
    incoming_edges = {}
    for edge in edges:
        receiver_id = edge["receiver_id"]
        initiator_id = edge["initiator_id"]
        if receiver_id not in incoming_edges:
            incoming_edges[receiver_id] = set()
        incoming_edges[receiver_id].add(initiator_id)

    #ancestor = None
    ancestor_list = []
    for edge in edges:
        initiator_id = edge["initiator_id"]
        if initiator_id not in incoming_edges or \
                (len(incoming_edges[initiator_id]) == 1 and initiator_id in incoming_edges[initiator_id]):
            #ancestor = initiator_id
            ancestor_list.append(initiator_id)
            #print("Ancestor Node: ", ancestor)
        # elif (len(incoming_edges[initiator_id]) == 1 and initiator_id in incoming_edges[initiator_id]):
        #     ancestor = initiator_id
        #     print("Ancestor: ", ancestor)
            #break
    #print("Ancestor Node: ", ancestor)
    return ancestor_list




def parse(input_json):
    notedata_id={}
    # Extract the 'nodes' dictionary from the input JSON
    nodes = input_json.get('nodes', {})

    # Create a dictionary to store the processed nodes
    processed_nodes = {}
    nodeno = 4000
    edgeno = 0
    notedata_id={}
    # Loop through each node in the 'nodes' dictionary
    for node_id, node_data in nodes.items():
        if not isinstance(node_data, dict):
            continue  # Skip non-dictionary objects

        properties = node_data.get('data', {}).get('properties', {})
        node_type = node_data.get('__name__', '')
        node_class = node_data.get('_node_class', '')
        display = node_data.get('process_image', '')
        color = node_data.get('__color__', '')

        # Extract the relevant properties from the 'properties' dictionary
        #process_guid = node_data.get('process_guid', '')
        #integrity_level = node_data.get('integrity_level', '')
        node_id = node_data.get('node_id', '')
        notedata_id[node_id] = nodeno
        #host = node_data.get('host', '')
        #process_id = node_data.get('process_id', '')
        #user = properties.get('user', '')
        #process_image = node_data.get('process_image', '')
        #process_image_path = node_data.get('process_image_path', '')
        #command_line =  node_data.get('command_line', '')
        #hashes = properties.get('hashes', {})
        #process_path =  node_data.get('process_path', '')
        node_data_dict = {}
        for i in node_data:
            if i == "__name__" or i == "__color__":
                continue
            node_data_dict[i] = node_data.get(i, '')
        node_data_dict['id'] = str(nodeno)
        #print(node_data_dict)
        # Create a new dictionary for the processed node
        processed_node = {
            'data': {
                # 'properties': {
                #     'process_id': process_id,
                #     'process_guid': process_guid,
                #     'process_image': process_image,
                #     'process_image_path': process_image_path,
                #     'command_line': command_line,
                #     'integrity_level': integrity_level,
                #     'node_id': node_id,
                #     'id': str(nodeno)
                # },
                'properties': node_data_dict,
                '_node_type': node_type,
                '_node_class': node_class,
                '_display': display,
                '_color': color,
                'id': node_id
            }
        }
        nodeno = nodeno + 1

        # Add the processed node to the dictionary using the 'id' as the key
        processed_nodes[node_id] = processed_node



            # Transform JSON
    #print(notedata_id)
    output_edge = []
    for edge in input_json["edges"]:
        eid = ""
        try:
            eid = str(eid_dict[edge["__name__"]])
        except:
            print("no match eid")
            eid = ""

        transformed_edge = {
            "data": {
                "id": str(edgeno),
                "type": edge["__name__"],
                "properties": {
                    "data": {
                        "timestamp": int(datetime.datetime.fromisoformat(edge["timestamp"][:-1]).timestamp())


                    },
                    "prov_direction":edge["prov_direction"],
                    "prop_direction":edge["prop_direction"],
                    "data_direction":edge["data_direction"]
                },
                "sid": notedata_id[edge["initiator_id"]],
                "tid": notedata_id[edge["receiver_id"]],
                "label": 0,
                "source": edge["initiator_id"],
                "target": edge["receiver_id"],
                "_display": edge["__name__"],
                "eid": eid
            }
        }
        output_edge.append(transformed_edge)
        edgeno = edgeno + 1


    # Create the output JSON in the desired format
    output_json = {
        'directed': True,
        'multigraph': True,
        'pid_hash_dict': {},
        'nodes': list(processed_nodes.values()),
        'edges': output_edge,
        "ancestors": find_ancestor_node(input_json["edges"])#[find_ancestor_node(input_json["edges"])]
    }

    # Save the output JSON to a file
    with open('output.sub.cy', 'w') as f:
        json.dump(output_json, f, indent=4)


parser = argparse.ArgumentParser(description='ArgparseTry')
parser.add_argument('--path',required=True,type=str)
args = parser.parse_args()
input_json = readfile(path=args.path)
parse(input_json)
