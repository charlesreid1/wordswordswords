import json
from queneau import DialogueAssembler

"""
To use olipy:

Step 1:
    git clone http://github.com/leonardr/olipy /path/to/olipy

Step 2:
    add /path/to/olipy to $PYTHONPATH
    add to your .profile:
    export PYTHONPATH="/path/to/olipy:$PYTHONPATH"

Step 3:
    good to go!
"""

d = DialogueAssembler.loadlines(open("data/apollo_12.txt"))
last_speaker = None
for i in range(1, 100):
    speaker, tokens = d.assemble(last_speaker)
    last_speaker = speaker
    print "%s: %s" % (speaker, " ".join(x for x, y in tokens))
    print

