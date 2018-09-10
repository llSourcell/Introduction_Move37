import os
import sys
import json

from view_controller import ViewController

def main():
    if len(sys.argv) < 2:
        print('Must input config file!')
        sys.exit(1)
    if not os.path.exists(sys.argv[1]):
        print('Config file must exist!')
        sys.exit(1)

    with open(sys.argv[1]) as f:
        metadata = json.load(f)

    view_controller = ViewController(metadata=metadata)
    view_controller.run()

if __name__ == '__main__':
    main()
