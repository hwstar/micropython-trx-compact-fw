import os
import errno
import ujson

class ConfigRw:
        
    def write(self, path: str, config: dict):
            init_str = ujson.dumps(config)
            with open(path, "w") as f:
                f.write(init_str)
                
        
    def read(self, path: str, default_init: dict, update: bool = True) -> dict:
        try:
            # File exists test
            res = os.stat(path)

        except OSError as e:
            if e.errno == errno.ENOENT:
                if update:
                    self.write(path, default_init)
                else:
                    return default_init
            else:
                raise

        with open(path, "r") as f:
            # Read in the json string
            config = f.read()
            res = ujson.loads(config)
            if update:
                # Update the default dict with the one read from the file
                udict  = {k:v for d in (default_init, res) for k,v in d.items()}
                # If there were any changes
                if res != udict:
                    # Write back the updated configuration  to flash
                    self.write(path, udict)
                    # Use the updated dict
                    res = udict      
            return res





