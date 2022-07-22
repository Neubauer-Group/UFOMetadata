
import os, sys, json,requests

if len(sys.argv) == 1:
    sys.exit()
else:

    # Get into the metadata folder and find the new uploaded metadata file
    fullpath = sys.argv[1]
    newmetadata = fullpath.split('/')[-1]
    path = os.path.dirname(os.path.realpath(fullpath))
    os.chdir(path)
    filelist = os.listdir()

    # List of keys in metadata file
    Neccessary_Model_Information_Keys = ['Author','Paper_id','Description','Model name','Model Doi']
    Neccessary_Model_related_Keys = ['Number of parameters','Number of vertices','Number of coupling orders','Number of coupling tensors','Number of lorentz tensors']
    Model_Related_Keys = ['Number of parameters','Number of vertices','Number of coupling orders','Number of coupling tensors','Number of lorentz tensors','Number of Propagators','Number of Decays']

    # Read .json as dictionary in python
    with open(newmetadata) as metadata:
        newfile = json.load(metadata)
    
    # Check necessary contents
    for i in Neccessary_Model_Information_Keys:
        assert newfile[i]
    
    # Check if Doi exists
    url = 'https://doi.org/' + newfile['Model Doi']
    zenodo_webpage = requests.get(url)
    assert zenodo_webpage.status_code < 400

    # Check model related contents
    for i in Neccessary_Model_related_Keys:
        assert newfile[i] and type(newfile[i]) == int
    
    # Ready for check particles defined in the model
    new_pdg_code = [newfile['All Particles'][i] for i in newfile['All Particles']]
    assert newfile['All Particles'] and type(newfile['All Particles']) == dict

    # Ready to check other model related content
    new_keys = [i for i in Model_Related_Keys if i in newfile]

    new_dic ={}
    for i in new_keys:
        new_dic[i] = newfile[i]

    # List of existing metadata file
    existingfilelist = [i for i in filelist if i != newmetadata]

    if existingfilelist != []:
        # Open .json as dictionary in python
        for jsonfile in existingfilelist:
            with open(jsonfile) as metadata:
                existingfile = json.load(metadata)

            # Ready for check particles defined in the model
            existing_pdg_code = [existingfile['All Particles'][i] for i in existingfile['All Particles']]

            # Ready to check other model related content   
            existing_keys = [i for i in Model_Related_Keys if i in existingfile]

            # Check whether the new model has been registered 
            if newfile['Model Doi'] == existingfile['Model Doi']:
                raise Exception('The DOI of model in this metadata has been registered by %s.' %(jsonfile))
            
            # Check whether the new model is the same to some existing model
            if set(new_pdg_code) == set(existing_pdg_code):
                if set(new_keys) == set(existing_keys):
                    existing_dic = {}
                    for i in existing_keys:
                        existing_dic[i] = existingfile[i]
                    if new_dic == existing_dic:
                        raise Exception('Your new uploaded metadata may be the same as %s.' %(jsonfile))

    print('You have successfully upload metadata for your model!')
        
