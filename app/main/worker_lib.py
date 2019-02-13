def get_file(filename):
    print('here')
    try:
        contents = ''
        with open(filename, 'r') as f:
            contents = f.read()
        return {
            'status': 'successfully opened file',
            'contents': contents
        }
    except:
        return "unable to open file"
