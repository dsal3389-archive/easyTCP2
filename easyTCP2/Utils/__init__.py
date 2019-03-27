

logger_format = "[%(asctime)s] %(levelname)s\teasyTCP2 | %(name)s -> %(message)s"

def load_external_module(module_name) -> None:
    """
    [:Util:]
        importing all of the given names/paths 
        to keep your code clean in case you have a lot of files

    [:params:]
        module_name - file name or ("path.to.the.file")
    """
    import_parts = module_name.split('.')
    if len(import_parts) > 1:
        globals()[import_parts[-1]] = __import__("{}".format('.'.join(import_parts[0:-1])), fromlist=[import_parts[-1]])
    globals()[import_parts[-1]] = __import__(import_parts[0])

async def string_to_dict(string):
    """
    [:Util:]
        convert a string to dict that you are able to send
    
    [:example:]
        await string_to_dict("hello -m world --to everyone here -r")
        
        #returns
        {
            "method": "hello", 
            "m": "world", 
            "to": "everyone here", 
            "r": ""
        }
    """
    ls = string.split('-')
    d = {'method': ls[0].strip()}

    for i in ls[1:]:
        words = i.split()
        if len(words):
            d[words[0].strip('--')] = i[len(words[0]):].strip()
    return d

