import os, sys, json,requests,time,re
from termcolor import colored, cprint
from particle import PDGID

if len(sys.argv) == 1:
    sys.exit()
else:

    # Get into the metadata folder and find the new uploaded metadata file
    All_added_files = sys.argv[1]
    File_list = All_added_files.split(',')
    DOI_list = []
    Homepage_list = []
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
        
        # Check whether a new version
        if '.V' in newmetadata:
            assert newfile['Existing Model Doi']
            url = 'https://doi.org/' + file['Existing Model Doi']
            existing_model_webpage = requests.get(url)
            try:
                assert existing_model_webpage.status_code < 400
            except:
                raise Exception(colored('We cannot find your model page with your provided existing model doi.', 'red'))
                
        # Check necessary contents
        # Check necessary contents
        missing_model_information_key = []
        for i in Neccessary_Model_Information_Keys:
            if i not in newfile:
                missing_model_information_key.append(i)

        if len(missing_model_information_key) != 0:
            raise Exception(colored('%s field do not exist in metadata' %missing_model_information_key, 'red'))

        all_contact = []
        for i in newfile['Author']:
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
        missing_necessary_model_related_key = []
        bad_necessary_model_related_key = []
        empty_necessary_model_related_key = []
        for i in Neccessary_Model_Related_Keys:
            if i not in newfile:
                missing_necessary_model_related_key.append(i)

            if i not in missing_necessary_model_related_key:
                if type(newfile[i]) != int:
                    bad_necessary_model_related_key.append(i)
            
            if i not in bad_necessary_model_related_key and i not in missing_necessary_model_related_key:
                if newfile[i] == 0:
                    empty_necessary_model_related_key.append(i)

    
        errors_in_necessary_model_related_key = 0
        if len(missing_necessary_model_related_key) != 0:
            print(colored("%s field not exist in metadata" %missing_necessary_model_related_key, 'red'))
            errors_in_necessary_model_related_key += 1
        if len(bad_necessary_model_related_key) != 0:
            print(colored("%s value should be integer" %bad_necessary_model_related_key, 'red'))
            errors_in_necessary_model_related_key += 1
        if len(empty_necessary_model_related_key) != 0:
            print(colored("%s should not be 0" %empty_necessary_model_related_key, 'red'))
            errors_in_necessary_model_related_key += 1
        
        if errors_in_necessary_model_related_key != 0:
            raise Exception(colored("Some keys in %s are missing, are not integer value, or value equals zero, in your model" %Neccessary_Model_Related_Keys, 'red'))
        
        # Ready for check particles defined in the model
        try: 
            assert newfile['All Particles']
        except:
            raise Exception(colored("'All Particles' key should be in metadata", 'red'))

        try:
            type(newfile['All Particles']) == dict
        except:
            raise Exception(colored("'All Particles' value should be dictionary", 'red'))
        
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

            # Check other particle-related keys                       
            if 'SM particles' in newfile:
                if len(newfile['SM particles'].keys()) != 0:
                    wrong_SM_particle = []
                    for i in newfile['SM particles']:
                        if PDGID(newfile['SM particles'][i]).is_valid == False:
                            wrong_SM_particle.append(i)
                        if PDGID(newfile['SM particles'][i]).is_sm_quark != True and PDGID(newfile['SM particles'][i]).is_sm_lepton != True and PDGID(newfile['SM particles'][i]).is_sm_gauge_boson_or_higgs != True:
                            wrong_SM_particle.append(i)
                    
                    if len(wrong_SM_particle) != 0:
                        raise Exception(colored("Particle %s in your 'SM particles' key is not SM particles" %wrong_SM_particle, 'red'))

            if 'BSM particles with standard PDG codes' in newfile:
                if len(newfile['BSM particles with standard PDG codes'].keys()) != 0:
                    wrong_BSM_particle = []
                    for i in newfile['BSM particles with standard PDG codes']:
                        if PDGID(newfile['BSM particles with standard PDG codes'][i]).is_valid == False:
                            wrong_BSM_particle.append(i)
                        if PDGID(newfile['BSM particles with standard PDG codes'][i]).is_sm_quark == True or PDGID(newfile['BSM particles with standard PDG codes'][i]).is_sm_lepton == True or PDGID(newfile['BSM particles with standard PDG codes'][i]).is_sm_gauge_boson_or_higgs == True:
                            wrong_BSM_particle.append(i)

                    if len(wrong_BSM_particle) != 0:
                        raise Exception(colored("Particle %s in your 'BSM particles with standard PDG codes' key are not BSM particles or are not registered by Particle Data Group" %wrong_BSM_particle, 'red'))

            if 'Particles with PDG-like IDs' in newfile:
                if len(newfile['Particles with PDG-like IDs'].keys()) != 0:
                    wrong_pdglike_particles = []
                    for i in newfile['Particles with PDG-like IDs']:
                        if PDGID(newfile['Particles with PDG-like IDs'][i]['id']).is_valid == True:
                            if newfile['Particles with PDG-like IDs'][i]['spin'] == PDGID(newfile['Particles with PDG-like IDs'][i]['id']).j_spin:
                                if int(round(newfile['Particles with PDG-like IDs'][i]['charge']*3)) == PDGID(newfile['Particles with PDG-like IDs'][i]['id']).three_charge:
                                    wrong_pdglike_particles.append(i)
                    
                    if len (wrong_pdglike_particles) != 0:
                        raise Exception(colored("Particle %s in your 'Particles with PDG-like IDs' key are registered by Particle Data Group" %wrong_pdglike_particles, 'red'))
        
        print('Check model-related information initial metadata:' + colored(' PASSED!', 'green'))
        DOI_list.append(newfile['Model Doi'])
        Homepage_list.append(newfile['Model Homepage'])

    # Check if all DOIs unique
    assert len(DOI_list) == len(set(DOI_list))

    # Check if Doi exists
    # Wait for 5 minutes for DOI page
    time.sleep(300)
    for i in DOI_list:
        url = 'https://doi.org/' + i
        zenodo_webpage = requests.get(url)
        assert zenodo_webpage.status_code < 400
    
    # Check if Model Homepage exists
    for i in Homepage_list:
        homepage_webpage = requests.get(i)
        assert homepage_webpage.status_code < 400

    print('Check DOI information of the model:' + colored(' PASSED!', 'green'))
    print('You have successfully upload metadata for your model!')
        
