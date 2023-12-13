import os
import json
import xml.etree.ElementTree as ET

def create_file_structure_json(folder_path):
    if not os.path.isdir(folder_path):
        print(f"The provided path '{folder_path}' is not a valid directory.")
        return

    folder_structure = {}
    for root, dirs, files in os.walk(folder_path):
        ignor=["target",".git",".idea","logs",".flattened-pom.xml","test","src","ddl"]
        for i in ignor:
            if i in dirs:
                dirs.remove(i)
        current_folder = folder_structure
        path = root.split(os.path.sep)[1:]
        for folder in path:
            if folder.endswith(".java"):
                continue
            if folder.endswith(".txt"):
                continue
            if folder.endswith(".iml"):
                continue
            current_folder = current_folder.setdefault(folder, {})
        current_folder.update({file: os.path.join(root, file) for file in files})

    while(len(folder_structure.keys())==1):
        folder_structure=folder_structure[list(folder_structure.keys())[0]]

    return folder_structure

def create_json_file(folder_path,folder_structure):
    json_file_path = os.path.join(folder_path, "file_structure.json")
    with open(json_file_path, 'w') as json_file:
        json.dump(folder_structure, json_file, indent=2)

    print(f"File structure information has been saved to '{json_file_path}'.")

def find_dependency(be_working):
    tree = ET.parse(be_working)
    root = tree.getroot()
    namespace = {'maven': 'http://maven.apache.org/POM/4.0.0'}

    group_id = root.find('./maven:groupId', namespaces=namespace)
    artifact_id = root.find('./maven:artifactId', namespaces=namespace)

    return {"group_id": group_id.text, "artifact_id": artifact_id.text}

def add_dependency(xml_path, group_id, artifact_id, version):
    tree = ET.parse(xml_path)
    xml_tree = tree.getroot()
    namespace = {'maven': 'http://maven.apache.org/POM/4.0.0'}
    dependencies_element = xml_tree.find('./maven:dependencies',namespaces=namespace)

    arrll=dependencies_element.findall('.//maven:dependency',namespaces=namespace)
    isPresent=True
    for dependency in arrll:
        groupId = dependency.find('.//maven:groupId',namespaces=namespace).text
        artifactId = dependency.find('.//maven:artifactId',namespaces=namespace).text
        if(groupId==group_id and artifact_id==artifactId):
            isPresent=False
        
    if(isPresent):
        new_dependency = ET.Element('dependency')
        group_id_element = ET.Element('groupId')
        group_id_element.text = group_id
        artifact_id_element = ET.Element('artifactId')
        artifact_id_element.text = artifact_id
        version_element = ET.Element('version')
        version_element.text = version

        new_dependency.extend([group_id_element, artifact_id_element, version_element])
        dependencies_element.append(new_dependency)
        tree.write(xml_path)
        with open(xml_path, 'r') as file:
            xml_data = file.read()
        
        xml_data_no_ns0 = xml_data.replace('ns0:', '')
        xml_data_no_ns0 = xml_data_no_ns0.replace(':ns0', '')
        xml_data_with_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_data_no_ns0

        with open(xml_path, 'w') as file:
            file.write(xml_data_with_declaration)

def find_and_add(be_working):
    be_depn=find_dependency(be_working)
    new_group_id=be_depn["group_id"]
    new_artifact_id =be_depn["artifact_id"]
    new_version = '${project.version}'
    add_dependency(fms_pom_path, new_group_id, new_artifact_id, new_version)

def get_all_be_bs(be_working):
    tree = ET.parse(be_working)
    root = tree.getroot()
    namespace = {'maven': 'http://maven.apache.org/POM/4.0.0'}
    arrll=root.findall('.//maven:module',namespaces=namespace)
    nameArr=[]
    for dependency in arrll:
        nameArr.append(dependency.text)

    return nameArr

folder_path = input("Enter the folder path: ")
folder_stec=create_file_structure_json(folder_path)

fms_pom_path=folder_stec["fms"]["pom.xml"]
be_pom_path=folder_stec["be"]["pom.xml"]
bs_pom_path=folder_stec["bs"]["pom.xml"]

be_arr=get_all_be_bs(be_pom_path)
bs_arr=get_all_be_bs(bs_pom_path)

print(be_arr,bs_arr)

working_bebs_path = input("Enter you BE or BS name : ")
working_bebs_path=working_bebs_path.split(",")

for itm in working_bebs_path:
    if(itm.endswith("*")):
        working_bebs_path.remove(itm)
        temp_arr=[]
        for i in be_arr:
            if(i.startswith(itm[:-1]) and i not in temp_arr):
                temp_arr.append(i)

        for i in bs_arr:
            if(i.startswith(itm[:-1]) and i not in temp_arr):
                temp_arr.append(i)

        working_bebs_path=working_bebs_path+temp_arr

temp_fmsPath=fms_pom_path=folder_stec["fms"]["pom.xml"]
fms_asset_path=temp_fmsPath.replace("\\pom.xml", "")

fms_asset_path=fms_asset_path+"\\src\\main\\resources\\AssetDetails.json"

with open(fms_asset_path, 'r') as file:
    fms_asset = json.load(file)

with open(folder_stec["asset-json"]["AssetDetails.json"], 'r') as file:
    asset_path = json.load(file)


def bebs_isPresent(jsonFile,typr,name):
    parsed_array = jsonFile[typr]
    for element in parsed_array:
        if isinstance(element, dict):
            if(typr=="BsDetails"):
                if(element["bsName"]==name):
                    return False
            else:
                if(element["beName"]==name):
                    return False
        else:
            if(name==element):
                return False
    return True

for i in working_bebs_path:
    if(i in be_arr):
        bePath=folder_stec["be"][i]["pom.xml"]
        find_and_add(bePath)
        if(bebs_isPresent(fms_asset,"BeDetails",i)):
            temp_obe={"version": "1.0"}
            temp_obe["beName"]=i
            fms_asset["BeDetails"].append(temp_obe)

        if(bebs_isPresent(asset_path,"BeDetails",i)):
            temp_obe={"version": "1.0"}
            temp_obe["beName"]=i
            asset_path["BeDetails"].append(temp_obe)

    if(i in bs_arr):
        bsPath=folder_stec["bs"][i]["pom.xml"]
        find_and_add(bsPath)
        if(bebs_isPresent(fms_asset,"BsDetails",i)):
            temp_obe={"version": "1.0"}
            temp_obe["bsName"]=i
            fms_asset["BsDetails"].append(temp_obe)

        if(bebs_isPresent(asset_path,"BsDetails",i)):
            temp_obe={"version": "1.0"}
            temp_obe["bsName"]=i
            asset_path["BsDetails"].append(temp_obe)


with open(fms_asset_path, 'w') as file:
    json.dump(fms_asset, file, indent=2)

with open(folder_stec["asset-json"]["AssetDetails.json"], 'w') as file:
    json.dump(asset_path, file, indent=2)

print("Thanks For using this tool :) ")
print("Developed by : Nitish Ranjan Naskar ........")
input("Enter any key ............")