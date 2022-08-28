
import os, sys, json,requests,time,re
from termcolor import colored, cprint

if len(sys.argv) == 1:
    sys.exit()
else:

    # Get into the metadata folder and find the new uploaded metadata file
    All_added_files = sys.argv[1]
    File_list = All_added_files.split(',')
    DOI_list = []
    os.chdir('/home/runner/work/UFOMetadata/UFOMetadata/Metadata')

    regex = r'[^@]+@[^@]+\.[^@]+'

    for file in File_list:
        newmetadata = file.split('/')[-1]
        filelist = os.listdir()

        # List of keys in metadata file
        Neccessary_Model_Information_Keys = ['Author','Paper_id','Description','Model name','Model Doi']
        Neccessary_Model_Related_Keys = ['Number of parameters','Number of vertices','Number of coupling orders','Number of coupling tensors','Number of lorentz tensors']
        Model_Related_Keys = ['Number of parameters','Number of vertices','Number of coupling orders','Number of coupling tensors','Number of lorentz tensors','Number of propagators','Number of decays']

        # Read .json as dictionary in python
        with open(newmetadata,encoding='utf-8') as metadata:
            newfile = json.load(metadata)
        
        # Check necessary contents
        for i in Neccessary_Model_Information_Keys:
            assert newfile[i]

        try:
            assert file['Author']
        except:
            raise Exception(colored('"Author" field does not exist in metadata', 'red'))
        all_contact = []
        for i in file['Author']:
            try:
                assert i['name'].strip()
            except:
                raise Exception(colored('At least one author name does not exist in metadata', 'red'))
            if 'contact' in i:
                assert re.match(regex, i['contact'].strip()), \
                    Exception(colored('At least one author contact is not a valid email address', 'red'))
                all_contact.append(i['contact'])
        assert all_contact != [], colored('No contact information for authors exists ', 'red')
        print('Check author information and contact information in initial metadata:' + colored(' PASSED!', 'green'))

        # Check model related contents
        for i in Neccessary_Model_Related_Keys:
            assert newfile[i] and type(newfile[i]) == int and newfile[i] != 0
        
        # Ready for check particles defined in the model
        assert newfile['All Particles'] and type(newfile['All Particles']) == dict
        new_pdg_code = [newfile['All Particles'][i] for i in newfile['All Particles']]

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
                with open(jsonfile,encoding='utf-8') as metadata:
                    existingfile = json.load(metadata)

                # Ready for check particles defined in the model
                existing_pdg_code = [existingfile['All Particles'][i] for i in existingfile['All Particles']]

                # Ready to check other model related content   
                existing_keys = [i for i in Model_Related_Keys if i in existingfile]

                # Check whether the new model has been registered 
                if newfile['Model Doi'] == existingfile['Model Doi']:
                    raise Exception('The DOI of model ' + colored(newmetadata, 'red') + ' in this metadata has been registered by ' + colored(jsonfile, 'red') + '.')
                
                # Check whether the new model is the same to some existing model
                if set(new_pdg_code) == set(existing_pdg_code):
                    if set(new_keys) == set(existing_keys):
                        existing_dic = {}
                        for i in existing_keys:
                            existing_dic[i] = existingfile[i]
                        if new_dic == existing_dic:
                            if newfile['Model Version'] == existingfile['Model Version']:
                                try:
                                    assert newfile['Paper_id']['doi'] and existingfile['Paper_id']['doi']
                                    if newfile['Paper_id']['doi'] == existingfile['Paper_id']['doi']:
                                        raise Exception('Your new uploaded metadata ' + colored(newmetadata, 'red') + ' may be the same with ' + colored(jsonfile, 'red') + '. ' + 'You can contact with ' + colored('thanoswang@163.com' ,'blue') + ' If your model has no problems.')
                                except:
                                    pass
                                
                                try:
                                    assert newfile['Paper_id']['arXiv'] and existingfile['Paper_id']['arXiv']
                                    if newfile['Paper_id']['arXiv'] and existingfile['Paper_id']['arXiv']:
                                        raise Exception('Your new uploaded metadata ' + colored(newmetadata, 'red') + ' may be the same with ' + colored(jsonfile, 'red') + '. ' + 'You can contact with ' + colored('thanoswang@163.com' ,'blue') + ' If your model has no problems.')
                                except:
                                    pass
                                

        DOI_list.append(newfile['Model Doi'])

    # Check if all DOIs unique
    assert len(DOI_list) == len(set(DOI_list))

    # Check if Doi exists
    # Wait for 5 minutes for DOI page
    time.sleep(300)
    for i in DOI_list:
        url = 'https://doi.org/' + i
        zenodo_webpage = requests.get(url)
        assert zenodo_webpage.status_code < 400

    print('You have successfully upload metadata for your model!')
        
