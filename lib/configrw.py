import os
import errno
import ujson

class ConfigRw:
        
    def write(self, path: str, config: dict):
        # Write a a configuration dictionary to a file. 
        init_str = ujson.dumps(config)
        with open(path, "w") as f:
            f.write(init_str)
                
        
    def read(self, path: str, default_init: dict, init: bool = True, merge: bool = False) -> dict:
        # Read a .json file into a config dictionary.
        # If set, the init flag enables an initial file to be created from the default init dict passed in.
        # For single level flat dictionaries the merge flag can be set, and the json file on the disk
        # will be updated with any new fields and defaults.
        # The merge flag with not work with multilevel dictionaries.
        try:
            # File exists test
            res = os.stat(path)

        except OSError as e:
            if e.errno == errno.ENOENT:
                if init:
                    self.write(path, default_init)
                else:
                    return default_init
            else:
                raise

        with open(path, "r") as f:
            # Read in the json string
            config = f.read()
            res = ujson.loads(config)
            if merge:
                # Update the default dict with the one read from the file
                udict  = {k:v for d in (default_init, res) for k,v in d.items()}
                # If there were any changes
                if res != udict:
                    # Write back the updated configuration  to flash
                    self.write(path, udict)
                    # Use the updated dict
                    res = udict      
            return res





